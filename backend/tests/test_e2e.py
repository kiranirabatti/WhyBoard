"""End-to-end integration tests — full pipeline from file upload to narrative output."""

import json
import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app

SAMPLE_DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "sample-data"

MOCK_AI_RESPONSE = {
    "executive_narrative": "Revenue growth is concentrated in a single region, masking underlying weakness in the South. The apparent 15% topline growth is a geographic illusion — strip out North and the business is flat.",
    "analyst_narrative": "North region contributed 68% of total revenue ($3.2M), growing 18% QoQ. South declined 12% across all product lines (Electronics: -$29K, Software: -$18K, Services: -$9K). Services showed strongest growth rate at 32% but from a small base ($908K total).",
    "key_signals": [
        {"label": "Revenue Concentration", "value": "68% North", "direction": "up"},
        {"label": "South Decline", "value": "-12% QoQ", "direction": "down"},
        {"label": "Services Growth", "value": "+32%", "direction": "up"},
    ],
    "risk_flag": "South region declining 3 consecutive months — losing $56K/month in run-rate revenue without intervention.",
    "opportunity_flag": "Services line at 32% growth with highest margins — shift sales capacity from saturated North Electronics to Services expansion.",
    "data_type": "sales",
}


def _make_mock_client():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(MOCK_AI_RESPONSE))]
    mock_message.usage = MagicMock(input_tokens=800, output_tokens=400)
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    return mock_client


# ── E2E: CSV Upload Flow ──────────────────────────────────


@pytest.mark.asyncio
async def test_e2e_csv_upload_sales():
    """Full flow: upload sales CSV → parse → summarize → AI → structured response."""
    csv_path = SAMPLE_DATA_DIR / "sales-q1.csv"
    if not csv_path.exists():
        pytest.skip("Sample data not found")

    csv_bytes = csv_path.read_bytes()

    with patch("backend.main.analyze_data", new_callable=AsyncMock) as mock_ai:
        from backend.schema import AnalyzeResponse, KeySignal, WhyBoardAnalysis

        mock_ai.return_value = AnalyzeResponse(
            success=True,
            analysis=WhyBoardAnalysis(
                executive_narrative=MOCK_AI_RESPONSE["executive_narrative"],
                analyst_narrative=MOCK_AI_RESPONSE["analyst_narrative"],
                key_signals=(
                    KeySignal(**MOCK_AI_RESPONSE["key_signals"][0]),
                    KeySignal(**MOCK_AI_RESPONSE["key_signals"][1]),
                    KeySignal(**MOCK_AI_RESPONSE["key_signals"][2]),
                ),
                risk_flag=MOCK_AI_RESPONSE["risk_flag"],
                opportunity_flag=MOCK_AI_RESPONSE["opportunity_flag"],
                data_type="sales",
                row_count=36,
                column_count=6,
                analyzed_at="2026-03-29T10:00:00+00:00",
            ),
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/analyze/csv",
                files={"file": ("sales-q1.csv", csv_bytes, "text/csv")},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    analysis = data["analysis"]
    assert "Revenue" in analysis["executive_narrative"] or "growth" in analysis["executive_narrative"].lower()
    assert len(analysis["key_signals"]) == 3
    assert analysis["risk_flag"]  # not empty
    assert analysis["opportunity_flag"]  # not empty
    assert analysis["data_type"] == "sales"
    assert analysis["row_count"] == 36
    assert analysis["column_count"] == 6

    # Verify each signal has required fields
    for signal in analysis["key_signals"]:
        assert "label" in signal
        assert "value" in signal
        assert signal["direction"] in ("up", "down", "flat")


@pytest.mark.asyncio
async def test_e2e_csv_upload_ops():
    """Full flow with ops-metrics.csv."""
    csv_path = SAMPLE_DATA_DIR / "ops-metrics.csv"
    if not csv_path.exists():
        pytest.skip("Sample data not found")

    csv_bytes = csv_path.read_bytes()

    # Test the parsing pipeline without mocking (up to AI call)
    from backend.parser import parse_csv, prepare_data_for_ai

    df = parse_csv(csv_bytes)
    assert len(df) > 0
    assert len(df.columns) >= 5

    cleaned_df, summary = prepare_data_for_ai(df)
    assert "Rows:" in summary
    assert "Column Statistics:" in summary
    assert "Tickets_Opened" in summary or "Tickets" in summary


@pytest.mark.asyncio
async def test_e2e_csv_upload_financial():
    """Full flow with financial-summary.csv."""
    csv_path = SAMPLE_DATA_DIR / "financial-summary.csv"
    if not csv_path.exists():
        pytest.skip("Sample data not found")

    csv_bytes = csv_path.read_bytes()

    from backend.parser import parse_csv, prepare_data_for_ai

    df = parse_csv(csv_bytes)
    assert len(df) > 0

    cleaned_df, summary = prepare_data_for_ai(df)
    assert "Budget" in summary or "Actual" in summary
    assert "Variance" in summary


# ── E2E: Paste Flow ───────────────────────────────────────


@pytest.mark.asyncio
async def test_e2e_paste_flow():
    """Full flow: paste tab-separated data → parse → AI → response."""
    paste_data = (
        "Region\tRevenue\tGrowth_Pct\n"
        "North\t3200000\t18.5\n"
        "South\t1100000\t-12.3\n"
        "East\t890000\t5.1\n"
        "West\t750000\t8.7\n"
    )

    with patch("backend.main.analyze_data", new_callable=AsyncMock) as mock_ai:
        from backend.schema import AnalyzeResponse, KeySignal, WhyBoardAnalysis

        mock_ai.return_value = AnalyzeResponse(
            success=True,
            analysis=WhyBoardAnalysis(
                executive_narrative="North dominates with 54% share.",
                analyst_narrative="North at $3.2M (54% share), South declining at -12.3%.",
                key_signals=(
                    KeySignal(label="North Share", value="54%", direction="up"),
                    KeySignal(label="South Decline", value="-12.3%", direction="down"),
                    KeySignal(label="Total Revenue", value="$5.94M", direction="flat"),
                ),
                risk_flag="South region declining — needs intervention.",
                opportunity_flag="West growing steadily at 8.7%.",
                data_type="sales",
                row_count=4,
                column_count=3,
                analyzed_at="2026-03-29T10:00:00+00:00",
            ),
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/analyze/paste",
                json={"data": paste_data, "context": "Quarterly regional review"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["analysis"]["row_count"] == 4
    assert data["analysis"]["column_count"] == 3

    # Verify context was passed
    mock_ai.assert_called_once()
    assert mock_ai.call_args.kwargs["context"] == "Quarterly regional review"


# ── E2E: Error flows ──────────────────────────────────────


@pytest.mark.asyncio
async def test_e2e_error_empty_csv():
    """Error flow: empty CSV returns clean error, not stack trace."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/csv",
            files={"file": ("empty.csv", b"", "text/csv")},
        )

    assert response.status_code == 400
    error_data = response.json()
    assert "detail" in error_data
    # Error message should be human-readable, not a stack trace
    assert "Traceback" not in error_data["detail"]


@pytest.mark.asyncio
async def test_e2e_error_malformed_paste():
    """Error flow: non-tabular paste returns clean error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/paste",
            json={"data": "just some random text without any structure"},
        )

    assert response.status_code == 400
    error_data = response.json()
    assert "detail" in error_data
    assert "Traceback" not in error_data["detail"]

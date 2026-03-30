"""End-to-end integration tests — full pipeline from file upload to narrative output."""

import pathlib
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch

from backend.main import app
from backend.tests.fixtures import MOCK_RESPONSE, make_mock_analysis
from backend.schema import AnalyzeResponse

SAMPLE_DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "sample-data"


# ── E2E: CSV Upload Flow ──────────────────────────────────


@pytest.mark.asyncio
async def test_e2e_csv_upload_sales():
    """Full flow: upload sales CSV → parse → summarize → AI → structured response."""
    csv_path = SAMPLE_DATA_DIR / "sales-q1.csv"
    if not csv_path.exists():
        pytest.skip("Sample data not found")

    csv_bytes = csv_path.read_bytes()

    with patch("backend.main.analyze_data", new_callable=AsyncMock) as mock_ai:
        mock_ai.return_value = MOCK_RESPONSE

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
    assert len(analysis["key_signals"]) == 3
    assert analysis["risk_flag"]
    assert analysis["opportunity_flag"]
    assert analysis["metadata"]["data_type"] == "sales"
    assert analysis["metadata"]["token_usage"]["total_tokens"] > 0
    assert analysis["metadata"]["token_usage"]["cost_inr"] > 0
    assert analysis["metadata"]["response_time_seconds"] >= 0
    assert analysis["metadata"]["data_quality_score"] >= 0

    for signal in analysis["key_signals"]:
        assert "label" in signal
        assert "value" in signal
        assert signal["direction"] in ("up", "down", "flat")


@pytest.mark.asyncio
async def test_e2e_csv_upload_ops():
    """Full flow with ops-metrics.csv — test parsing pipeline."""
    csv_path = SAMPLE_DATA_DIR / "ops-metrics.csv"
    if not csv_path.exists():
        pytest.skip("Sample data not found")

    csv_bytes = csv_path.read_bytes()

    from backend.parser import parse_csv, prepare_data_for_ai

    df = parse_csv(csv_bytes)
    assert len(df) > 0
    assert len(df.columns) >= 5

    cleaned_df, summary = prepare_data_for_ai(df)
    assert "Rows:" in summary
    assert "Column Statistics:" in summary


@pytest.mark.asyncio
async def test_e2e_csv_upload_financial():
    """Full flow with financial-summary.csv — test parsing pipeline."""
    csv_path = SAMPLE_DATA_DIR / "financial-summary.csv"
    if not csv_path.exists():
        pytest.skip("Sample data not found")

    csv_bytes = csv_path.read_bytes()

    from backend.parser import parse_csv, prepare_data_for_ai

    df = parse_csv(csv_bytes)
    assert len(df) > 0

    cleaned_df, summary = prepare_data_for_ai(df)
    assert "Budget" in summary or "Actual" in summary


# ── E2E: Paste Flow ───────────────────────────────────────


@pytest.mark.asyncio
async def test_e2e_paste_flow():
    """Full flow: paste tab-separated data → parse → AI → response with metadata."""
    paste_data = (
        "Region\tRevenue\tGrowth_Pct\n"
        "North\t3200000\t18.5\n"
        "South\t1100000\t-12.3\n"
        "East\t890000\t5.1\n"
        "West\t750000\t8.7\n"
    )

    mock_analysis = make_mock_analysis(
        metadata={"row_count": 4, "column_count": 3},
    )
    mock_response = AnalyzeResponse(success=True, analysis=mock_analysis)

    with patch("backend.main.analyze_data", new_callable=AsyncMock) as mock_ai:
        mock_ai.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/analyze/paste",
                json={"data": paste_data, "context": "Quarterly regional review"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["analysis"]["metadata"]["row_count"] == 4
    assert data["analysis"]["metadata"]["token_usage"]["cost_inr"] > 0

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

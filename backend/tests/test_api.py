"""Tests for API endpoints — /api/analyze/csv and /api/analyze/paste."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.schema import AnalyzeResponse, KeySignal, WhyBoardAnalysis

MOCK_ANALYSIS = WhyBoardAnalysis(
    executive_narrative="Test narrative for executives.",
    analyst_narrative="Test narrative with 23% growth in Q1 revenue.",
    key_signals=(
        KeySignal(label="Revenue Growth", value="23%", direction="up"),
        KeySignal(label="Cost Ratio", value="45%", direction="flat"),
        KeySignal(label="Margin Trend", value="-3%", direction="down"),
    ),
    risk_flag="Concentration risk in North region.",
    opportunity_flag="Services line growing fast — expand capacity.",
    data_type="sales",
    row_count=36,
    column_count=6,
    analyzed_at="2026-03-29T10:00:00+00:00",
)

MOCK_RESPONSE = AnalyzeResponse(success=True, analysis=MOCK_ANALYSIS)


@pytest.fixture
def transport():
    return ASGITransport(app=app)


# ── Health check ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_check(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── POST /api/analyze/csv ─────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_csv_success(transport):
    csv_content = b"Region,Revenue,Units\nNorth,100000,50\nSouth,80000,40\nEast,60000,30\n"

    with patch("backend.main.analyze_data", new_callable=AsyncMock, return_value=MOCK_RESPONSE):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/analyze/csv",
                files={"file": ("test.csv", csv_content, "text/csv")},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["analysis"]["executive_narrative"] == "Test narrative for executives."


@pytest.mark.asyncio
async def test_analyze_csv_empty_file(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/csv",
            files={"file": ("empty.csv", b"", "text/csv")},
        )

    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_analyze_csv_oversized_file(transport):
    big_content = b"A,B\n" + b"x,1\n" * (6 * 1024 * 1024 // 4)  # >5MB

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/csv",
            files={"file": ("big.csv", big_content, "text/csv")},
        )

    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_analyze_csv_no_file(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/analyze/csv")

    assert response.status_code == 422  # FastAPI validation error


# ── POST /api/analyze/paste ────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_paste_success(transport):
    paste_data = "Region\tRevenue\tUnits\nNorth\t100000\t50\nSouth\t80000\t40\n"

    with patch("backend.main.analyze_data", new_callable=AsyncMock, return_value=MOCK_RESPONSE):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/analyze/paste",
                json={"data": paste_data},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["analysis"]["key_signals"]) == 3


@pytest.mark.asyncio
async def test_analyze_paste_empty_data(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/paste",
            json={"data": ""},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_analyze_paste_with_context(transport):
    paste_data = "Region\tRevenue\nNorth\t100000\nSouth\t80000\n"

    with patch("backend.main.analyze_data", new_callable=AsyncMock, return_value=MOCK_RESPONSE) as mock_ai:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/analyze/paste",
                json={"data": paste_data, "context": "Focus on regional trends"},
            )

    assert response.status_code == 200
    # Verify context was passed through
    mock_ai.assert_called_once()
    assert mock_ai.call_args.kwargs["context"] == "Focus on regional trends"


@pytest.mark.asyncio
async def test_analyze_paste_oversized(transport):
    big_text = "A\tB\n" + "x\t1\n" * 60000  # >50K chars

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze/paste",
            json={"data": big_text},
        )

    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()

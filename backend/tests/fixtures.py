"""Shared test fixtures for mock data."""

from backend.schema import (
    AnalysisMetadata,
    AnalyzeResponse,
    KeySignal,
    TokenUsage,
    WhyBoardAnalysis,
)

MOCK_TOKEN_USAGE = TokenUsage(
    input_tokens=800,
    output_tokens=400,
    total_tokens=1200,
    cost_usd=0.0084,
    cost_inr=0.7014,
)

MOCK_METADATA = AnalysisMetadata(
    data_type="sales",
    row_count=36,
    column_count=6,
    analyzed_at="2026-03-29T10:00:00+00:00",
    response_time_seconds=3.21,
    token_usage=MOCK_TOKEN_USAGE,
    data_quality_score=85,
)

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
    metadata=MOCK_METADATA,
)

MOCK_RESPONSE = AnalyzeResponse(success=True, analysis=MOCK_ANALYSIS)


def make_mock_analysis(**overrides) -> WhyBoardAnalysis:
    """Create a mock WhyBoardAnalysis with optional overrides."""
    meta_overrides = overrides.pop("metadata", {})
    meta = MOCK_METADATA.model_copy(update=meta_overrides)
    defaults = MOCK_ANALYSIS.model_dump()
    defaults["metadata"] = meta
    defaults.update(overrides)
    return WhyBoardAnalysis(**defaults)

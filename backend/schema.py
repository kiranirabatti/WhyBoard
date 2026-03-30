from pydantic import BaseModel
from typing import Literal


class KeySignal(BaseModel):
    label: str
    value: str
    direction: Literal["up", "down", "flat"]


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    cost_inr: float


class AnalysisMetadata(BaseModel):
    data_type: str
    row_count: int
    column_count: int
    analyzed_at: str
    response_time_seconds: float
    token_usage: TokenUsage
    data_quality_score: int  # 0-100: based on completeness, size, variety


class WhyBoardAnalysis(BaseModel):
    executive_narrative: str
    analyst_narrative: str
    key_signals: tuple[KeySignal, KeySignal, KeySignal]
    risk_flag: str
    opportunity_flag: str
    metadata: AnalysisMetadata


class AnalyzeResponse(BaseModel):
    success: bool
    analysis: WhyBoardAnalysis | None = None
    error: str | None = None

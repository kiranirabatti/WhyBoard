from pydantic import BaseModel
from typing import Literal


class KeySignal(BaseModel):
    label: str
    value: str
    direction: Literal["up", "down", "flat"]


class WhyBoardAnalysis(BaseModel):
    executive_narrative: str
    analyst_narrative: str
    key_signals: tuple[KeySignal, KeySignal, KeySignal]
    risk_flag: str
    opportunity_flag: str
    data_type: str
    row_count: int
    column_count: int
    analyzed_at: str


class AnalyzeResponse(BaseModel):
    success: bool
    analysis: WhyBoardAnalysis | None = None
    error: str | None = None

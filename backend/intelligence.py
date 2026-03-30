"""
WhyBoard AI Intelligence Layer — Claude API integration.

Sends summarized data to Claude, receives structured narrative analysis.
Always uses claude-sonnet-4-6. Never hardcodes another model.
"""

import json
import logging
import re
import time
from datetime import datetime, timezone

import anthropic

from backend.config import settings
from backend.schema import (
    AnalysisMetadata,
    AnalyzeResponse,
    KeySignal,
    TokenUsage,
    WhyBoardAnalysis,
)

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

# Claude Sonnet 4 pricing (per token)
PRICE_INPUT_PER_MTOK_USD = 3.00   # $3.00 per million input tokens
PRICE_OUTPUT_PER_MTOK_USD = 15.00  # $15.00 per million output tokens
USD_TO_INR = 83.50  # Approximate exchange rate

SYSTEM_PROMPT = """You are a senior business analyst. Given structured data, output ONLY valid JSON.

Your job: interpret what the data MEANS, not describe what it shows.
Find the signal. Name the risk. Name the opportunity.
Write for two audiences: executive (10 seconds) and analyst (10 minutes).

Output this exact JSON structure — no markdown, no explanation, just JSON:
{
  "executive_narrative": "3 sentences max. Board-deck ready. No jargon. No hedging.",
  "analyst_narrative": "Same insight but with specific data references, column names, percentages, and comparisons.",
  "key_signals": [
    {"label": "signal name", "value": "the number or fact", "direction": "up|down|flat"},
    {"label": "signal name", "value": "the number or fact", "direction": "up|down|flat"},
    {"label": "signal name", "value": "the number or fact", "direction": "up|down|flat"}
  ],
  "risk_flag": "One line — what to watch. Be specific.",
  "opportunity_flag": "One line — what to act on. Be specific.",
  "data_type": "sales|financial|ops|hr|marketing|mixed|unknown"
}

Rules:
- INTERPRET, don't describe. Wrong: "Sales went up 23%". Right: "March's 23% spike is concentrated in one product — demand signal, not broad growth."
- Every field must have a value. Never null. Never empty string.
- key_signals must be EXACTLY 3 items.
- Be direct. No "appears to" or "seems like" or "it is worth noting".
- executive_narrative: a CEO reads this in 10 seconds before a board meeting.
- analyst_narrative: an analyst reads this to decide what to investigate next.
- risk_flag and opportunity_flag: actionable, not generic. Never "monitor closely" — say WHAT to monitor and WHY.
"""


def _build_user_prompt(data_summary: str, context: str | None = None) -> str:
    """Build the user message with data summary and optional context."""
    parts = [f"Analyze this dataset:\n\n{data_summary}"]
    if context:
        parts.append(f"\nAdditional context from the user: {context}")
    return "\n".join(parts)


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences if Claude wraps the JSON response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _parse_ai_response(raw_text: str) -> dict:
    """Parse Claude's response into a dict. Handles markdown fences and edge cases."""
    cleaned = _strip_markdown_fences(raw_text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group())
        raise


def _calculate_cost(input_tokens: int, output_tokens: int) -> TokenUsage:
    """Calculate token usage and cost in USD and INR."""
    cost_usd = (
        (input_tokens / 1_000_000) * PRICE_INPUT_PER_MTOK_USD
        + (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_MTOK_USD
    )
    cost_inr = cost_usd * USD_TO_INR

    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=round(cost_usd, 6),
        cost_inr=round(cost_inr, 4),
    )


def _calculate_data_quality_score(
    row_count: int,
    column_count: int,
    summary: str,
) -> int:
    """Score data quality 0-100 based on size, completeness, and variety.

    Factors:
    - Row count (more rows = better signal, up to a point)
    - Column count (more dimensions = richer analysis)
    - Presence of numeric stats (means data has analyzable numbers)
    - Presence of breakdowns (means categorical variety exists)
    """
    score = 0

    # Row count: 0-30 points
    if row_count >= 100:
        score += 30
    elif row_count >= 20:
        score += 25
    elif row_count >= 10:
        score += 20
    elif row_count >= 5:
        score += 15
    else:
        score += 5

    # Column count: 0-25 points
    if column_count >= 6:
        score += 25
    elif column_count >= 4:
        score += 20
    elif column_count >= 3:
        score += 15
    else:
        score += 10

    # Has numeric statistics: 0-25 points
    if "Column Statistics:" in summary:
        score += 25
    elif "min=" in summary:
        score += 15

    # Has categorical breakdowns: 0-20 points
    if "Breakdowns:" in summary:
        score += 20
    elif "Notable patterns:" in summary and "None detected" not in summary:
        score += 10

    return min(score, 100)


def _validate_and_build_analysis(
    data: dict,
    row_count: int,
    column_count: int,
    response_time: float,
    token_usage: TokenUsage,
    data_quality_score: int,
) -> WhyBoardAnalysis:
    """Validate parsed JSON against schema and inject backend metadata."""
    signals = data.get("key_signals", [])
    if len(signals) != 3:
        raise ValueError(f"Expected 3 key_signals, got {len(signals)}")

    metadata = AnalysisMetadata(
        data_type=data.get("data_type", "unknown"),
        row_count=row_count,
        column_count=column_count,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        response_time_seconds=round(response_time, 2),
        token_usage=token_usage,
        data_quality_score=data_quality_score,
    )

    return WhyBoardAnalysis(
        executive_narrative=data["executive_narrative"],
        analyst_narrative=data["analyst_narrative"],
        key_signals=(
            KeySignal(**signals[0]),
            KeySignal(**signals[1]),
            KeySignal(**signals[2]),
        ),
        risk_flag=data["risk_flag"],
        opportunity_flag=data["opportunity_flag"],
        metadata=metadata,
    )


async def analyze_data(
    data_summary: str,
    row_count: int,
    column_count: int,
    context: str | None = None,
) -> AnalyzeResponse:
    """Send data summary to Claude and return structured analysis.

    This is the main entry point for the AI layer.
    """
    start_time = time.monotonic()

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = await client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": _build_user_prompt(data_summary, context),
                }
            ],
        )

        response_time = time.monotonic() - start_time
        raw_text = message.content[0].text

        token_usage = _calculate_cost(
            message.usage.input_tokens,
            message.usage.output_tokens,
        )

        logger.info(
            "Claude response received in %.2fs — %d tokens ($%.4f / ₹%.4f)",
            response_time,
            token_usage.total_tokens,
            token_usage.cost_usd,
            token_usage.cost_inr,
        )

        data_quality = _calculate_data_quality_score(row_count, column_count, data_summary)
        parsed = _parse_ai_response(raw_text)
        analysis = _validate_and_build_analysis(
            parsed, row_count, column_count,
            response_time, token_usage, data_quality,
        )

        return AnalyzeResponse(success=True, analysis=analysis)

    except json.JSONDecodeError as e:
        logger.error("Failed to parse Claude response as JSON: %s", e)
        return AnalyzeResponse(success=False, error="AI returned invalid response format. Please try again.")

    except (KeyError, ValueError) as e:
        logger.error("Claude response missing required fields: %s", e)
        return AnalyzeResponse(success=False, error="AI response was incomplete. Please try again.")

    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", e)
        return AnalyzeResponse(success=False, error="AI service temporarily unavailable. Please try again.")

    except anthropic.AuthenticationError:
        logger.error("Anthropic API key is invalid")
        return AnalyzeResponse(success=False, error="AI service configuration error. Contact support.")

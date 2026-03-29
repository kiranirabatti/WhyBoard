"""
WhyBoard AI Intelligence Layer — Claude API integration.

Sends summarized data to Claude, receives structured narrative analysis.
Always uses claude-sonnet-4-6. Never hardcodes another model.
"""

import json
import logging
import re
from datetime import datetime, timezone

import anthropic

from backend.config import settings
from backend.schema import AnalyzeResponse, KeySignal, WhyBoardAnalysis

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

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
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _parse_ai_response(raw_text: str) -> dict:
    """Parse Claude's response into a dict. Handles markdown fences and edge cases."""
    cleaned = _strip_markdown_fences(raw_text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from mixed text
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group())
        raise


def _validate_and_build_analysis(
    data: dict,
    row_count: int,
    column_count: int,
) -> WhyBoardAnalysis:
    """Validate parsed JSON against schema and inject backend metadata."""
    # Validate key_signals has exactly 3
    signals = data.get("key_signals", [])
    if len(signals) != 3:
        raise ValueError(f"Expected 3 key_signals, got {len(signals)}")

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
        data_type=data.get("data_type", "unknown"),
        # Backend-injected metadata — not from Claude
        row_count=row_count,
        column_count=column_count,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
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

        raw_text = message.content[0].text
        logger.info(
            "Claude response received",
            extra={"model": MODEL, "tokens_used": message.usage.input_tokens + message.usage.output_tokens},
        )

        parsed = _parse_ai_response(raw_text)
        analysis = _validate_and_build_analysis(parsed, row_count, column_count)

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

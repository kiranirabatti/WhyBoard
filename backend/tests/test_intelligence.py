"""Tests for backend.intelligence — AI response parsing, validation, prompt building."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.intelligence import (
    _build_user_prompt,
    _parse_ai_response,
    _strip_markdown_fences,
    _validate_and_build_analysis,
    analyze_data,
)


# ── Markdown fence stripping ──────────────────────────────


class TestStripMarkdownFences:
    def test_no_fences(self):
        assert _strip_markdown_fences('{"key": "value"}') == '{"key": "value"}'

    def test_json_fences(self):
        text = '```json\n{"key": "value"}\n```'
        assert _strip_markdown_fences(text) == '{"key": "value"}'

    def test_plain_fences(self):
        text = '```\n{"key": "value"}\n```'
        assert _strip_markdown_fences(text) == '{"key": "value"}'

    def test_extra_whitespace(self):
        text = '  ```json\n  {"key": "value"}  \n```  '
        result = _strip_markdown_fences(text)
        assert '"key"' in result


# ── Response parsing ──────────────────────────────────────


class TestParseAiResponse:
    def test_clean_json(self):
        text = '{"executive_narrative": "test"}'
        result = _parse_ai_response(text)
        assert result["executive_narrative"] == "test"

    def test_json_with_fences(self):
        text = '```json\n{"executive_narrative": "test"}\n```'
        result = _parse_ai_response(text)
        assert result["executive_narrative"] == "test"

    def test_json_embedded_in_text(self):
        text = 'Here is the analysis:\n{"executive_narrative": "test"}\nDone.'
        result = _parse_ai_response(text)
        assert result["executive_narrative"] == "test"

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_ai_response("not json at all")


# ── Prompt building ───────────────────────────────────────


class TestBuildUserPrompt:
    def test_without_context(self):
        prompt = _build_user_prompt("summary here")
        assert "summary here" in prompt
        assert "context" not in prompt.lower()

    def test_with_context(self):
        prompt = _build_user_prompt("summary here", "focus on revenue trends")
        assert "summary here" in prompt
        assert "focus on revenue trends" in prompt


# ── Schema validation ─────────────────────────────────────


VALID_AI_RESPONSE = {
    "executive_narrative": "Revenue growth masks a concentration risk.",
    "analyst_narrative": "Revenue grew 23% YoY driven by Electronics in North region.",
    "key_signals": [
        {"label": "Revenue Growth", "value": "23%", "direction": "up"},
        {"label": "Region Concentration", "value": "68% North", "direction": "flat"},
        {"label": "South Decline", "value": "-12%", "direction": "down"},
    ],
    "risk_flag": "68% of revenue from single region — geographic concentration risk.",
    "opportunity_flag": "Services line growing 32% — expand capacity before Q2.",
    "data_type": "sales",
}


class TestValidateAndBuildAnalysis:
    def test_valid_response(self):
        analysis = _validate_and_build_analysis(VALID_AI_RESPONSE, row_count=36, column_count=6)
        assert analysis.executive_narrative == "Revenue growth masks a concentration risk."
        assert analysis.row_count == 36
        assert analysis.column_count == 6
        assert analysis.data_type == "sales"
        assert analysis.analyzed_at  # not empty
        assert len(analysis.key_signals) == 3

    def test_wrong_signal_count_raises(self):
        bad = {**VALID_AI_RESPONSE, "key_signals": [VALID_AI_RESPONSE["key_signals"][0]]}
        with pytest.raises(ValueError, match="Expected 3"):
            _validate_and_build_analysis(bad, row_count=10, column_count=3)

    def test_missing_field_raises(self):
        bad = {k: v for k, v in VALID_AI_RESPONSE.items() if k != "executive_narrative"}
        with pytest.raises(KeyError):
            _validate_and_build_analysis(bad, row_count=10, column_count=3)

    def test_metadata_injected_by_backend(self):
        analysis = _validate_and_build_analysis(VALID_AI_RESPONSE, row_count=100, column_count=8)
        assert analysis.row_count == 100
        assert analysis.column_count == 8
        assert "T" in analysis.analyzed_at  # ISO format check


# ── Full analyze_data flow (mocked Claude) ─────────────────


class TestAnalyzeData:
    @pytest.mark.asyncio
    async def test_successful_analysis(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(VALID_AI_RESPONSE))]
        mock_message.usage = MagicMock(input_tokens=500, output_tokens=300)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("backend.intelligence.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await analyze_data(
                data_summary="test summary",
                row_count=36,
                column_count=6,
            )

        assert result.success is True
        assert result.analysis is not None
        assert result.analysis.executive_narrative == VALID_AI_RESPONSE["executive_narrative"]
        assert result.error is None

    @pytest.mark.asyncio
    async def test_invalid_json_response(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="This is not JSON")]
        mock_message.usage = MagicMock(input_tokens=100, output_tokens=50)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("backend.intelligence.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await analyze_data(
                data_summary="test summary",
                row_count=10,
                column_count=3,
            )

        assert result.success is False
        assert "invalid response" in result.error.lower()

    @pytest.mark.asyncio
    async def test_missing_fields_response(self):
        incomplete = {"executive_narrative": "test"}  # missing all other fields
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(incomplete))]
        mock_message.usage = MagicMock(input_tokens=100, output_tokens=50)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("backend.intelligence.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await analyze_data(
                data_summary="test summary",
                row_count=10,
                column_count=3,
            )

        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_api_error_handled(self):
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        with patch("backend.intelligence.anthropic.AsyncAnthropic", return_value=mock_client):
            # The generic Exception won't be caught by our specific handlers,
            # but let's test the anthropic.APIError path
            import anthropic as anth
            mock_client.messages.create = AsyncMock(
                side_effect=anth.APIStatusError(
                    message="rate limited",
                    response=MagicMock(status_code=429),
                    body={"error": {"message": "rate limited"}},
                )
            )
            result = await analyze_data(
                data_summary="test summary",
                row_count=10,
                column_count=3,
            )

        assert result.success is False
        assert "unavailable" in result.error.lower()

    @pytest.mark.asyncio
    async def test_context_passed_to_prompt(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(VALID_AI_RESPONSE))]
        mock_message.usage = MagicMock(input_tokens=500, output_tokens=300)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("backend.intelligence.anthropic.AsyncAnthropic", return_value=mock_client):
            await analyze_data(
                data_summary="test summary",
                row_count=36,
                column_count=6,
                context="Focus on revenue trends",
            )

        # Verify the message sent to Claude includes context
        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_message = call_kwargs["messages"][0]["content"]
        assert "Focus on revenue trends" in user_message

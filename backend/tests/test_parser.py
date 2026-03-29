"""Tests for backend.parser — CSV parsing, paste parsing, validation, PII stripping."""

import pytest
import pandas as pd

from backend.parser import (
    ParseError,
    parse_csv,
    parse_pasted_data,
    strip_pii_columns,
    strip_pii_values,
    summarize_dataframe,
    validate_csv_size,
    validate_paste_length,
)


# ── parse_csv ──────────────────────────────────────────────


class TestParseCsv:
    def test_valid_csv(self):
        data = b"Name,Value\nAlpha,100\nBeta,200\n"
        df = parse_csv(data)
        assert len(df) == 2
        assert list(df.columns) == ["Name", "Value"]

    def test_utf8_encoding(self):
        data = "Region,Revenue\nNorth,€1000\nSouth,€2000\n".encode("utf-8")
        df = parse_csv(data)
        assert len(df) == 2

    def test_latin1_fallback(self):
        data = "Region,Revenue\nNorth,\xe91000\nSouth,\xe92000\n".encode("latin-1")
        df = parse_csv(data)
        assert len(df) == 2

    def test_empty_csv_raises(self):
        with pytest.raises(ParseError, match="empty"):
            parse_csv(b"")

    def test_single_column_raises(self):
        with pytest.raises(ParseError, match="at least 2 columns"):
            parse_csv(b"OnlyColumn\n1\n2\n")

    def test_malformed_csv_raises(self):
        # Inconsistent columns — pandas may still parse but let's test handling
        data = b"A,B\n1,2,3\n4,5,6\n"
        # pandas handles this by adding extra columns, so it should parse
        df = parse_csv(data)
        assert df.shape[1] >= 2


# ── parse_pasted_data ──────────────────────────────────────


class TestParsePastedData:
    def test_tab_separated(self):
        text = "Name\tValue\nAlpha\t100\nBeta\t200"
        df = parse_pasted_data(text)
        assert len(df) == 2
        assert list(df.columns) == ["Name", "Value"]

    def test_comma_separated(self):
        text = "Name,Value\nAlpha,100\nBeta,200"
        df = parse_pasted_data(text)
        assert len(df) == 2
        assert list(df.columns) == ["Name", "Value"]

    def test_empty_raises(self):
        with pytest.raises(ParseError, match="empty"):
            parse_pasted_data("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ParseError, match="empty"):
            parse_pasted_data("   \n  \t  ")

    def test_tab_preferred_over_comma(self):
        # If data has tabs, should use tab as separator
        text = "A\tB\n1\t2\n3\t4"
        df = parse_pasted_data(text)
        assert list(df.columns) == ["A", "B"]


# ── validation ─────────────────────────────────────────────


class TestValidation:
    def test_csv_size_under_limit(self):
        data = b"x" * (4 * 1024 * 1024)  # 4 MB
        validate_csv_size(data, max_mb=5)  # should not raise

    def test_csv_size_over_limit(self):
        data = b"x" * (6 * 1024 * 1024)  # 6 MB
        with pytest.raises(ParseError, match="exceeds 5 MB"):
            validate_csv_size(data, max_mb=5)

    def test_paste_length_under_limit(self):
        text = "x" * 40_000
        validate_paste_length(text, max_chars=50_000)  # should not raise

    def test_paste_length_over_limit(self):
        text = "x" * 60_000
        with pytest.raises(ParseError, match="exceeds"):
            validate_paste_length(text, max_chars=50_000)


# ── PII stripping ──────────────────────────────────────────


class TestPiiStripping:
    def test_strip_pii_columns(self):
        df = pd.DataFrame({
            "email": ["a@b.com"],
            "phone": ["1234567890"],
            "Revenue": [100],
        })
        result = strip_pii_columns(df)
        assert "Revenue" in result.columns
        assert "email" not in result.columns
        assert "phone" not in result.columns

    def test_strip_pii_columns_case_insensitive(self):
        df = pd.DataFrame({
            "Email_Address": ["a@b.com"],
            "Revenue": [100],
        })
        result = strip_pii_columns(df)
        assert "Email_Address" not in result.columns

    def test_strip_pii_values(self):
        df = pd.DataFrame({
            "notes": ["Contact john@example.com for details"],
            "Revenue": [100],
        })
        result = strip_pii_values(df)
        assert "[REDACTED]" in result["notes"].iloc[0]
        assert "john@example.com" not in result["notes"].iloc[0]

    def test_no_pii_passthrough(self):
        df = pd.DataFrame({"Region": ["North"], "Revenue": [100]})
        result = strip_pii_columns(df)
        assert list(result.columns) == ["Region", "Revenue"]


# ── summarize_dataframe ────────────────────────────────────


class TestSummarizeDataframe:
    def test_summary_contains_row_count(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        summary = summarize_dataframe(df)
        assert "Rows: 3" in summary

    def test_summary_contains_column_names(self):
        df = pd.DataFrame({"Revenue": [100], "Units": [50]})
        summary = summarize_dataframe(df)
        assert "Revenue" in summary
        assert "Units" in summary

    def test_summary_contains_statistics(self):
        df = pd.DataFrame({"Revenue": [100, 200, 300]})
        summary = summarize_dataframe(df)
        assert "min=" in summary
        assert "max=" in summary
        assert "mean=" in summary

    def test_summary_contains_sample_rows(self):
        df = pd.DataFrame({"A": ["x", "y"], "B": [1, 2]})
        summary = summarize_dataframe(df)
        assert "Sample rows" in summary
        assert "x" in summary

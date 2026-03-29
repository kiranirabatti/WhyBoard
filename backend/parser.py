"""
CSV and pasted data parsing — memory only, no disk writes.
"""

import io
import re

import pandas as pd

# PII detection patterns
PII_PATTERNS = [
    re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),  # email
    re.compile(r"\b\d{10}\b"),  # phone (10 digits)
    re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),  # phone formatted
]

PII_COLUMN_KEYWORDS = [
    "email", "phone", "mobile", "contact", "name",
    "address", "ssn", "pan", "aadhaar",
]


class ParseError(Exception):
    """Raised when data cannot be parsed into a valid DataFrame."""


def parse_csv(file_bytes: bytes) -> pd.DataFrame:
    """Parse CSV bytes into a DataFrame. Never writes to disk.

    Tries UTF-8 first, falls back to Latin-1.
    Raises ParseError if the data cannot be parsed.
    """
    for encoding in ("utf-8", "latin-1"):
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
            if df.empty or df.shape[1] < 2:
                raise ParseError("CSV must contain at least 2 columns")
            return df
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise ParseError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ParseError(f"Could not parse CSV: {e}")

    raise ParseError("Could not decode CSV with UTF-8 or Latin-1 encoding")


def parse_pasted_data(text: str) -> pd.DataFrame:
    """Parse tab-separated or comma-separated pasted text into a DataFrame.

    Tries tab-separated first, falls back to comma-separated.
    Raises ParseError if the data cannot be parsed.
    """
    text = text.strip()
    if not text:
        raise ParseError("Pasted data is empty")

    # Try tab-separated first
    try:
        df = pd.read_csv(io.StringIO(text), sep="\t")
        if df.shape[1] > 1:
            return df
    except Exception:
        pass

    # Fall back to comma-separated
    try:
        df = pd.read_csv(io.StringIO(text))
        if df.empty or df.shape[1] < 2:
            raise ParseError("Data must contain at least 2 columns")
        return df
    except pd.errors.EmptyDataError:
        raise ParseError("Pasted data is empty")
    except pd.errors.ParserError as e:
        raise ParseError(f"Could not parse pasted data: {e}")


def validate_csv_size(file_bytes: bytes, max_mb: int = 5) -> None:
    """Validate CSV file size. Raises ParseError if too large."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        raise ParseError(f"File size ({size_mb:.1f} MB) exceeds {max_mb} MB limit")


def validate_paste_length(text: str, max_chars: int = 50_000) -> None:
    """Validate pasted text length. Raises ParseError if too long."""
    if len(text) > max_chars:
        raise ParseError(
            f"Pasted data ({len(text):,} chars) exceeds {max_chars:,} char limit"
        )


def strip_pii_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns that likely contain PII based on column name keywords."""
    cols_to_drop = []
    for col in df.columns:
        col_lower = col.lower().strip()
        if any(keyword in col_lower for keyword in PII_COLUMN_KEYWORDS):
            cols_to_drop.append(col)

    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    return df


def strip_pii_values(df: pd.DataFrame) -> pd.DataFrame:
    """Mask PII patterns (emails, phone numbers) in string columns."""
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        for pattern in PII_PATTERNS:
            df[col] = df[col].astype(str).apply(
                lambda val, p=pattern: p.sub("[REDACTED]", val)
            )
    return df


def summarize_dataframe(df: pd.DataFrame) -> str:
    """Convert a DataFrame into a structured text summary for the AI layer.

    Returns a human-readable summary with:
    - Row/column counts
    - Column names and types
    - Key statistics for numeric columns
    - Categorical breakdowns
    - Sample rows (first 5)
    - Notable patterns and correlations
    """
    lines = []

    # Basic info
    lines.append("Dataset Summary:")
    lines.append(f"- Rows: {len(df):,}")
    lines.append(f"- Columns: {', '.join(df.columns.tolist())}")
    lines.append("")

    # Column types
    lines.append("Column Types:")
    for col in df.columns:
        dtype = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "text"
        unique_count = df[col].nunique()
        lines.append(f"- {col}: {dtype} ({unique_count:,} unique values)")
    lines.append("")

    # Numeric statistics
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        lines.append("Column Statistics:")
        for col in numeric_cols:
            stats = df[col].describe()
            lines.append(
                f"- {col}: min={stats['min']:,.2f} | max={stats['max']:,.2f} | "
                f"mean={stats['mean']:,.2f} | median={stats['50%']:,.2f} | "
                f"sum={df[col].sum():,.2f}"
            )
        lines.append("")

    # Categorical breakdowns — group by text columns and aggregate numeric
    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    if text_cols and numeric_cols:
        lines.append("Breakdowns:")
        for text_col in text_cols[:3]:  # Limit to first 3 text columns
            if df[text_col].nunique() <= 20:  # Only if manageable cardinality
                for num_col in numeric_cols[:2]:  # First 2 numeric cols
                    grouped = df.groupby(text_col)[num_col].sum().sort_values(ascending=False)
                    total = grouped.sum()
                    lines.append(f"- {num_col} by {text_col}:")
                    for cat, val in grouped.items():
                        pct = (val / total * 100) if total > 0 else 0
                        lines.append(f"    {cat}: {val:,.2f} ({pct:.1f}%)")
        lines.append("")

    # Sample rows
    sample = df.head(5)
    lines.append(f"Sample rows (first {len(sample)}):")
    for _, row in sample.iterrows():
        lines.append(", ".join(str(v) for v in row.values))
    lines.append("")

    # Notable patterns
    patterns_found = []
    for col in numeric_cols:
        if len(df) >= 3:
            last_3 = df[col].tail(3).tolist()
            if all(last_3[i] > last_3[i + 1] for i in range(len(last_3) - 1)):
                patterns_found.append(f"- {col} shows declining trend in last 3 rows")
            elif all(last_3[i] < last_3[i + 1] for i in range(len(last_3) - 1)):
                patterns_found.append(f"- {col} shows increasing trend in last 3 rows")

    # Concentration analysis
    for col in numeric_cols:
        total = df[col].sum()
        if total > 0:
            max_val = df[col].max()
            if max_val / total > 0.3:
                patterns_found.append(
                    f"- {col}: single highest value represents {max_val / total:.0%} of total"
                )

    # Variance/spread analysis
    for col in numeric_cols:
        if len(df) >= 3:
            cv = df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
            if cv > 0.5:
                patterns_found.append(
                    f"- {col}: high variability (coefficient of variation: {cv:.2f})"
                )

    if patterns_found:
        lines.append("Notable patterns:")
        lines.extend(patterns_found)
    else:
        lines.append("Notable patterns: None detected")

    return "\n".join(lines)


def prepare_data_for_ai(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Full pipeline: strip PII, then summarize. Returns cleaned df and summary."""
    cleaned = strip_pii_columns(df)
    cleaned = strip_pii_values(cleaned)
    summary = summarize_dataframe(cleaned)
    return cleaned, summary

# Data Handling Rules — WhyBoard
> CSV parsing, memory-only processing, PII rules.

---

## The Fundamental Rule

**WhyBoard never stores data. Ever.**

No database. No file system writes. No S3 bucket. No cache with data content.
Every upload is processed in memory and discarded after the response is sent.
If someone asks you to add persistence for data — refuse and ask for explicit instruction.

---

## CSV Parsing (parser.py)

### Ingestion

```python
import pandas as pd
import io

def parse_csv(file_bytes: bytes) -> pd.DataFrame:
    """Parse CSV bytes into DataFrame. Never write to disk."""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding='latin-1')
    return df

def parse_pasted_data(text: str) -> pd.DataFrame:
    """Parse tab-separated or comma-separated pasted text."""
    # Try tab-separated first (common from Excel copy-paste)
    try:
        df = pd.read_csv(io.StringIO(text), sep='\t')
        if df.shape[1] > 1:
            return df
    except Exception:
        pass
    # Fall back to comma-separated
    return pd.read_csv(io.StringIO(text))
```

### Normalization — What Gets Sent to Claude

Never send raw rows to Claude. Always send a structured summary:

```python
def summarize_dataframe(df: pd.DataFrame) -> str:
    """Convert DataFrame to a structured summary for Claude."""
    summary_lines = [
        f"Dataset Summary:",
        f"- Rows: {len(df):,}",
        f"- Columns: {', '.join(df.columns.tolist())}",
        f"",
        "Column Statistics:",
    ]

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            summary_lines.append(
                f"- {col}: min={df[col].min():,.0f} | "
                f"max={df[col].max():,.0f} | "
                f"mean={df[col].mean():,.0f} | "
                f"total={df[col].sum():,.0f}"
            )
        else:
            top_vals = df[col].value_counts().head(5).index.tolist()
            summary_lines.append(f"- {col}: top values = {top_vals}")

    summary_lines += ["", "Sample rows (first 5):"]
    summary_lines.append(df.head(5).to_string(index=False))

    return "\n".join(summary_lines)
```

---

## PII Stripping

Strip before summarizing. These columns should be masked:

```python
PII_PATTERNS = [
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # email
    r'\b\d{10}\b',                                          # phone (10 digit)
    r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',                    # phone (formatted)
]

PII_COLUMN_KEYWORDS = ['email', 'phone', 'mobile', 'contact', 'name', 'address', 'ssn', 'pan', 'aadhaar']

def strip_pii_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns that appear to contain PII."""
    df = df.copy()
    for col in df.columns:
        if any(keyword in col.lower() for keyword in PII_COLUMN_KEYWORDS):
            df = df.drop(columns=[col])
    return df
```

---

## File Size Limits

| Input | Max Size | Reason |
|---|---|---|
| CSV upload | 5 MB | Prevents memory abuse |
| Pasted text | 50,000 characters | Practical limit |
| DAX query result (Phase 2) | 1,000 rows | API cost + token limit |

Enforce at the FastAPI layer with `UploadFile` size validation.

---

## Logging Rules

**Log this (metadata only):**
- Row count, column count, detected data type
- Processing time (ms)
- AI response time (ms)
- Errors (type only, no content)

**Never log this:**
- Any data values
- Column contents
- Raw CSV text
- User-provided context text

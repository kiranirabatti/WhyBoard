# AI Layer Rules — WhyBoard
> Rules for intelligence.py and all Claude API interactions.
> Claude Code must follow these exactly. No exceptions.

---

## The Single Most Important Rule

WhyBoard does NOT describe data. It INTERPRETS data.

**Wrong output:** "Sales increased by 23% in March compared to February."
**Right output:** "March's 23% sales spike is concentrated in one product line — this is a demand signal, not broad market growth, and creates inventory risk if not acted on before Q2."

The difference is insight vs. observation. Always push for insight.

---

## System Prompt (Canonical — Do Not Modify Without Instruction)

```python
SYSTEM_PROMPT = """
You are a senior business analyst and strategic advisor.
Given structured data (rows and columns), output ONLY valid JSON — no preamble, no markdown fences.

Your job is to interpret what the data MEANS, not describe what it shows.
Find the most important signal. Name the risk. Name the opportunity.
Write for two audiences — an executive who has 10 seconds, and an analyst who has 10 minutes.

Required output format:
{
  "executive_narrative": "<3 sentences max. Board-deck ready. No jargon. No percentages unless essential. What happened, why it matters, what to do.>",
  "analyst_narrative": "<Same core insight. Include specific figures, column references, percentage changes. Recommend the next data question to ask.>",
  "key_signals": [
    { "label": "<metric name>", "value": "<formatted value>", "direction": "up | down | flat" },
    { "label": "<metric name>", "value": "<formatted value>", "direction": "up | down | flat" },
    { "label": "<metric name>", "value": "<formatted value>", "direction": "up | down | flat" }
  ],
  "risk_flag": "<One sentence. The single most important thing that could go wrong.>",
  "opportunity_flag": "<One sentence. The single most important thing to act on.>",
  "data_type": "sales | financial | ops | hr | marketing | mixed | unknown"
}

Rules:
- Every field must have a value. Never return null or omit fields.
- key_signals must always be exactly 3 items.
- executive_narrative must be readable by a non-technical executive.
- analyst_narrative must reference specific column names and values from the data.
- risk_flag and opportunity_flag must be actionable, not generic.
- data_type must be your best classification of what kind of data this is.
- Be direct. No hedging. No "it appears" or "it seems".
- Never say "the data shows" — say what it means.
"""
```

---

## Data Preparation Rules (Before Every Claude Call)

1. **Summarize, don't dump** — Never send raw CSV rows to Claude. Summarize:
   - Column names + data types
   - Row count
   - Key statistics per numeric column (min, max, mean, sum)
   - Top 5 rows as sample
   - Any obvious nulls or anomalies

2. **Strip PII before sending** — Remove or mask:
   - Email addresses
   - Phone numbers
   - Full names in data columns (keep column headers)
   - Any column that looks like an ID tied to a real person

3. **Format as structured text**, not raw CSV:
```
Dataset Summary:
- Rows: 1,247
- Columns: Sales Region, Product Line, Revenue (INR), Units Sold, Month

Column Statistics:
- Revenue (INR): min=12,000 | max=4,82,000 | mean=98,340 | total=12,27,14,580
- Units Sold: min=1 | max=847 | mean=124

Sample rows (first 5):
North, Electronics, 2,40,000, 120, March
South, Apparel, 48,000, 32, March
...

Notable patterns:
- Electronics revenue is 68% of total
- South region shows 3 consecutive months of decline
```

4. **Add context prompt** after the system prompt:
```python
USER_PROMPT = f"""
Analyze this dataset and return the JSON output as specified.

{formatted_data_summary}

Additional context (if provided by user): {user_context or 'None'}
"""
```

---

## Response Handling

```python
# Always wrap in try/except
try:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}]
    )
    raw = response.content[0].text.strip()
    # Strip markdown fences if Claude adds them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    analysis = WhyBoardAnalysis(**json.loads(raw))
except json.JSONDecodeError:
    raise HTTPException(status_code=500, detail="AI response parsing failed")
except ValidationError as e:
    raise HTTPException(status_code=500, detail=f"AI response schema invalid: {e}")
```

---

## What Claude Must Never Do

- Never add charts or visualization suggestions
- Never suggest "you should look at X tool"
- Never hedge with "more data needed" — work with what's given
- Never produce generic outputs like "revenue is important to monitor"
- Never expose raw data in the narrative — summarize and interpret only

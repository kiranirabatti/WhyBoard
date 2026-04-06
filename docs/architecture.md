# WhyBoard — Architecture & API Contracts
> Full technical reference. Keep this updated as the product evolves.

---

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                  DATA SOURCES                       │
├─────────────────┬───────────────┬───────────────────┤
│   CSV Upload    │  Paste Data   │  Power BI OAuth   │
│   (Phase 1)     │  (Phase 1)    │  (Phase 2)        │
└────────┬────────┴───────┬───────┴─────────┬─────────┘
         │                │                 │
         └────────────────▼─────────────────┘
                          │
┌─────────────────────────▼─────────────────────────┐
│              Python / FastAPI Backend              │
│                                                    │
│  parser.py      → normalize all inputs to         │
│                   pandas DataFrame                 │
│                                                    │
│  parser.py      → summarize DataFrame             │
│                   (never send raw rows to AI)      │
│                                                    │
│  parser.py      → strip PII columns               │
│                                                    │
│  intelligence.py → Claude API call                │
│                    (system prompt + summary)       │
│                                                    │
│  schema.py      → validate + structure response   │
└─────────────────────────┬─────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────┐
│              React Frontend                        │
│                                                    │
│  DataInput.tsx      → CSV upload or paste         │
│  NarrativeView.tsx  → Hero output display         │
│  ModeToggle.tsx     → Executive / Analyst         │
│  SignalCards.tsx    → 3 key signals               │
│  CopyButton.tsx     → One-click copy              │
└────────────────────────────────────────────────────┘
```

---

## Phase 2 Addition — Power BI Auth Flow

```
User Browser          WhyBoard Frontend     WhyBoard Backend      Microsoft / Power BI
─────────────         ─────────────────     ────────────────      ────────────────────
Click "Connect" ────→ GET /api/auth/login ──────────────────────→ Redirect to MS login
                                                                   ↓
                                           GET /api/auth/callback ←── Auth code returned
                                                ↓
                                           Exchange code for token
                                                ↓
                                           Store token in session
                                                ↓
                       { authenticated: true } ←──────────────────
                            ↓
                       Show workspace picker ──→ GET /api/powerbi/workspaces ─→ PBI API
                       Show dataset picker  ──→ GET /api/powerbi/.../datasets ─→ PBI API
                       Show table picker   ──→ GET /api/powerbi/.../tables   ─→ PBI API
                       Click "Analyze"     ──→ POST /api/powerbi/.../query   ─→ PBI API
                                                ↓
                                           Rows → DataFrame → AI → Response
                            ↓
                       Same NarrativeView ←──────────────────────
```

---

## API Contract

### POST /api/analyze/csv

**Request:** `multipart/form-data`
```
file: <CSV file>
context: <optional string — user-provided context about the data>
```

**Response:** `application/json`
```json
{
  "success": true,
  "analysis": {
    "executive_narrative": "...",
    "analyst_narrative": "...",
    "key_signals": [
      { "label": "...", "value": "...", "direction": "up" },
      { "label": "...", "value": "...", "direction": "down" },
      { "label": "...", "value": "...", "direction": "flat" }
    ],
    "risk_flag": "...",
    "opportunity_flag": "...",
    "data_type": "sales",
    "row_count": 1247,
    "column_count": 6,
    "analyzed_at": "2026-03-29T10:30:00Z"
  }
}
```

**Error response:**
```json
{
  "success": false,
  "error": "File too large. Maximum size is 5MB."
}
```

---

### POST /api/analyze/paste

**Request:** `application/json`
```json
{
  "data": "Region\tProduct\tRevenue\nNorth\tElectronics\t240000\n...",
  "context": "Optional context about this data"
}
```

**Response:** Same as `/api/analyze/csv`

---

### GET /api/auth/login (Phase 2)
Redirects to Microsoft OAuth. No request body.

---

### GET /api/auth/callback (Phase 2)
OAuth callback. Handled server-side. Redirects frontend to `/` with session established.

---

### GET /api/auth/status (Phase 2)

**Response:**
```json
{
  "authenticated": true,
  "user_email": "name@scriptshub.net"
}
```

---

### GET /api/powerbi/workspaces (Phase 2)

**Response:**
```json
{
  "workspaces": [
    { "id": "uuid", "name": "ScriptsHub Analytics" }
  ]
}
```

---

### GET /api/powerbi/workspaces/{workspace_id}/datasets (Phase 2)

**Response:**
```json
{
  "datasets": [
    { "id": "uuid", "name": "Sales Dashboard Dataset" }
  ]
}
```

---

### GET /api/powerbi/datasets/{dataset_id}/tables (Phase 2)

**Response:**
```json
{
  "tables": [
    { "name": "SalesTable" },
    { "name": "RegionTable" }
  ]
}
```

---

### POST /api/powerbi/datasets/{dataset_id}/query (Phase 2)

**Request:** `application/json`
```json
{
  "table_name": "SalesTable",
  "context": "Optional user context"
}
```

**Response:** Same structure as `/api/analyze/csv`

---

## Pydantic Models (schema.py)

```python
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class KeySignal(BaseModel):
    label: str
    value: str
    direction: Literal['up', 'down', 'flat']

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

class PasteRequest(BaseModel):
    data: str
    context: str | None = None

class PowerBIQueryRequest(BaseModel):
    table_name: str
    context: str | None = None
```

---

## Environment Variables

```bash
# .env (never commit this file)

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Azure AD (Phase 2)
AZURE_CLIENT_ID=
AZURE_TENANT_ID=
AZURE_CLIENT_SECRET=
REDIRECT_URI=http://localhost:8000/api/auth/callback

# Session
SESSION_SECRET=<32 random chars>

# App
ENVIRONMENT=development
MAX_CSV_SIZE_MB=5
MAX_PASTE_CHARS=50000
MAX_DAX_ROWS=1000
```

---

## Phase Build Checklist

### Phase 1 — CSV + Paste (Start here)
- [ ] FastAPI scaffold with health endpoint
- [ ] `schema.py` — all Pydantic models
- [ ] `parser.py` — CSV + paste ingestion + PII strip + summarize
- [ ] `intelligence.py` — Claude API call + defensive parsing
- [ ] `main.py` — wire up `/api/analyze/csv` and `/api/analyze/paste`
- [ ] React scaffold with Vite + TypeScript + Tailwind
- [ ] `DataInput.tsx` — CSV upload + paste tabs
- [ ] `ModeToggle.tsx` — Executive / Analyst
- [ ] `NarrativeView.tsx` — narrative display with toggle
- [ ] `SignalCards.tsx` — 3 signal cards
- [ ] `CopyButton.tsx` — clipboard copy
- [ ] `whyboard.ts` — all API calls centralized
- [ ] Sample data files in `/sample-data/`
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] End-to-end test with all 3 sample CSVs

### Phase 2 — Power BI OAuth
- [ ] Azure AD app registered (manual step — not code)
- [ ] `.env` updated with AZURE_CLIENT_ID, TENANT_ID, CLIENT_SECRET
- [ ] `auth.py` — MSAL OAuth flow
- [ ] `powerbi.py` — REST API client (workspaces, datasets, tables, query)
- [ ] Auth endpoints wired in `main.py`
- [ ] Power BI query endpoint wired (reuses same intelligence pipeline)
- [ ] `PowerBIConnect.tsx` — connect button + workspace/dataset/table picker
- [ ] Token refresh handled silently
- [ ] End-to-end test with real ScriptsHub Power BI workspace

### Phase 3 — Azure + Teams
- [ ] Azure App Service deployment
- [ ] Azure Functions for scheduled refresh trigger
- [ ] Teams webhook integration
- [ ] Per-team configuration store

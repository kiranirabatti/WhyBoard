# WhyBoard — Claude Code Root Memory
> Read this first. Every session. No exceptions.

---

## What WhyBoard Is

WhyBoard turns raw data into board-ready narrative intelligence.

You upload a CSV, paste a table, or connect your Power BI workspace — WhyBoard tells you **what the data means**, not what it shows. BI tools describe. WhyBoard interprets.

**The core mechanic:**
```
Data in (CSV / paste / Power BI dataset)
→ AI reads the numbers
→ AI writes the "so what" — insight, risk, opportunity
→ Human gets a narrative they can paste into a board deck or client email
```

**What it is NOT:**
- Not a BI tool — no chart builder, no drag-and-drop dashboards
- Not a data warehouse — nothing is stored, everything is processed in memory
- Not a report generator — it produces narrative intelligence, not formatted documents

---

## Current Phase

> **Update this every session.**

**Active Phase: Phase 1 — CSV + Paste MVP**

| Phase | Status | Description |
|---|---|---|
| Phase 1 | 🔨 In Progress | CSV upload + paste → AI narrative → Executive/Analyst toggle |
| Phase 2 | ⏳ Planned | Power BI OAuth → Workspace → Dataset → Table picker → same AI layer |
| Phase 3 | ⏳ Planned | Scheduled refresh, Teams notification, Azure hosting, client config |

---

## Product Decisions (Non-Negotiable)

- **No charts** — the narrative IS the product. Never add charting libraries without explicit instruction.
- **No data storage** — process everything in memory. Never write data to disk or database.
- **Executive / Analyst toggle** is the hero feature — same insight, two audiences. Never compromise its UX.
- **Internal ScriptsHub use first** — single Azure AD tenant, ScriptsHub Microsoft accounts only.
- **Power BI OAuth is Delegated flow** — users log in with their own Microsoft work account.

---

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend | Python 3.11+, FastAPI, uvicorn | Async throughout |
| AI | Anthropic SDK, `claude-sonnet-4-6` | Never hardcode another model |
| Auth | `msal` (Microsoft Authentication Library) | Delegated OAuth, single tenant |
| Power BI | Power BI REST API | httpx async calls with bearer token |
| Data | `pandas` | CSV parsing + DAX response normalization |
| Frontend | React 18, TypeScript, Tailwind CSS, Vite | Strict TypeScript — no `any` |
| HTTP | `httpx` (async) | Never use `requests` in FastAPI |
| Deploy (dev) | Backend → Railway, Frontend → Vercel | |
| Deploy (prod) | Azure App Service + Azure Functions | Phase 3 |

---

## Folder Structure

```
whyboard/
├── CLAUDE.md                        ← You are here
├── .claude/
│   └── rules/
│       ├── ai-layer.md              ← Prompt design + output schema rules
│       ├── frontend.md              ← React + TypeScript conventions
│       ├── data-handling.md         ← CSV parsing, memory-only rules
│       └── powerbi-auth.md          ← OAuth flow, MSAL, API patterns
├── docs/
│   └── architecture.md             ← Full architecture + API contracts
├── backend/
│   ├── main.py                     ← FastAPI entry point
│   ├── intelligence.py             ← Claude API brain
│   ├── parser.py                   ← CSV + DAX response normalization
│   ├── powerbi.py                  ← Power BI REST API client (Phase 2)
│   ├── auth.py                     ← MSAL OAuth handling (Phase 2)
│   ├── schema.py                   ← Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DataInput.tsx       ← CSV upload + paste tab
│   │   │   ├── PowerBIConnect.tsx  ← OAuth connect + dataset picker (Phase 2)
│   │   │   ├── NarrativeView.tsx   ← Hero output component
│   │   │   ├── SignalCards.tsx     ← 3 key signals beneath narrative
│   │   │   ├── ModeToggle.tsx      ← Executive / Analyst toggle
│   │   │   └── CopyButton.tsx      ← One-click copy narrative
│   │   ├── api/
│   │   │   └── whyboard.ts         ← All API calls centralized here
│   │   └── types/
│   │       └── index.ts            ← Shared TypeScript interfaces
│   └── package.json
└── sample-data/
    ├── sales-q1.csv                ← Pre-loaded demo: sales data
    ├── ops-metrics.csv             ← Pre-loaded demo: ops data
    └── financial-summary.csv       ← Pre-loaded demo: finance data
```

---

## API Endpoints

| Method | Path | Phase | Description |
|---|---|---|---|
| POST | `/api/analyze/csv` | 1 | Analyze uploaded CSV file |
| POST | `/api/analyze/paste` | 1 | Analyze pasted table data |
| GET | `/api/auth/login` | 2 | Initiate Microsoft OAuth flow |
| GET | `/api/auth/callback` | 2 | OAuth callback, store token in session |
| GET | `/api/auth/status` | 2 | Check if user is authenticated |
| GET | `/api/powerbi/workspaces` | 2 | List user's Power BI workspaces |
| GET | `/api/powerbi/workspaces/{id}/datasets` | 2 | List datasets in workspace |
| GET | `/api/powerbi/datasets/{id}/tables` | 2 | List tables in dataset |
| POST | `/api/powerbi/datasets/{id}/query` | 2 | Execute DAX query, return rows |
| GET | `/api/health` | 1 | Health check |

---

## Engineering Non-Negotiables

1. **Model**: Always use `claude-sonnet-4-6`. Never hardcode another.
2. **Type safety**: Strict TypeScript. Never use `any`. Extend interfaces correctly.
3. **Async**: Use `httpx` (async) in FastAPI. Never `requests`.
4. **Memory only**: Never write data to disk. No database. No file storage.
5. **Defensive parsing**: All Claude responses in `try/except`. Always validate JSON.
6. **No PII logging**: Never log data content. Log only metadata (row count, column count).
7. **Token handling**: Never expose OAuth tokens to the frontend. Backend holds tokens in server-side session only.
8. **API centralization**: All frontend API calls in `frontend/src/api/whyboard.ts` only.
9. **Toggle is sacred**: Executive/Analyst toggle is the hero UX. Never degrade it.
10. **Loading skeleton**: Use skeleton loader during AI processing. Never a spinner.

---

## The Narrative Output Schema

```typescript
interface WhyBoardAnalysis {
  // Core narrative — the hero output
  executive_narrative: string;       // 3 sentences max, board-deck ready, no jargon
  analyst_narrative: string;         // Same insight, with data references + percentages

  // Supporting signals
  key_signals: [                     // Exactly 3 — the evidence behind the narrative
    { label: string; value: string; direction: 'up' | 'down' | 'flat'; },
    { label: string; value: string; direction: 'up' | 'down' | 'flat'; },
    { label: string; value: string; direction: 'up' | 'down' | 'flat'; },
  ];

  // Flags
  risk_flag: string;                 // One line — what to watch
  opportunity_flag: string;          // One line — what to act on

  // Metadata (added by backend, not Claude)
  data_type: string;                 // e.g. "sales", "ops", "financial", "unknown"
  row_count: number;
  column_count: number;
  analyzed_at: string;               // ISO timestamp
}
```

---

## What "Done" Looks Like Per Phase

**Phase 1 Done:**
- User uploads CSV or pastes data
- AI returns narrative in < 8 seconds
- Executive / Analyst toggle works smoothly
- Copy button copies the active narrative to clipboard
- Error state handled cleanly — no stack traces visible
- Deployed on Railway + Vercel with a working public URL

**Phase 2 Done:**
- "Connect Power BI" button initiates Microsoft OAuth
- User can browse their workspaces → datasets → tables
- Selecting a table triggers the same AI analysis pipeline
- Token refresh handled silently in background
- Disconnecting clears the session cleanly

**Phase 3 Done:**
- Scheduled analysis runs when Power BI dataset refreshes
- Result posted to Microsoft Teams channel automatically
- Deployed on Azure App Service
- Per-team configuration (which workspace, which channel)

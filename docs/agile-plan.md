# WhyBoard — Agile Development Plan

> Project Start: 2026-03-29
> Methodology: Agile Scrum
> Sprint Duration: 1 week
> Total Phases: 3 | Current Focus: Phase 1 (MVP)

---

## 1. Agentic Team Structure

| Role | Responsibility | Mapped Agent |
|---|---|---|
| **Product Owner** | Owns backlog, prioritizes stories, accepts/rejects deliverables | User (you) |
| **Scrum Master** | Facilitates sprints, removes blockers, enforces Definition of Done | Claude (orchestrator) |
| **Backend Engineer** | FastAPI, Python, Claude API integration, data parsing | Claude (backend agent) |
| **Frontend Engineer** | React, TypeScript, Tailwind, component architecture | Claude (frontend agent) |
| **QA Engineer** | Unit tests, integration tests, E2E validation, STLC execution | Claude (test agent) |
| **DevOps Engineer** | CI/CD, Railway/Vercel deployment, environment setup | Claude (devops agent) |
| **AI/ML Engineer** | Prompt engineering, Claude response validation, output quality | Claude (AI agent) |

---

## 2. SDLC Phases Mapped to WhyBoard

```
┌─────────────┐    ┌──────────┐    ┌────────┐    ┌─────────┐    ┌──────────┐    ┌────────────┐
│ Requirements │ -> │  Design  │ -> │  Build │ -> │  Test   │ -> │  Deploy  │ -> │  Maintain   │
│  (CLAUDE.md) │    │(arch.md) │    │(Sprints│    │ (STLC)  │    │(Railway/ │    │(Phase 2+3) │
│  (specs)     │    │(rules)   │    │ below) │    │         │    │ Vercel)  │    │            │
└─────────────┘    └──────────┘    └────────┘    └─────────┘    └──────────┘    └────────────┘
     DONE              DONE         IN PROGRESS
```

**Requirements** — Complete (CLAUDE.md, architecture.md, ai-layer.md, data-handling.md, frontend.md, powerbi-auth.md)
**Design** — Complete (API contracts, Pydantic models, TypeScript interfaces, folder structure all defined)
**Build** — Starting now (Phase 1 sprints below)
**Test** — Parallel with build (STLC defined in Section 6)
**Deploy** — End of Phase 1 (Railway + Vercel)
**Maintain** — Phase 2 & 3 iterations

---

## 3. Product Backlog

### Epic 1: Project Scaffolding & Infrastructure
> *Set up the development environment, project structure, and CI pipeline.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E1-S1** | As a developer, I want the backend project scaffolded with FastAPI, uvicorn, and all dependencies so I can start building endpoints | Must | 3 |
| **E1-S2** | As a developer, I want the frontend project scaffolded with React 18, TypeScript, Vite, and Tailwind so I can start building UI | Must | 3 |
| **E1-S3** | As a developer, I want Pydantic models (schema.py) and TypeScript interfaces (types/index.ts) defined so backend and frontend share a contract | Must | 2 |
| **E1-S4** | As a developer, I want a health check endpoint (`GET /api/health`) returning `{status: "ok"}` so I can verify the backend runs | Must | 1 |
| **E1-S5** | As a developer, I want sample CSV files (sales, ops, finance) in `/sample-data/` for testing | Should | 2 |
| **E1-S6** | As a developer, I want `.env.example`, `.gitignore`, and project configs (tsconfig, vite.config, etc.) properly set up | Must | 2 |

**Epic 1 Total: 13 story points**

---

### Epic 2: Data Ingestion Layer
> *Accept CSV uploads and pasted tabular data, parse into DataFrames, summarize for AI.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E2-S1** | As a user, I want to upload a CSV file (up to 5 MB) so the system can analyze my data | Must | 3 |
| **E2-S2** | As a user, I want to paste tab-separated or comma-separated data so I can quickly analyze without a file | Must | 3 |
| **E2-S3** | As a developer, I want a `parse_csv()` function that reads bytes into a DataFrame with UTF-8/Latin-1 fallback | Must | 2 |
| **E2-S4** | As a developer, I want a `parse_pasted_data()` function that auto-detects tab vs comma delimiters | Must | 2 |
| **E2-S5** | As a developer, I want a `summarize_dataframe()` function that produces a structured text summary (stats, samples, patterns) for Claude | Must | 5 |
| **E2-S6** | As a developer, I want PII columns stripped before data reaches the AI layer | Must | 3 |
| **E2-S7** | As a developer, I want file size and character count validation with clear error messages | Must | 2 |

**Epic 2 Total: 20 story points**

---

### Epic 3: AI Intelligence Layer
> *Send summarized data to Claude, receive structured narrative analysis.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E3-S1** | As a developer, I want `intelligence.py` with the canonical system prompt that instructs Claude to interpret data and return JSON | Must | 5 |
| **E3-S2** | As a developer, I want defensive response parsing — strip markdown fences, validate JSON, catch errors | Must | 3 |
| **E3-S3** | As a developer, I want the AI to return exactly the `WhyBoardAnalysis` schema with all fields populated (never null) | Must | 3 |
| **E3-S4** | As a developer, I want metadata fields (data_type, row_count, column_count, analyzed_at) injected by the backend, not Claude | Must | 2 |
| **E3-S5** | As a user, I want the AI response in under 8 seconds for typical datasets | Should | 3 |

**Epic 3 Total: 16 story points**

---

### Epic 4: API Endpoints (Phase 1)
> *Wire up FastAPI routes for CSV analysis, paste analysis, and health check.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E4-S1** | As a user, I want `POST /api/analyze/csv` to accept a CSV file upload and return an `AnalyzeResponse` | Must | 3 |
| **E4-S2** | As a user, I want `POST /api/analyze/paste` to accept pasted text data and return an `AnalyzeResponse` | Must | 3 |
| **E4-S3** | As a developer, I want proper CORS configuration for the frontend origin | Must | 1 |
| **E4-S4** | As a developer, I want error responses to be clean JSON — never stack traces to the client | Must | 2 |

**Epic 4 Total: 9 story points**

---

### Epic 5: Frontend — Data Input
> *Build the data entry interface with CSV upload and paste tabs.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E5-S1** | As a user, I want a tabbed interface with "Upload CSV" and "Paste Data" tabs | Must | 3 |
| **E5-S2** | As a user, I want drag-and-drop CSV upload with a click-to-browse fallback | Must | 3 |
| **E5-S3** | As a user, I want a monospace textarea for pasting tabular data with an example placeholder | Must | 2 |
| **E5-S4** | As a user, I want the "Analyze" button disabled until I provide data | Must | 1 |
| **E5-S5** | As a user, I want a skeleton loader while the AI processes my data (never a spinner) | Must | 2 |

**Epic 5 Total: 11 story points**

---

### Epic 6: Frontend — Narrative Output (Hero Feature)
> *Display the AI-generated narrative with Executive/Analyst toggle, signal cards, and copy.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E6-S1** | As a user, I want to see the AI narrative displayed prominently with editorial typography | Must | 3 |
| **E6-S2** | As a user, I want an Executive/Analyst toggle that smoothly switches between narrative versions (300ms fade) | Must | 5 |
| **E6-S3** | As a user, I want 3 signal cards below the narrative showing key metrics with directional indicators (up/down/flat) | Must | 3 |
| **E6-S4** | As a user, I want a risk flag and opportunity flag displayed clearly | Must | 2 |
| **E6-S5** | As a user, I want a copy button that copies the active narrative with "Copied!" feedback for 2 seconds | Must | 2 |
| **E6-S6** | As a user, I want clean error states — never a stack trace, always a human-readable message | Must | 2 |

**Epic 6 Total: 17 story points**

---

### Epic 7: Integration, Polish & Deployment
> *End-to-end flow, responsive design, and production deployment.*

| Story ID | User Story | Priority | Points |
|---|---|---|---|
| **E7-S1** | As a user, I want the full flow working end-to-end: upload CSV -> see narrative -> toggle -> copy | Must | 5 |
| **E7-S2** | As a user, I want the app to look good on desktop (responsive is nice-to-have) | Should | 3 |
| **E7-S3** | As a developer, I want the backend deployed to Railway with env vars configured | Must | 3 |
| **E7-S4** | As a developer, I want the frontend deployed to Vercel with API proxy configured | Must | 3 |
| **E7-S5** | As a developer, I want the deployed URLs working end-to-end | Must | 2 |

**Epic 7 Total: 16 story points**

---

## 4. Sprint Plan — Phase 1 (MVP)

> **Velocity assumption:** ~20 story points per sprint (1-week sprints)
> **Total Phase 1 points:** 102 story points across 7 epics
> **Estimated sprints:** 5 sprints (5 weeks)

---

### Sprint 1: Foundation (Week 1)
**Goal:** Project scaffolded, contracts defined, health check working, sample data ready.

| Story | Points | Status |
|---|---|---|
| E1-S1: Scaffold backend (FastAPI + deps) | 3 | Pending |
| E1-S2: Scaffold frontend (React + Vite + Tailwind) | 3 | Pending |
| E1-S3: Define Pydantic models + TS interfaces | 2 | Pending |
| E1-S4: Health check endpoint | 1 | Pending |
| E1-S5: Sample CSV files | 2 | Pending |
| E1-S6: Project configs (.env.example, .gitignore, etc.) | 2 | Pending |
| E2-S3: `parse_csv()` function | 2 | Pending |
| E2-S4: `parse_pasted_data()` function | 2 | Pending |
| E2-S7: File size validation | 2 | Pending |

**Sprint 1 Total: 19 points**

**Definition of Done — Sprint 1:**
- `python -m uvicorn backend.main:app` starts without errors
- `npm run dev` starts the React app
- `GET /api/health` returns `{status: "ok"}`
- `parse_csv()` and `parse_pasted_data()` unit tests pass
- Sample CSVs load correctly into DataFrames

---

### Sprint 2: Data Pipeline + AI Brain (Week 2)
**Goal:** Full data ingestion pipeline and Claude integration working.

| Story | Points | Status |
|---|---|---|
| E2-S5: `summarize_dataframe()` | 5 | Pending |
| E2-S6: PII stripping | 3 | Pending |
| E3-S1: `intelligence.py` with system prompt | 5 | Pending |
| E3-S2: Defensive response parsing | 3 | Pending |
| E3-S3: Schema validation for AI output | 3 | Pending |
| E3-S4: Backend metadata injection | 2 | Pending |

**Sprint 2 Total: 21 points**

**Definition of Done — Sprint 2:**
- `summarize_dataframe()` produces correct structured summary for all 3 sample CSVs
- PII columns are detected and stripped (unit tests)
- `intelligence.py` calls Claude and returns valid `WhyBoardAnalysis`
- Malformed Claude responses are caught gracefully (edge case tests)
- Integration test: CSV bytes in -> WhyBoardAnalysis out

---

### Sprint 3: API Endpoints + Frontend Input (Week 3)
**Goal:** Backend endpoints live, frontend data input working, wired together.

| Story | Points | Status |
|---|---|---|
| E4-S1: `POST /api/analyze/csv` | 3 | Pending |
| E4-S2: `POST /api/analyze/paste` | 3 | Pending |
| E4-S3: CORS configuration | 1 | Pending |
| E4-S4: Clean error responses | 2 | Pending |
| E2-S1: CSV upload UI | 3 | Pending |
| E2-S2: Paste data UI | 3 | Pending |
| E5-S1: Tabbed interface | 3 | Pending |
| E5-S4: Disabled button until data present | 1 | Pending |

**Sprint 3 Total: 19 points**

**Definition of Done — Sprint 3:**
- Both `/api/analyze/csv` and `/api/analyze/paste` return valid JSON for all sample CSVs
- Frontend shows tabbed interface with CSV upload (drag-and-drop) and paste textarea
- Analyze button correctly enables/disables
- Frontend successfully calls backend and receives response
- Error cases return clean JSON (tested: empty file, oversized file, malformed data)

---

### Sprint 4: Hero UI — Narrative + Toggle + Signals (Week 4)
**Goal:** The hero feature — narrative display, toggle, signal cards, copy — fully working.

| Story | Points | Status |
|---|---|---|
| E6-S1: NarrativeView component | 3 | Pending |
| E6-S2: ModeToggle (Executive/Analyst) | 5 | Pending |
| E6-S3: SignalCards (3 cards) | 3 | Pending |
| E6-S4: Risk + Opportunity flags | 2 | Pending |
| E6-S5: CopyButton | 2 | Pending |
| E5-S2: Drag-and-drop refinement | 3 | Pending |
| E5-S5: Skeleton loader | 2 | Pending |

**Sprint 4 Total: 20 points**

**Definition of Done — Sprint 4:**
- Executive narrative displays with editorial typography
- Analyst narrative shows with data references
- Toggle animates smoothly (300ms CSS transition)
- 3 signal cards render with correct colors (green/red/muted)
- Copy button copies active narrative, shows "Copied!" for 2s
- Skeleton loader shows during AI processing
- Full flow: upload -> skeleton -> narrative + toggle + signals + copy

---

### Sprint 5: Integration, Polish & Deploy (Week 5)
**Goal:** End-to-end polished, deployed, working public URLs.

| Story | Points | Status |
|---|---|---|
| E7-S1: E2E flow validation | 5 | Pending |
| E7-S2: Desktop responsive polish | 3 | Pending |
| E7-S3: Deploy backend to Railway | 3 | Pending |
| E7-S4: Deploy frontend to Vercel | 3 | Pending |
| E7-S5: Deployed E2E verification | 2 | Pending |
| E6-S6: Error state polish | 2 | Pending |
| E3-S5: Response time < 8s validation | 3 | Pending |

**Sprint 5 Total: 21 points**

**Definition of Done — Sprint 5:**
- Full app working at public Railway + Vercel URLs
- CSV upload and paste both produce narratives in < 8 seconds
- Toggle, signals, copy all work in production
- Error states are clean and human-readable
- No console errors, no broken layouts
- **Phase 1 COMPLETE**

---

## 5. Sprint Ceremonies

| Ceremony | When | Duration | Purpose |
|---|---|---|---|
| **Sprint Planning** | Start of each sprint | 15 min | Review stories, confirm scope, identify blockers |
| **Daily Standup** | Each work session start | 5 min | What's done, what's next, blockers |
| **Sprint Review** | End of each sprint | 10 min | Demo working features, collect feedback |
| **Sprint Retro** | End of each sprint | 10 min | What worked, what didn't, improvements |

**How this works with Claude Code:**
- At the start of each sprint, I'll present the sprint backlog and confirm priorities with you
- During a sprint, I'll report progress as I complete each story
- At sprint end, I'll demo what's built and ask for your review
- You (Product Owner) accept or reject each story

---

## 6. STLC — Software Testing Life Cycle

### Test Strategy by Layer

```
┌─────────────────────────────────────────────────────────┐
│                    E2E Tests (Playwright)                │  Sprint 5
│  Full flow: upload CSV -> narrative -> toggle -> copy    │
├─────────────────────────────────────────────────────────┤
│              Integration Tests (pytest + httpx)          │  Sprint 3-4
│  API endpoint tests with real parsing + mocked Claude   │
├─────────────────────────────────────────────────────────┤
│                 Unit Tests (pytest + vitest)             │  Sprint 1-2
│  parser.py, intelligence.py, components, utils          │
└─────────────────────────────────────────────────────────┘
```

### Test Plan by Epic

| Epic | Test Type | What to Test | Tool |
|---|---|---|---|
| **E1: Scaffolding** | Smoke | Server starts, health check responds | pytest |
| **E2: Data Ingestion** | Unit | CSV parsing (valid, malformed, encodings, oversized) | pytest |
| | Unit | Paste parsing (tab, comma, mixed) | pytest |
| | Unit | DataFrame summarization (stats accuracy, sample rows) | pytest |
| | Unit | PII detection and stripping | pytest |
| | Unit | Size limit validation | pytest |
| **E3: AI Layer** | Unit | System prompt construction | pytest |
| | Unit | Response parsing (valid JSON, markdown-wrapped, malformed) | pytest |
| | Unit | Schema validation (all fields, missing fields, wrong types) | pytest |
| | Integration | Claude API call with real data (mocked in CI) | pytest |
| **E4: API Endpoints** | Integration | `/api/analyze/csv` happy path + error cases | pytest + httpx |
| | Integration | `/api/analyze/paste` happy path + error cases | pytest + httpx |
| | Integration | CORS headers present | pytest |
| **E5: Frontend Input** | Unit | DataInput tab switching | vitest + RTL |
| | Unit | File upload handler | vitest + RTL |
| | Unit | Paste textarea handler | vitest + RTL |
| | Unit | Analyze button enabled/disabled logic | vitest + RTL |
| **E6: Frontend Output** | Unit | NarrativeView renders executive/analyst text | vitest + RTL |
| | Unit | ModeToggle switches state | vitest + RTL |
| | Unit | SignalCards render 3 cards with correct colors | vitest + RTL |
| | Unit | CopyButton copies text to clipboard | vitest + RTL |
| | Visual | Skeleton loader appears during loading state | manual |
| **E7: Integration** | E2E | Full flow: upload -> narrative -> toggle -> copy | Playwright |
| | E2E | Error flow: bad file -> error message | Playwright |
| | Performance | Response time < 8 seconds | manual + timer |
| | Deployment | Health check on Railway URL | curl |

### Test Metrics & Exit Criteria

| Metric | Target |
|---|---|
| Unit test coverage (backend) | > 80% |
| Unit test coverage (frontend) | > 70% |
| Integration test pass rate | 100% |
| E2E critical path pass rate | 100% |
| AI response time (P95) | < 8 seconds |
| Zero critical/high severity bugs | Required for deploy |

### STLC Phases

```
Test Planning ──> Test Design ──> Test Environment ──> Test Execution ──> Defect Reporting ──> Test Closure
     │                 │                │                    │                  │                  │
  Sprint 1         Sprint 1-2      Sprint 1           Sprint 1-5          Ongoing           Sprint 5
  (this doc)      (write cases)   (pytest/vitest     (run every          (GitHub            (coverage
                                   configured)        sprint)            Issues)            report)
```

---

## 7. Definition of Done (Global)

A story is **Done** when ALL of the following are true:

- [ ] Code is written and follows all engineering non-negotiables from CLAUDE.md
- [ ] Unit tests written and passing
- [ ] No TypeScript `any` types
- [ ] No `requests` library usage (only `httpx`)
- [ ] No data written to disk
- [ ] No PII in logs
- [ ] Code reviewed (user acceptance)
- [ ] No lint errors
- [ ] Feature works in local development environment

---

## 8. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Claude API rate limits during development | Medium | Medium | Use response mocking for unit tests; real API only for integration |
| Claude returns inconsistent JSON format | High | Medium | Defensive parsing + retry logic + strict schema validation |
| Large CSV files cause memory issues | Medium | Low | Enforce 5 MB limit; summarize, don't send raw data |
| Tailwind + editorial typography conflict | Low | Medium | Test font rendering early in Sprint 4 |
| Railway/Vercel deployment config issues | Medium | Medium | Test deployment in Sprint 3 (not just Sprint 5) |

---

## 9. Phase 2 & 3 Backlog (Preview)

### Phase 2: Power BI Integration (Sprints 6-8)
| Epic | Stories | Est. Points |
|---|---|---|
| E8: Azure AD OAuth | Login, callback, token refresh, session management | 21 |
| E9: Power BI API | Workspaces, datasets, tables, DAX queries | 18 |
| E10: Power BI UI | Connect button, dropdown pickers, disconnect | 13 |

### Phase 3: Automation & Azure (Sprints 9-11)
| Epic | Stories | Est. Points |
|---|---|---|
| E11: Scheduled Refresh | Azure Functions, dataset refresh triggers | 15 |
| E12: Teams Notification | Webhook, message formatting, channel config | 10 |
| E13: Azure Deployment | App Service, CI/CD pipeline, per-team config | 13 |

---

## 10. Ready to Start?

**Sprint 1 is ready to begin.** The backlog is groomed, stories are estimated, and the Definition of Done is clear.

To kick off Sprint 1, say: **"Start Sprint 1"**

I'll scaffold both projects in parallel (backend + frontend), define the shared contracts, set up sample data, and have the foundation running by end of sprint.

# Frontend Rules — WhyBoard
> React 18 + TypeScript + Tailwind. Strict mode. No exceptions.

---

## Non-Negotiables

- **No `any` in TypeScript** — ever. Extend interfaces. Use generics. No shortcuts.
- **No chart libraries** — Recharts, Chart.js, D3 are banned. WhyBoard has no charts.
- **All API calls** go through `frontend/src/api/whyboard.ts` only. Never call fetch/axios inline in components.
- **Loading state** uses skeleton loader — never a spinner.
- **Error state** shows a clean message — never a stack trace or raw error object.

---

## Component Rules

### NarrativeView.tsx — The Hero Component
- Displays the active narrative (executive or analyst) based on toggle state
- Smooth fade transition between modes — 300ms, CSS transition
- Copy button always visible alongside the narrative
- Font must feel editorial — this is a reading experience, not a dashboard

### ModeToggle.tsx — Executive / Analyst Toggle
- This is the hero UX. Never degrade it.
- Toggle state lives in parent — NarrativeView receives it as prop
- Animate the switch — the narrative should feel like it's "changing perspective"
- Label clearly: "Executive" and "Analyst" — no icons replacing text

### SignalCards.tsx
- Always exactly 3 cards — never more, never less (schema enforces this)
- Each card: label, value, direction indicator (↑ ↓ →)
- Direction colors: up = green, down = red, flat = muted
- Cards appear below the narrative, not above

### CopyButton.tsx
- Copies the currently active narrative (executive or analyst) to clipboard
- Shows "Copied!" feedback for 2 seconds, then resets
- Never copies both — only the active mode

### DataInput.tsx
- Two tabs: "Upload CSV" and "Paste Data"
- CSV upload: drag-and-drop + click to browse
- Paste: textarea with monospace font, placeholder with example data
- "Analyze" button disabled until data is present

---

## TypeScript Interfaces

```typescript
// frontend/src/types/index.ts

export interface KeySignal {
  label: string;
  value: string;
  direction: 'up' | 'down' | 'flat';
}

export interface WhyBoardAnalysis {
  executive_narrative: string;
  analyst_narrative: string;
  key_signals: [KeySignal, KeySignal, KeySignal];
  risk_flag: string;
  opportunity_flag: string;
  data_type: string;
  row_count: number;
  column_count: number;
  analyzed_at: string;
}

export type NarrativeMode = 'executive' | 'analyst';

export interface AnalyzeResponse {
  success: boolean;
  analysis: WhyBoardAnalysis;
  error?: string;
}
```

---

## State Management

- No Redux, no Zustand — React `useState` and `useContext` only for this scale
- Auth state (Phase 2): single `AuthContext` wrapping the app
- Analysis result: local state in the page component, passed as props down

---

## Styling Rules

- Tailwind utility classes only — no inline styles, no CSS modules
- Dark theme as default — this is a data intelligence tool, not a consumer app
- Monospace font for any data preview or raw output
- Editorial serif or clean sans-serif for narrative text — must feel like reading an insight, not a tooltip

---

## Phase 2 Addition — PowerBIConnect.tsx

When Phase 2 starts, add this component:
- "Connect Power BI" button → triggers OAuth redirect
- After auth: shows workspace dropdown → dataset dropdown → table dropdown
- "Analyze this table" button → calls `/api/powerbi/datasets/{id}/query` → pipes to same AI layer
- Disconnect button → calls `/api/auth/logout` → clears session
- Never show the OAuth token in the UI — not even in dev tools network tab (backend handles tokens)

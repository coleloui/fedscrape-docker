# Claude Code Prompt — FedScrape Frontend

---

## Context

I have a FastAPI backend called FedScrape that serves Federal Reserve H.15
interest rate data. The backend is live at:

**`https://fed-scrape-api.up.railway.app`**

Full API docs are at `https://fed-scrape-api.up.railway.app/docs` — fetch
them before writing any data-fetching code so you have the exact response
shapes. Also fetch `https://fed-scrape-api.up.railway.app/rates/latest` to
see the actual field names in use (they may differ slightly from the original
plan — use what the live API returns, not assumed names).

---

## Tech stack

- **Vite + React + TypeScript** — `npm create vite@latest fedscrape-ui -- --template react-ts`
- **Tailwind CSS** — utility styling
- **shadcn/ui** — component library (`npx shadcn@latest init` after Tailwind)
- **Recharts** — all charts and time series visualizations
- **TanStack Query (React Query)** — all API data fetching, caching, loading states
- **React Router v6** — page routing
- **date-fns** — date formatting

Do NOT use any other charting libraries. Do NOT use axios — use native `fetch`
wrapped in React Query query functions.

---

## Project structure

Create this as `fedscrape-ui/` in the same repo root as the existing backend:

```
fedscrape-ui/
├── src/
│   ├── api/
│   │   └── client.ts          # typed fetch wrappers for every endpoint
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── Layout.tsx
│   │   ├── charts/
│   │   │   ├── RateSeriesChart.tsx   # reusable time series line chart
│   │   │   └── SpreadChart.tsx       # area chart for spread visualization
│   │   └── ui/                # shadcn components live here
│   ├── pages/
│   │   ├── Dashboard.tsx      # main landing page
│   │   ├── Explorer.tsx       # rate series explorer
│   │   ├── YieldCurve.tsx     # yield curve page
│   │   └── Chat.tsx           # GenAI chat interface
│   ├── hooks/
│   │   └── useRates.ts        # React Query hooks wrapping api/client.ts
│   ├── lib/
│   │   └── queryKeys.ts       # all React Query key constants
│   ├── types/
│   │   └── rates.ts           # TypeScript interfaces matching API responses
│   └── main.tsx
├── .env.example
└── README.md
```

---

## Pages to build

### 1. Dashboard (`/`)

The main landing page. Clean financial data dashboard aesthetic.

**Top section — Key Rate Cards**
Display the latest value for these rates as stat cards in a row.
Use the actual field names from the live `/rates/latest` response:
- Federal Funds Rate
- 2-Year Treasury
- 10-Year Treasury
- 30-Year Treasury
- Bank Prime Loan

Each card shows: rate name, current value formatted as `X.XX%`, and the date.
Fetch from `GET /rates/latest`.

**Middle section — Yield Curve Snapshot**
A bar chart showing the current yield curve shape across all Treasury
maturities in order from shortest to longest duration.
Color bars red if the short end (3-month) yield is higher than the long
end (10-year) — indicating inversion — otherwise use blue/slate.

**Bottom section — Fed Funds Rate (1 year)**
Line chart of the Fed Funds rate over the past 365 days.
Fetch from `GET /rates/federal_funds?limit=365` (use the correct field
name from the live API).

---

### 2. Rate Explorer (`/explorer`)

A flexible time series explorer. The user can:
- Select any rate type from a dropdown (populated from `GET /rates/types`)
- Set start and end dates with date pickers
- See the time series as a Recharts line chart
- See a summary card: min, max, and average for the selected period

Chart requirements:
- Tooltip showing date + value on hover
- Y-axis auto-scales to data range with small padding
- Null values create gaps in the line, not connections across

---

### 3. Yield Curve (`/yield-curve`)

**Top — Current spread badge**
Show the 10y-2y spread prominently with a badge: green if positive,
red if negative (inverted). Fetch from `GET /rates/spread?a=tnote_10y&b=tnote_2y`
(verify exact field names against live API).

**Main chart — Yield curve shape over time**
Multi-line Recharts chart showing the yield curve at 3 time slices:
latest, 1 year ago, 2 years ago. Each line plots maturities from
1-month to 30-year as X axis, yield as Y axis.

**Below — 10y-2y spread history**
Line chart of the spread over the past 2 years, computed client-side
by zipping two rate series. Shade area below zero red to highlight
inversion periods.

---

### 4. Chat (`/chat`)

A conversational interface powered by the live `POST /chat` endpoint.
This is the GenAI feature — users can ask natural language questions
about Fed rate data and get data-backed answers.

**Layout:**
- Full-height chat panel
- Message history displayed top to bottom
- User messages right-aligned, assistant messages left-aligned
- Input box pinned to bottom with Send button

**Behavior:**
- Maintain full conversation history in React state
- On each send, POST the full messages array to `/chat`
- Show a loading indicator while waiting for response
- Display `tool_calls_made` count as a subtle badge on assistant
  messages (e.g. "Used 2 tools") so users can see the AI fetched
  real data to answer
- Handle errors gracefully with an error message in the chat

**Request format:**
```typescript
POST /chat
{
  "messages": [
    { "role": "user", "content": "What is the current Fed Funds rate?" },
    { "role": "assistant", "content": "The current Fed Funds rate is..." },
    { "role": "user", "content": "How does that compare to last year?" }
  ]
}
```

**Suggested starter prompts** displayed when chat is empty:
- "What is the current Federal Funds rate?"
- "Is the yield curve currently inverted?"
- "How have 10-year Treasury yields trended over the past year?"
- "What was the average Fed Funds rate in 2024?"

---

## API client (`src/api/client.ts`)

Fetch the live API docs first, then write typed functions. All functions:
- Accept typed parameters
- Return typed responses matching `src/types/rates.ts`
- Throw on non-2xx with a useful error message

```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "https://fed-scrape-api.up.railway.app";

export async function getLatestRates(): Promise<RateSnapshot> { ... }
export async function getRateTypes(): Promise<RateTypesResponse> { ... }
export async function getRateSeries(rateType: string, params: SeriesParams): Promise<RateSeriesResponse> { ... }
export async function getRateAverage(rateType: string, params: DateRangeParams): Promise<RateAverageResponse> { ... }
export async function getSpread(a: string, b: string, date?: string): Promise<RateSpreadResponse> { ... }
export async function getRates(params: PaginatedParams): Promise<PaginatedRatesResponse> { ... }
export async function sendChatMessage(messages: Message[]): Promise<ChatResponse> { ... }
```

---

## Design direction

- Dark background (`zinc-950`) with card surfaces at `zinc-900`
- Single blue accent: `blue-400` / `blue-500` for interactive elements and primary chart lines
- Monospaced numbers for all rate values (`font-mono` on `%` values)
- Recharts theme: `zinc-700` grid lines, `zinc-400` axis text, transparent chart backgrounds
- Spread indicators: `red-400` negative, `green-400` positive
- Chat: user bubble `blue-600`, assistant bubble `zinc-800`
- Flat, data-forward aesthetic — no decorative gradients

---

## Implementation notes

- All React Query keys in `src/lib/queryKeys.ts`
- `staleTime` of 5 minutes on all rate queries (data refreshes once daily)
- `staleTime` of 0 on chat (never cache)
- Loading states: shadcn `Skeleton` components matching content layout
- Error states: error card with message, never a blank screen
- Format all rate values to 2 decimal places with `%` suffix
- Format all dates as `MMM DD, YYYY` using date-fns
- `VITE_API_BASE_URL` is the only environment variable needed

---

## `.env.example`

```
VITE_API_BASE_URL=https://fed-scrape-api.up.railway.app
```

---

## `fedscrape-ui/README.md`

Include:
- `npm install`
- `cp .env.example .env`
- `npm run dev`
- Note: backend must be running at `VITE_API_BASE_URL`
- Note: the chat feature requires a valid LLM API key on the backend

---

## What to deliver

1. Complete working Vite project in `fedscrape-ui/` in the repo root
2. All 4 pages functional and routing correctly
3. Chat page wired to the live `/chat` endpoint
4. `.env.example` and `README.md` in `fedscrape-ui/`

---

## First step

Before writing any code, fetch these two URLs and read the responses:
1. `https://fed-scrape-api.up.railway.app/openapi.json` — full API schema
2. `https://fed-scrape-api.up.railway.app/rates/latest` — actual field names

Use the real field names from those responses in all TypeScript types and
API client functions. Do not assume field names from this prompt.

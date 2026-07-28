# Frontend (`fedscrape-ui`)

Vite + React 19 + TypeScript, Tailwind CSS v4, shadcn/ui, Recharts,
TanStack Query, React Router v7, date-fns, react-markdown. Standalone app
in `fedscrape-ui/` at the repo root — not a monorepo workspace, just a
sibling directory to the Python backend.

## Setup

Requires **Node 22** (`fedscrape-ui/.nvmrc`) — Vite 6, eslint 9, and the
shadcn CLI expect Node ≥20, and misbehave or refuse to install under
Node 18. If you're on an older system Node, use nvm scoped to this
project rather than changing the system default (other tools may depend
on it).

```sh
cd fedscrape-ui
npm install
cp .env.example .env
npm run dev
```

## Directory structure

```
fedscrape-ui/src/
├── api/
│   ├── generated/       # typed client, DO NOT hand-edit — see api-generation.md
│   └── config.ts        # hand-written: sets the runtime base URL
├── components/
│   ├── ui/               # shadcn components
│   ├── layout/            # Navbar, Footer, Layout (route shell)
│   ├── charts/            # RateSeriesChart, SpreadChart (Recharts wrappers)
│   ├── chat/              # ChatMessage, DisclaimerBanner
│   └── RateCard.tsx
├── hooks/
│   └── useRates.ts        # all React Query hooks
├── lib/
│   ├── queryKeys.ts        # React Query key constants
│   ├── formatters.ts        # rate value parsing + date/percent formatting
│   └── utils.ts              # shadcn's cn() helper
├── pages/
│   ├── Dashboard.tsx, Explorer.tsx, YieldCurve.tsx, Chat.tsx
├── types/
│   └── rates.ts             # re-exports generated types under a stable path
└── App.tsx                    # BrowserRouter + route table
```

## Theming — everything traces back to `index.css`

There are **no hardcoded hex colors** anywhere outside `src/index.css`.
Every color used anywhere in the app — Tailwind utility classes,
Recharts SVG props, the chat disclaimer banner — resolves to a CSS custom
property defined once in the `:root`/`.dark` blocks there. This is a
deliberate, explicit project convention (raised directly by the project
owner), not a default shadcn pattern — don't reintroduce bare hex values
in new components.

Concretely:

- Standard shadcn tokens (`--color-background`, `--color-card`,
  `--color-primary`, `--color-muted-foreground`, etc.) — use as Tailwind
  classes (`bg-background`, `text-primary`, ...).
- `--color-chart-*` tokens (`chart-grid`, `chart-axis`, `chart-line`,
  `chart-positive`, `chart-negative`, `chart-positive-fill`,
  `chart-negative-fill`, `chart-reference`) exist **specifically** because
  Recharts' SVG props (`stroke`, `fill`) can't consume Tailwind utility
  classes — they take literal CSS values. Reference them as
  `var(--color-chart-line)` etc. directly in chart component JSX, never
  as a bare hex fallback.
- `--color-warning`/`--color-warning-foreground`/`--color-warning-border`
  — the amber-equivalent tokens for the chat page's financial disclaimer
  banner. Same rule: if you need a new semantic color anywhere, add a
  named token to `index.css` first, then consume it — don't drop hex or
  raw Tailwind palette classes (`amber-500`, etc.) directly into a
  component.

The app is **dark-only** — `:root` and `.dark` are identical, there's no
light/dark toggle. This was a deliberate choice (a flat, data-forward
financial-dashboard aesthetic), not an oversight.

## Places the original build spec and the live backend disagreed

The frontend was originally built from a spec document that predated the
real backend schema in a few places. That document has since been
removed (its job was done once the frontend existed), but the deviations
it caused are still real and worth knowing if you're extending these
pages — the live API is always the source of truth, check `/openapi.json`
fresh rather than assuming any written spec is current:

- `/rates/spread` takes `rate_a`/`rate_b` query params, not `a`/`b`.
- `/rates/{rate_type}/average` takes `?days=N` (a trailing window), not
  `start`/`end` dates.
- `/rates/{rate_type}` caps `limit` at 365 server-side — there is no way
  to request a 2-year trailing series in one call. The Yield Curve page's
  "spread history" chart covers 1 year for this reason, and the "yield
  curve shape over time" chart only plots the latest curve (no
  1-year-ago/2-years-ago slices) because the API has no point-in-time
  historical lookup, only trailing series from today.
- There's no date-picker UI on the Explorer page — the backend has
  nothing to filter by explicit start/end dates, only a trailing `limit`,
  so Explorer exposes a "last N days" dropdown instead.

## Testing

No automated frontend test suite exists yet (see
[testing.md](testing.md)). Verify changes with `npm run build` (typecheck
+ production bundle) and manual/headless browser checks against the live
backend before committing anything nontrivial.

## Pre-commit

See [git-hooks.md](git-hooks.md) — prettier + eslint run automatically on
staged `.ts`/`.tsx` files, `tsc -b` blocks the commit on type errors. Runs
from the repo-root hook, not a `fedscrape-ui`-local one.

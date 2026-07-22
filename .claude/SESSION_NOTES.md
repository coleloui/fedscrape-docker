# Session Notes — Frontend Build & Claude Docs

Working doc for the in-progress task: build the FedScrape frontend and port
pineframe's dev-tooling patterns into this repo's Claude docs. Update this
file as steps complete so a new session (or terminated/resumed one) can pick
up without re-deriving context. Delete this file once the whole task ships.

## Picking this up on Windows

Everything below was done from WSL. To continue from Windows:

1. `git pull` — `fedscrape-ui/`, `.claude/` (this file + `claude.md` +
   `architecture.md`), and `frontend_prompt.md` are now committed and
   pushed (see commit `<fill in after commit>` below once made).
2. **Node version**: `fedscrape-ui/` needs Node 22 (`fedscrape-ui/.nvmrc`).
   If Windows has an older Node, either install nvm-windows and `nvm use`,
   or install Node 22 directly — Vite 6 / eslint 9 / the shadcn CLI warn
   or misbehave under Node 18.
3. `cd fedscrape-ui && npm install` — `node_modules` isn't committed.
   `src/api/generated/` (the typed API client) IS committed, so this step
   doesn't require the backend to be reachable, but re-run
   `npm run generate:api` if you want the freshest schema.
4. `cp .env.example .env` then `npm run dev` to confirm it boots.
5. Continue from "Status" below — plumbing is done, pages are not built yet.

## Goal

1. Add missing backend endpoints the frontend needs.
2. Build `fedscrape-ui/` per `frontend_prompt.md`.
3. Port pineframe patterns: repo-wide pre-commit lint hook (Python: Ruff +
   Pyright; frontend: eslint/prettier via husky+lint-staged or equivalent),
   and a `generate-api.js`-style script for typed API client generation.
4. Fill in the docs already linked from `.claude/claude.md` but not yet
   written: `backend.md`, `database.md`, `testing.md`, `api-generation.md`,
   `git-hooks.md`, plus a new `frontend.md`.

## Status

- [x] `GET /rates/types` and `GET /rates/{rate_type}/average` added to
      `api/routes/rates.py`. Commits `e94566c` (`.gitattributes` LF fix) and
      `154e85d` (the endpoints), pushed to `origin/main` and confirmed live
      on Railway.
- [x] Fixed `slug_to_display()` casing bug (multi-digit maturities like
      "10y" stayed lowercase) and added proper Pydantic `response_model`s
      (`RateTypesResponse`, `RateAverageResponse`) so the two new endpoints
      get typed OpenAPI schemas instead of `{}`. Commit `cf21558`, pushed
      to `origin/main`.
- [x] WSL now has direct SSH push/fetch access to the personal GitHub
      account — see "Known gotchas" below. No more Windows-only pushing.
- [x] Fetched `https://fed-scrape-api.up.railway.app/openapi.json` and
      `/rates/latest` and confirmed real field names/shapes. Notes:
      - All rate values are `Optional[str]` (not float) — the scraper
        stores raw strings including `"n.a."` for missing data, so the
        frontend must parse/guard, not assume numeric.
      - `RateResponse` (from `/rates/latest`) has ~30 individual optional
        string fields, one per rate type, plus `date`.
      - `RateSeriesResponse` = `{ rate_type: str, data: [{date, value}] }`.
      - `SpreadResponse` = `{ date, rate_a, rate_b, spread: float }` — note
        query params are `rate_a`/`rate_b`, NOT `a`/`b` as
        `frontend_prompt.md` assumed.
      - `RateTypesResponse` = `{ rate_types: { slug: display_name } }`.
      - `RateAverageResponse` = `{ rate_type, display_name, days, average }`
        — note this is `?days=N` (trailing window), NOT `start`/`end` dates
        as `frontend_prompt.md` assumed. Update the frontend plan/types
        accordingly when building `src/api/client.ts`.
      - `ChatRequest.messages[].role` is restricted to `"user" | "assistant"`
        only (no `"system"`).
      - Full schema saved at
        `/tmp/claude-1000/.../scratchpad/openapi_pretty.json` in the prior
        session — re-fetch if that's gone; it's scratch, not persisted.
- [x] Scaffolded `fedscrape-ui/` (Vite + React 19 + TS, Tailwind v4,
      shadcn/ui, Recharts, TanStack Query, React Router v7, date-fns).
      Used `npm create vite@6` (not `@latest`) because `create-vite@9`
      requires Node ≥20.19 and WSL's system Node was 18 at scaffold time.
      Installed nvm and Node 22 for this project specifically (system
      Node left untouched at 18 — don't `nvm alias default`, other tools
      like claude-code itself depend on system Node). `fedscrape-ui/.nvmrc`
      pins `22`.
- [x] `vite.config.ts`: added `@tailwindcss/vite` plugin and `@` →
      `./src` path alias (matches pineframe's `services/client` convention).
      Same alias added to `tsconfig.app.json`.
- [x] `shadcn init` run with `-d` (all defaults) — generated its own
      default theme (grayscale + Geist font via `@fontsource-variable/geist`)
      rather than reusing pineframe's manually-tuned theme, since fedscrape
      needs its own dark financial-dashboard palette per `frontend_prompt.md`
      (zinc-950/zinc-900, blue-400/blue-500 accent) — **not yet applied,
      still on shadcn's grayscale default**. Added components: card,
      skeleton, badge, input, label, select.
- [x] eslint.config.js + .prettierrc added, matching pineframe's rules
      (react-hooks, jsx-a11y, no-console warn, etc.) — one deliberate
      difference: `"semi": false` in prettier (pineframe uses `true`),
      chosen to match what the Vite/shadcn scaffolding already generated
      rather than reformat everything.
- [x] `scripts/generate-api.js` — adapted from pineframe's version but
      simplified (fedscrape has one backend, not pineframe's multi-service
      `api-config.json` setup). Uses `@hey-api/openapi-ts` against
      `${VITE_API_BASE_URL}/openapi.json`. Verified working end-to-end
      against the live Railway backend — generates
      `src/api/generated/{client,sdk,types}.gen.ts` with full types for
      all 8 endpoints. Run via `npm run generate:api`.
      **Decision: this generated output IS committed to git** (matches
      pineframe's approach for `services/client/src/api/core-api`) so
      `npm run build` never depends on the live backend being reachable.
- [x] `src/api/config.ts` (hand-written, not generated) calls
      `client.setConfig({ baseUrl: import.meta.env.VITE_API_BASE_URL ||
      '<railway-url>' })` — same pattern as pineframe's `api/config.ts`.
      Imported once in `main.tsx` before first use.
- [x] `main.tsx` wired with `QueryClientProvider` (new `QueryClient()`,
      default options untouched — spec calls for 5min staleTime on rate
      queries specifically, not global, so that belongs on individual
      query hooks later, not here).
- [x] `.env.example` and `README.md` written for `fedscrape-ui/`.
- [ ] **NOT DONE**: `App.tsx` still has Vite's boilerplate counter demo.
      No router, no layout, no pages, no `src/pages/`, `src/hooks/`,
      `src/types/`, `src/components/layout/`, `src/components/charts/`
      directories yet. This is the next real chunk of work — build the 4
      pages (Dashboard, Explorer, Yield Curve, Chat) per `frontend_prompt.md`,
      adjusted for the schema deltas noted above (`rate_a`/`rate_b` not
      `a`/`b`, `?days=` not `start`/`end`).
- [ ] Custom Tailwind theme colors (zinc-950/900 + blue-400/500 palette)
      not yet applied — still shadcn's grayscale default.
- [ ] Add repo-wide pre-commit hook: Ruff + Pyright for Python (not
      currently configured despite `.claude/claude.md` claiming it is —
      no `.pre-commit-config.yaml`, no ruff/pyright in `pyproject.toml`
      deps), plus husky + lint-staged wired to `fedscrape-ui`'s
      lint/format/typecheck scripts (pineframe's root `package.json`
      `lint-staged` config is the template — see there for the exact
      prettier→eslint→tsc chain).
- [ ] Write `.claude/backend.md`, `database.md`, `testing.md`,
      `api-generation.md`, `git-hooks.md`, `frontend.md`.

## Known gotchas (don't rediscover these)

- `db/models.py` has no `RATE_COLUMNS` — only `RATE_TYPES` (flat slug list)
  and `SCRAPE_COLUMN_MAP` (scraper header → slug). Display names for
  `/rates/types` are generated via a `slug_to_display()` helper in
  `api/routes/rates.py`, not stored data.
- `db/crud.py`'s `get_average()` takes `days: int` (trailing window), not
  `start`/`end` — `/rates/{rate_type}/average` matches that: `?days=30`.
- Route ordering matters: `/types` and `/{rate_type}/average` must stay
  registered before the catch-all `GET /{rate_type}` in `rates.py`, or
  FastAPI will treat "types"/"average" as a `rate_type` value.
- Repo was showing whole-file CRLF/LF diff noise on every tracked file due
  to Windows checkout. Fixed via `.gitattributes` (LF-enforced) + `git add
  --renormalize .` — already resolved, shouldn't resurface, but if it does,
  don't use `git rm --cached -r .` + `reset --hard` (unnecessarily
  destructive); `--renormalize` is sufficient and safe.
- WSL now has a dedicated SSH key (`~/.ssh/id_ed25519_personal`) registered
  on the personal GitHub account (`coleloui`), with `~/.ssh/config` pinning
  it as the default identity for `github.com`. Push/fetch work directly
  from WSL now — no more routing through Windows.
- `npm audit` on `fedscrape-ui` reports 3 moderate + 4 high findings. All
  are transitive dev-only tooling deps (shadcn CLI's bundled MCP server →
  `@hono/node-server` path-traversal, Windows-only; `@hey-api/openapi-ts`'s
  YAML parser → `js-yaml` quadratic-CPU DoS, only triggers on YAML specs
  and fedscrape serves JSON). Neither ships in the built app. Investigated
  and consciously left as-is rather than forcing `npm audit fix --force`
  breaking-change downgrades of `shadcn`/`@hey-api/openapi-ts` — re-check
  if `npm audit` surfaces something new, don't just re-suppress this one.
- Two Node versions are now in play in WSL: system Node stays at 18.19.1
  (`/usr/bin/node`, used by claude-code and other global tools — do not
  change this), and nvm has Node 22.23.1 installed separately, activated
  per-shell via `export NVM_DIR="$HOME/.nvm"; \. "$NVM_DIR/nvm.sh"; nvm use
  --delete-prefix v22.23.1 --silent` (the `--delete-prefix` flag works
  around this user's `~/.npmrc` having a custom `prefix`/`globalconfig`
  that otherwise conflicts with nvm). Any future WSL work in
  `fedscrape-ui/` needs that activation line first, or `node`/`npm` will
  silently fall back to system Node 18 and may hit engine-compatibility
  issues again.

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
- [x] Windows-side session (concurrent with WSL work) committed a broken
      snapshot of the frontend WIP (`5775d9b`) plus two unrelated
      chat-service backend fixes (`e9089c1`, `b57927c`, INTERNAL_API_URL /
      httpx→direct-DB refactor). Reconciled in WSL: fixed the shadcn `@/`
      literal-directory bug and the `generated` barrel import (`c832dd2`).
- [x] All 4 pages built and wired to the live backend: Dashboard,
      Explorer, Yield Curve, Chat. Layout with shared Navbar + Footer.
      React Router v7 (`BrowserRouter` in `App.tsx`). Commit `846c579`,
      pushed to `origin/main`.
- [x] Custom dark theme applied — replaced shadcn's grayscale default
      with a zinc/blue/green/red palette, defined **entirely as CSS custom
      properties in `index.css`** (no bare hex anywhere else in the
      codebase, per explicit user preference). Added `--color-chart-*`
      tokens specifically because Recharts SVG props (`stroke`/`fill`)
      can't consume Tailwind utility classes — chart components reference
      `var(--color-chart-line)` etc. instead. Also added `--color-warning*`
      tokens for the chat disclaimer banner. `:root` and `.dark` are
      identical (app is dark-only, no light/dark toggle).
- [x] Chat page requirements (user-specified, not in original
      `frontend_prompt.md`): amber warning banner above message history,
      matching disclaimer in the footer on every page (smaller/neutral
      styling, not amber), pre-populated welcome assistant message on
      load, and `react-markdown` + `remark-gfm` (+ `@tailwindcss/typography`
      for `prose` styling) rendering assistant messages so markdown
      tables/headers/bold render properly instead of showing raw syntax.
      Verified end-to-end with a real chat round-trip — backend returned
      a markdown table that rendered correctly.
- [x] Explorer page deviates from `frontend_prompt.md`'s "start/end date
      pickers" — the backend's `/rates/{rate_type}` only supports a
      trailing `limit` (number of records), not arbitrary date-range
      filtering, so Explorer exposes a "last N days" dropdown (30/90/180/
      365) instead of fabricating date-picker UI the API can't actually
      serve. Same constraint applies anywhere else a date range might
      seem natural — check the OpenAPI schema's query params before
      building date-picker UI.
- [x] Yield Curve's "shape over time" chart shows the latest curve only,
      not latest/1yr-ago/2yr-ago as `frontend_prompt.md` asked — the API
      has no point-in-time lookup (only trailing series from today), so
      the 1yr/2yr-ago slices can't be computed from what's exposed.
      Documented inline in `CurveShapeChart`'s comment.
- [x] Fixed a real bug caught by headless testing (not by tsc/eslint):
      Yield Curve's spread-history chart requested `limit=730` but
      `/rates/{rate_type}` caps `limit` at 365 server-side → 422s. Fixed
      to `SPREAD_HISTORY_DAYS = 365`, card title changed from "(2 Years)"
      to "(1 Year)" to match. This class of bug (query params exceeding
      backend-declared limits) won't show up in typecheck/lint — worth
      an actual network-level check when adding new date-range queries.
- [x] Verified via `tsc -b`, `eslint`, `npm run build` (production build
      succeeds, ~325kB gzipped main chunk — large-chunk warning noted but
      not addressed, code-splitting would be the fix if it matters later),
      and headless Playwright checks (installed ad hoc in the scratchpad
      dir, not a project dependency) against all 4 routes with the live
      backend — zero console errors, real data rendering.
- [x] Ruff added (not Pyright — user explicitly said don't touch Pyright;
      555 strict-mode findings are mostly missing-stub noise from pytest
      fixtures, not real bugs, address incrementally later instead of in
      a bulk pass). `[tool.ruff]` in `pyproject.toml`: `line-length = 88`,
      `select = ["E", "F", "I"]`. Ran `ruff check --fix` once (86 findings,
      74 auto-fixed — mostly unused imports / import sorting; 16 remaining
      `E501` line-length violations left untouched, not auto-fixable
      safely). Added `ruff check .` as a CI step in `.github/workflows/ci.yml`
      before the pytest step. Commit `be6d4ea`, pushed.
- [x] Alembic was scaffolded (`db/alembic/`, baseline migration for
      `RateRecord`) then **fully reverted** per explicit instruction — user
      wants `init_db()`'s `create_all()` to stay as the source of truth
      until the schema needs to change or before launch, since there are
      no production users yet and no untested deploy-time changes are
      wanted right now. Added a TODO comment in `api/main.py`'s
      `lifespan()` marking the future switch (Railway release command:
      `alembic upgrade head`). Commit `b4e17bf`, pushed. **Do not
      re-introduce Alembic without being asked again** — this was tried
      once and explicitly undone.
- [x] Repo-wide pre-commit hook added: husky + lint-staged at repo root
      (new root `package.json`, `.husky/pre-commit` runs `npx lint-staged`).
      Config covers `fedscrape-ui/src/**/*.{js,jsx,ts,tsx}` (prettier +
      eslint --fix), `fedscrape-ui/**/*.{json,css,md}` (prettier), 
      `fedscrape-ui/src/**/*.{ts,tsx}` (tsc -b, no-emit typecheck), and
      root `*.py` (`ruff check --fix`). Adapted from pineframe's root
      `package.json` lint-staged block, but npm not pnpm, and no
      `postinstall` chain since Python deps aren't npm-managed.
      **Caveat**: the `*.py` rule assumes `ruff` is on PATH, i.e. the
      committer's Python venv is active — no PATH-detection fallback was
      added (user's ruff-only instructions didn't ask for one; documented
      as a requirement in git-hooks.md instead). Verified working
      end-to-end with a real test commit (deliberately unsorted/unused
      import got auto-fixed by the hook before the commit landed), then
      the test commit was `git reset --hard` off since it was scratch —
      the real hook-setup commit (`81d437a`) stayed. Added `/node_modules/`
      to root `.gitignore` (wasn't there before — root had no Node tooling
      until this).
- [x] Wrote `.claude/backend.md`, `database.md`, `testing.md`,
      `api-generation.md`, `git-hooks.md`, `frontend.md` — all grounded in
      the real code (read the actual files, not guessed). Also did a full
      accuracy pass on the two pre-existing docs: `claude.md` (fixed
      claims about Alembic/Pyright pre-commit that were never true) and
      `architecture.md` (directory tree had wrong paths — `db/database.py`
      instead of `db/session.py`, `db/models/` instead of `db/models.py`,
      `test_api.py`/`test_scraper.py` that don't exist; the entire "Key
      Patterns" → "Docker Patterns" section, ~290 lines, was fictional
      example code — `RateService`/`RateRepository` classes, an
      `InterestRate` model, a `cache.cached()` decorator, TaskIQ, none of
      which exist — replaced with descriptions of the real patterns).
- [x] **Public-facing docs reframed around the live Railway deployment,
      not local self-hosting** — user does not want this repo (public on
      GitHub) inviting others to run/redeploy it. Added a `LICENSE` file
      (all-rights-reserved, explicit "viewing is fine, running/forking
      for deployment is not"). `ReadMe.md` rewritten around the live URL
      (`https://fed-scrape-api.up.railway.app`) instead of docker-compose
      setup instructions; also fixed a stale/fictional `GET /rates`
      endpoint listing. `DEPLOYMENT.md`'s "Local development" section and
      Docker Desktop prerequisite removed, retitled "Deployment
      *Reference*" (documents how the live deployment is configured, not
      a self-hosting guide), added `/rates/types` and
      `/rates/{rate_type}/average` to its endpoint table (were missing),
      and added a real `/chat` example — verified against the actual live
      response rather than fabricated (the model's true response is a
      markdown table, not plain prose — worth remembering if writing
      chat examples elsewhere: **always curl the real endpoint first**.
      **Scope boundary**: this reframing applies to public-facing docs
      only (`ReadMe.md`, `DEPLOYMENT.md`). The `.claude/*.md` docs
      (including this file) keep local-dev references (`npm run dev`,
      `localhost:8000` fallback defaults) — those are working notes for
      Claude Code sessions and the project owner, not public setup
      instructions, and the user explicitly confirmed they should stay
      as-is.
      `docker-compose.yml`/`Dockerfile` themselves were **not** touched —
      `docker-compose.yml` is inert w.r.t. Railway (railway.toml points
      straight at the Dockerfile) and stays as the owner's own local-dev
      convenience; `Dockerfile` is load-bearing for the real Railway build.
- [x] Deleted `frontend_prompt.md` (its job — spec for building the
      frontend — was done). Fixed the one place a `.claude/*.md` doc
      pointed at it (`frontend.md`); left references in code comments
      (`YieldCurve.tsx`) and this file's own history alone since those
      are explaining past decisions, not pointing readers to a file that
      needs to exist.

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

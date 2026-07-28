# API Client Generation

`fedscrape-ui` never hand-writes fetch wrappers or response types for the
backend. Everything under `fedscrape-ui/src/api/generated/` is generated
from the backend's live OpenAPI schema via
[`@hey-api/openapi-ts`](https://heyapi.dev/), adapted from the same
`generate-api.js` pattern pineframe uses in `services/client/`.

## Running it

```sh
cd fedscrape-ui
npm run generate:api
```

This hits `${VITE_API_BASE_URL}/openapi.json` (defaults to
`http://localhost:8000` if unset — **not** the live Railway URL, so set
`VITE_API_BASE_URL` explicitly to regenerate against production):

```sh
VITE_API_BASE_URL=https://fed-scrape-api.up.railway.app npm run generate:api
```

The backend must actually be running and reachable at that URL — the
script fails loudly (non-zero exit, clear error message) rather than
silently producing a stale/empty client if it can't reach the schema
endpoint.

## What gets generated

`src/api/generated/` contains `client.gen.ts` (the fetch-based HTTP
client), `sdk.gen.ts` (one typed function per operation, e.g.
`rateAverageRatesRateTypeAverageGet`), and `types.gen.ts` (every request/
response shape, generated straight from the OpenAPI component schemas —
`RateResponse`, `RateSeriesResponse`, `ChatRequest`, etc.). Function names
are auto-derived from the FastAPI route's operation ID
(`{handler_name}_{path}_{method}`) — they're verbose and not something
you'd hand-write, but they're stable as long as the backend route
function names don't change.

**This generated output is committed to git**, matching pineframe's
`services/client/src/api/core-api` convention — `npm run build` (and any
future CI) should never depend on the live backend being reachable just
to typecheck or bundle. Regenerate and commit the diff whenever the
backend's API surface changes; don't hand-edit anything under
`generated/`, since it'll be silently overwritten on the next run.

## Wiring the base URL at runtime

The generated `client.gen.ts` hardcodes whatever `baseUrl` was live in the
OpenAPI schema at generation time (currently the Railway URL) — that's
fine for the generation step, but wrong for e.g. local dev against
`localhost:8000`. `src/api/config.ts` (hand-written, never regenerated)
overrides this once at app startup:

```typescript
import { client } from './generated/client.gen'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://fed-scrape-api.up.railway.app'

client.setConfig({ baseUrl: API_BASE_URL, throwOnError: true })
```

`main.tsx` imports `./api/config` once, before anything else touches the
API client, purely for this side effect (`import './api/config'` — no
named imports needed).

## Prerequisite: every endpoint needs a real `response_model`

`@hey-api/openapi-ts` derives types straight from the OpenAPI component
schemas FastAPI publishes. A route that returns a bare `dict` without a
`response_model=` produces an **empty `{}` schema** in `/openapi.json` —
the generated client function still exists, but its return type is
untyped (`unknown`/`any`), defeating the entire point of codegen. See
[backend.md](backend.md)'s route pattern section: always back a route
with a real Pydantic `BaseModel` in `api/models/`, even for endpoints that
conceptually "just return a dict" (`RateTypesResponse`,
`RateAverageResponse` were added specifically to fix this for two
endpoints that initially shipped without one).

## Query-param constraints matter for the frontend too

FastAPI's `Query(..., le=365)`-style constraints show up in the generated
OpenAPI schema and are enforced server-side with a `422` — but nothing on
the frontend prevents you from calling a generated SDK function with a
value that violates them. There's no client-side validation layer here.
Before wiring up a new date-range or limit-style query param on the
frontend, check the backend's actual `Query(...)` bounds in the relevant
route (`api/routes/rates.py`) rather than assuming a value like "2 years"
is safe — a previous pass hardcoded `limit=730` for a "2 year" spread
history chart when the backend caps `limit` at `365`, which 422'd
silently until caught by a headless browser check (not by `tsc`/`eslint`,
which have no way to know about runtime query constraints).

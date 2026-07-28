# Backend Patterns

FastAPI + SQLModel backend serving Federal Reserve H.15 interest rate data,
plus a Claude-powered chat endpoint. See [architecture.md](architecture.md)
for the overall layer breakdown.

## Route pattern

Routes live in `api/routes/`, one file per resource, each with its own
`APIRouter(prefix=..., tags=[...])`. Every route:

- Takes `request: Request` as the first parameter — required by
  `@limiter.limit(...)` (slowapi reads the request to key rate limits).
- Declares `response_model=` for anything with a real Pydantic/SQLModel
  shape. Endpoints returning a plain `dict` (e.g. `/rates/types`) still get
  a `response_model` backed by a dedicated response class in
  `api/models/rate.py` — a bare dict return produces an empty `{}` schema
  in the generated OpenAPI doc, which breaks typed client codegen for the
  frontend (see [api-generation.md](api-generation.md)). Always add the
  response model, even for endpoints that "just return a dict".
- Validates path/query params against `db.models.RATE_TYPES` before
  touching the database, raising `HTTPException(404, ...)` for unknown
  rate-type slugs.

```python
@router.get("/{rate_type}/average", response_model=RateAverageResponse)
@limiter.limit("60/minute")
async def rate_average(
    request: Request,
    rate_type: str,
    days: int = Query(30, ge=1, le=3650, description="Trailing window size in days"),
    session: AsyncSession = Depends(get_session),
):
    if rate_type not in RATE_TYPES:
        raise HTTPException(status_code=404, detail=f"Unknown rate type: {rate_type!r}")
    average = await get_average(session, rate_type, days=days)
    return {"rate_type": rate_type, ...}
```

### Route ordering matters

FastAPI matches routes in declaration order. Static-segment routes
(`/types`, `/{rate_type}/average`) must be registered **before** the
catch-all `GET /{rate_type}` in the same router file, or FastAPI will
treat `"types"` as a `rate_type` path value and 404 on the real handler.
When adding a new static route under `/rates/`, put it above
`rate_series` in `api/routes/rates.py`.

## Service layer

`api/services/` holds business logic that doesn't belong in a route
handler: `scraper.py` (Fed H.15 HTML scraping), `chat.py` (Claude tool-use
loop), `upload.py` (S3 upload gating). Services call `db/crud.py`
functions directly — the chat service used to call its own HTTP endpoints
over `httpx` (self-calls to `localhost`), which broke on Railway (a
service can't call its own public URL, and the internal port needed
manual tracking via `INTERNAL_API_URL`). This was refactored to call
`db/crud.py` functions directly instead, which is now the standard
pattern — **new tool/service logic should query the DB layer directly,
never make an HTTP call back into this same FastAPI process.**

## Caching (`api/cache.py`)

Redis-backed, fully optional at the call site — every `cache_get`/
`cache_set`/`cache_delete_pattern` call catches its own exceptions and
logs a warning rather than propagating, so a Redis outage degrades to
"always miss" instead of 500ing requests. Cache keys are ad hoc strings
built per-route (`f"rates:series:{rate_type}:{limit}"`); there's no
central key registry. `cache_delete_pattern("rates:*")` is called after
`/rates/refresh` to invalidate everything at once — if you add a new
cached read endpoint, make sure its key falls under the `rates:*`
prefix so refresh invalidation still catches it, or add an explicit
invalidation call.

## Rate limiting (`api/limiter.py`)

`slowapi.Limiter` keyed on remote address, backed by the same Redis
instance. Disabled entirely when `APP_ENV == "test"` (see
`Settings.APP_ENV` in `api/config.py`) so the test suite doesn't get
throttled. Every route decorated with `@limiter.limit(...)` must also
accept `request: Request` — omitting it is a runtime error, not just a
lint warning.

## Configuration (`api/config.py`)

Single `Settings(BaseSettings)` class, loaded once as the module-level
`settings` singleton. All env vars have defaults suitable for local dev
(`localhost` Postgres/Redis) so the app boots without a `.env` file in
CI/tests. `PORT` vs `API_PORT`: Railway injects `$PORT` at deploy time,
`API_PORT` is the local-dev default — `PORT` is what's actually bound.

## Response models (`api/models/`)

Plain Pydantic `BaseModel`s, separate from the SQLModel table models in
`db/models.py`. `RateResponse.model_config = {"from_attributes": True}`
lets it validate directly off a `RateRecord` ORM instance
(`RateResponse.model_validate(record)`). All rate values are typed
`Optional[str]`, not `float` — the scraper stores raw strings including
the literal `"n.a."` for missing Fed data, so anything consuming these
values (frontend included) must parse defensively, never assume a valid
number.

## Adding a new endpoint — checklist

1. Add/extend a response model in `api/models/` (never return a bare
   `dict` without one — see route pattern above).
2. Add the CRUD function in `db/crud.py` if new data access is needed.
3. Add the route in the right `api/routes/*.py` file, respecting
   ordering (static paths before `{param}` catch-alls).
4. If it's cacheable, follow the existing `cache_get`/`cache_set` pattern
   with a `rates:`-prefixed key.
5. Regenerate the frontend's typed client:
   `cd fedscrape-ui && npm run generate:api` (see
   [api-generation.md](api-generation.md)) — the new endpoint won't be
   usable from the frontend until this runs.
6. Add a test in `tests/` (see [testing.md](testing.md)).

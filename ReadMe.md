# FedScrape

FastAPI + MCP server that scrapes and serves Federal Reserve H.15 interest rate data. Rates are fetched from the Fed's published release, stored in PostgreSQL, and exposed via a REST API, a chat interface backed by Claude, and an MCP (Model Context Protocol) server for LLM tool use.

This is a personal project, shared publicly for portfolio/reference
purposes — see [LICENSE](LICENSE). It isn't intended to be self-hosted or
redeployed by others.

## Live deployment

The API is live on Railway at:

**`https://fed-scrape-api.up.railway.app`**

Interactive docs: `https://fed-scrape-api.up.railway.app/docs`
Health check: `https://fed-scrape-api.up.railway.app/health`

## Frontend

**Live:** https://fedrate-production.up.railway.app/

`fedscrape-ui/` is a Vite + React dashboard consuming this API — see
[`fedscrape-ui/README.md`](fedscrape-ui/README.md).

## API

Key endpoints:

```
GET  /health                          Health check
GET  /rates/latest                    Most recent H.15 record
GET  /rates/types                     All rate-type slugs + display names
GET  /rates/{rate_type}                Time series for one rate type
GET  /rates/{rate_type}/average        Trailing-window average for one rate type
GET  /rates/spread                     Yield spread between two rate types
POST /chat                              Conversational interface backed by Claude + rate tools
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full endpoint reference, rate
limits, available rate-type slugs, and a `/chat` example.

## How it's deployed

See [DEPLOYMENT.md](DEPLOYMENT.md) for how the live Railway deployment is
configured (services, env vars, cron scraper schedule, CI/CD) — kept as a
reference for maintaining this specific deployment, not a self-hosting guide.

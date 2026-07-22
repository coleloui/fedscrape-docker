# fedscrape-ui

Frontend for FedScrape — Federal Reserve H.15 interest rate data.

## Stack

Vite + React + TypeScript, Tailwind CSS v4, shadcn/ui, Recharts, TanStack Query, React Router, date-fns.

## Setup

Requires Node 22 (see `.nvmrc`; run `nvm use` if you have nvm installed).

```sh
npm install
cp .env.example .env
npm run dev
```

The backend must be running and reachable at `VITE_API_BASE_URL` (defaults to the
live Railway deployment if unset). The chat feature requires the backend to have
a valid LLM API key configured.

## API client

`src/api/generated/` is a typed client generated from the backend's live OpenAPI
schema via [`@hey-api/openapi-ts`](https://heyapi.dev/). It's committed to the repo
(not gitignored) so builds don't depend on the backend being reachable, but should
be regenerated whenever the backend's API surface changes:

```sh
npm run generate:api
```

Set `VITE_API_BASE_URL` first if generating against a non-default backend (e.g. a
local instance) — the script reads that same env var.

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — typecheck and build for production
- `npm run lint` / `npm run lint:fix` — ESLint
- `npm run format` / `npm run format:check` — Prettier
- `npm run generate:api` — regenerate the typed API client from the live backend schema

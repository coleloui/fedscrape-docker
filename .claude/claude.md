# Claude Code Instructions for FedScrape

This directory contains patterns, conventions, and workflows for the FedScrape project. These instructions describe what's actually in the codebase — not an aspirational target — so they can be trusted at face value.

## Documentation Structure

- **[architecture.md](architecture.md)** - Project structure and architectural patterns
- **[backend.md](backend.md)** - Python backend patterns and conventions
- **[database.md](database.md)** - Database schema and current (migration-free) setup
- **[testing.md](testing.md)** - Testing patterns and best practices
- **[api-generation.md](api-generation.md)** - Frontend's typed API client generation workflow
- **[git-hooks.md](git-hooks.md)** - Pre-commit hooks and code quality checks
- **[frontend.md](frontend.md)** - `fedscrape-ui` structure, theming, and conventions

## Quick Start

### For New Features
1. Read [architecture.md](architecture.md) to understand project structure
2. Follow patterns in [backend.md](backend.md) for Python code, or [frontend.md](frontend.md) for `fedscrape-ui`
3. Add tests following [testing.md](testing.md)
4. If touching the API surface, regenerate the frontend client — see [api-generation.md](api-generation.md)

### For Database Changes
There is no migration framework in place right now — see
[database.md](database.md) for why and what the schema actually looks
like. Modify `db/models.py` directly; the schema is created via
`SQLModel.metadata.create_all()` on startup. **Do not set up Alembic
without being explicitly asked** — this has been tried and deliberately
reverted once already.

### Code Quality
- Pre-commit hooks run **Ruff** (auto-fix) on staged Python files, and
  Prettier + ESLint + a `tsc` typecheck on staged frontend files — see
  [git-hooks.md](git-hooks.md) for exact scope and the one caveat
  (`ruff` must be on `PATH`, i.e. your venv active, when committing).
- **Pyright is not wired into the hook or CI.** It's available to run
  manually but is not enforced — see git-hooks.md for why (mostly
  missing-stub noise in strict mode, not real bugs), and don't add it to
  the hook without discussing scope first.
- Follow the patterns documented in [backend.md](backend.md) / [frontend.md](frontend.md)

## Technology Stack

### Backend
- **FastAPI** - Web framework
- **SQLModel** - ORM with Pydantic integration
- **PostgreSQL** - Primary database (schema managed via `create_all()`, not migrations — see database.md)
- **Redis** - Caching layer
- **Typer** - CLI framework
- **Pytest** - Testing framework

### Frontend (`fedscrape-ui/`)
- **Vite + React 19 + TypeScript**
- **Tailwind CSS v4 + shadcn/ui** - all colors as CSS custom properties, no hardcoded hex (see frontend.md)
- **Recharts** - charts, colored via `var(--color-chart-*)` tokens
- **TanStack Query** - data fetching, wraps a generated typed API client (see api-generation.md)
- **React Router v7**

### Code Quality Tools
- **Ruff** - Fast Python linter, auto-fix on commit (not yet running `ruff format`)
- **ESLint + Prettier** - frontend linting/formatting, auto-fix on commit
- **Pytest** - Unit and integration testing
- **Husky + lint-staged** - repo-root pre-commit hook covering both languages

## Key Principles

1. **Match reality, not aspiration**: if a doc here describes something that isn't actually true of the code, fix the doc (or the code) rather than leaving the mismatch — a previous version of these docs described Alembic and strict-mode Pyright hooks that never existed.
2. **Testing**: All new features must include tests (see testing.md for what "tested" means given the no-local-Postgres reality).
3. **API changes require a client regen**: any backend route change needs `fedscrape-ui`'s generated client regenerated and committed (api-generation.md).
4. **Documentation**: Update these Claude docs when patterns actually change — don't let them drift back into describing intentions instead of the codebase.

## Development Workflow

1. Make code changes
2. Add/update tests
3. Regenerate the frontend API client if the backend's routes/schemas changed
4. Commit (pre-commit hooks run automatically — Ruff for Python, Prettier/ESLint/tsc for frontend)
5. Push to remote

## Getting Help

If you're working with Claude Code and need to:
- Add a new feature → Check [architecture.md](architecture.md) and [backend.md](backend.md) or [frontend.md](frontend.md)
- Understand the database setup → Check [database.md](database.md)
- Add tests → Check [testing.md](testing.md)
- Regenerate the frontend's API client → Check [api-generation.md](api-generation.md)
- Understand hooks → Check [git-hooks.md](git-hooks.md)

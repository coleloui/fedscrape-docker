# Claude Code Instructions for FedScrape

This directory contains patterns, conventions, and workflows for the FedScrape project. These instructions are adapted from production-grade patterns and designed to maintain code quality and consistency.

## Documentation Structure

- **[architecture.md](architecture.md)** - Project structure and architectural patterns
- **[backend.md](backend.md)** - Python backend patterns and conventions
- **[database.md](database.md)** - Database migration workflow and patterns
- **[testing.md](testing.md)** - Testing patterns and best practices
- **[api-generation.md](api-generation.md)** - API client generation workflow (for future frontend)
- **[git-hooks.md](git-hooks.md)** - Pre-commit hooks and code quality checks

## Quick Start

### For New Features
1. Read [architecture.md](architecture.md) to understand project structure
2. Follow patterns in [backend.md](backend.md) for Python code
3. Add tests following [testing.md](testing.md)
4. Create migrations if models change - see [database.md](database.md)

### For Database Changes
1. Modify models in `db/models/`
2. Run `alembic revision --autogenerate -m "description"`
3. Review and test the migration
4. Pre-commit hook will warn if you forget

### Code Quality
- Pre-commit hooks automatically run Ruff (linting) and Pyright (type checking)
- All Python code must pass type checking in strict mode
- Follow the patterns documented in [backend.md](backend.md)

## Technology Stack

### Backend
- **FastAPI** - Web framework
- **SQLModel** - ORM with Pydantic integration
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **Typer** - CLI framework
- **Pytest** - Testing framework

### Code Quality Tools
- **Ruff** - Fast Python linter and formatter
- **Pyright** - Static type checker
- **Pytest** - Unit and integration testing
- **Pre-commit hooks** - Automated quality checks

## Key Principles

1. **Type Safety**: All code must be fully typed (Pyright strict mode)
2. **Database Migrations**: Never modify models without creating a migration
3. **Testing**: All new features must include tests
4. **Code Quality**: Pre-commit hooks enforce linting and formatting
5. **Documentation**: Update Claude docs when patterns change

## Development Workflow

1. Make code changes
2. Add/update tests
3. Create migration if models changed
4. Commit (pre-commit hooks run automatically)
5. Push to remote

## Getting Help

If you're working with Claude Code and need to:
- Add a new feature → Check [architecture.md](architecture.md) and [backend.md](backend.md)
- Modify database → Check [database.md](database.md)
- Add tests → Check [testing.md](testing.md)
- Set up frontend → Check [api-generation.md](api-generation.md)
- Understand hooks → Check [git-hooks.md](git-hooks.md)

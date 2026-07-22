# Project Architecture

## Directory Structure

```
fedscrape-docker/
├── api/                    # FastAPI application
│   ├── __init__.py
│   ├── main.py            # FastAPI app setup
│   ├── config.py          # Configuration management
│   ├── cache.py           # Redis caching logic
│   ├── limiter.py         # Rate limiting
│   ├── models/            # Pydantic models (request/response)
│   ├── routes/            # API route handlers
│   └── services/          # Business logic layer
├── db/                    # Database layer
│   ├── __init__.py
│   ├── database.py        # Database connection and session
│   ├── models/            # SQLModel database models
│   └── alembic/           # Database migrations
├── fedscrape/             # Core scraping logic and CLI
│   ├── __init__.py
│   ├── cli.py             # Typer CLI entrypoint
│   ├── scraper.py         # Web scraping logic
│   └── mcp/               # MCP server implementation
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   ├── test_api.py        # API tests
│   └── test_scraper.py    # Scraper tests
├── .claude/               # Claude Code instructions
├── docker-compose.yml     # Container orchestration
├── Dockerfile             # Application container
├── pyproject.toml         # Python project configuration
└── README.md              # Project documentation
```

## Architectural Patterns

### Layered Architecture

The project follows a clean layered architecture:

1. **API Layer** (`api/`)
   - FastAPI routes and request/response models
   - Input validation with Pydantic
   - Dependency injection for services
   - Error handling and HTTP responses

2. **Service Layer** (`api/services/`)
   - Business logic and orchestration
   - Interacts with database layer
   - Handles caching logic
   - No direct HTTP concerns

3. **Database Layer** (`db/`)
   - SQLModel models (combines SQLAlchemy + Pydantic)
   - Database session management
   - Query logic
   - Alembic migrations

4. **Core Logic** (`fedscrape/`)
   - Domain-specific logic (web scraping)
   - CLI commands
   - MCP server
   - Independent of API layer

### Key Patterns

#### 1. Dependency Injection

Use FastAPI's dependency injection for database sessions, services, and configuration:

```python
from fastapi import Depends
from sqlmodel import Session
from api.services.rate_service import RateService
from db.database import get_session

async def get_rate_service(session: Session = Depends(get_session)) -> RateService:
    return RateService(session)

@router.get("/rates")
async def get_rates(service: RateService = Depends(get_rate_service)):
    return await service.get_all_rates()
```

#### 2. Configuration Management

Use Pydantic Settings for environment-based configuration:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str
    redis_url: str
    api_port: int = 8000
    debug: bool = False

settings = Settings()
```

#### 3. SQLModel for Type-Safe ORM

Use SQLModel to combine SQLAlchemy models with Pydantic validation:

```python
from sqlmodel import SQLModel, Field
from datetime import date
from typing import Optional

class InterestRate(SQLModel, table=True):
    __tablename__ = "interest_rates"

    id: Optional[int] = Field(default=None, primary_key=True)
    series: str = Field(index=True)
    rate_date: date = Field(index=True)
    value: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### 4. Async/Await Throughout

Use async/await for all I/O operations:

```python
# Database queries
async def get_rates(session: AsyncSession) -> list[InterestRate]:
    result = await session.execute(select(InterestRate))
    return result.scalars().all()

# HTTP requests
async def fetch_data(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

#### 5. Service Pattern

Encapsulate business logic in service classes:

```python
class RateService:
    def __init__(self, session: Session):
        self.session = session

    async def get_rates_by_series(self, series: str) -> list[InterestRate]:
        """Fetch rates for a specific series with caching."""
        # Business logic here
        pass

    async def upsert_rate(self, rate_data: dict) -> InterestRate:
        """Create or update a rate record."""
        # Business logic here
        pass
```

#### 6. Repository Pattern (Optional)

For complex queries, consider a repository pattern:

```python
class RateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_series_and_date(
        self, series: str, start_date: date, end_date: date
    ) -> list[InterestRate]:
        query = select(InterestRate).where(
            InterestRate.series == series,
            InterestRate.rate_date >= start_date,
            InterestRate.rate_date <= end_date,
        )
        result = await self.session.execute(query)
        return result.scalars().all()
```

## Scaling Patterns (Future)

### When to Refactor to Packages

If the project grows significantly, consider the pineframe monorepo pattern:

```
fedscrape-docker/
├── packages/              # Reusable libraries
│   ├── core/             # Core utilities, base models
│   ├── database/         # Database models and migrations
│   ├── scraper/          # Scraping logic
│   └── mcp/              # MCP server logic
└── services/             # Standalone applications
    ├── api/              # FastAPI REST API
    ├── worker/           # Background task worker
    └── mcp/              # MCP server service
```

Benefits:
- Each package can be independently versioned
- Shared code reused across services
- Clear dependency boundaries
- Easier to test in isolation

### Task Queue Pattern

For background jobs (like scheduled scraping), add a task queue:

```python
# Using TaskIQ (from pineframe pattern)
from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker

broker = ListQueueBroker("redis://localhost:6379")

@broker.task
async def scrape_rates():
    """Background task to scrape rates."""
    # Scraping logic here
    pass
```

## API Design Patterns

### RESTful Resource Naming

- Use plural nouns: `/rates`, `/series`
- Use nested routes for relationships: `/series/{series_id}/rates`
- Use query params for filtering: `/rates?series=FEDFUNDS&start_date=2024-01-01`

### Response Models

Always use Pydantic models for responses:

```python
from pydantic import BaseModel

class RateResponse(BaseModel):
    id: int
    series: str
    rate_date: date
    value: float

    model_config = {"from_attributes": True}

@router.get("/rates/{rate_id}", response_model=RateResponse)
async def get_rate(rate_id: int, service: RateService = Depends()):
    return await service.get_rate(rate_id)
```

### Error Handling

Use FastAPI's HTTPException for errors:

```python
from fastapi import HTTPException, status

if not rate:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Rate with id {rate_id} not found"
    )
```

## Testing Architecture

- **Unit Tests**: Test services and utilities in isolation
- **Integration Tests**: Test API endpoints with test database
- **Fixtures**: Use pytest fixtures for common setup (see [testing.md](testing.md))

## Performance Patterns

### Caching

Use Redis for caching expensive operations:

```python
from api.cache import cache

@cache.cached(ttl=3600, key="rates:all")
async def get_all_rates() -> list[InterestRate]:
    # Expensive database query
    pass
```

### Rate Limiting

Use SlowAPI to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/rates")
@limiter.limit("100/minute")
async def get_rates(request: Request):
    pass
```

### Database Indexing

Add indexes for commonly queried fields:

```python
class InterestRate(SQLModel, table=True):
    series: str = Field(index=True)  # Indexed for fast lookups
    rate_date: date = Field(index=True)  # Indexed for date range queries
```

## Docker Patterns

### Multi-stage Builds

Use multi-stage Docker builds to minimize image size:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app
CMD ["fedscrape", "serve"]
```

### Docker Compose for Development

Use docker-compose.yml for local development with all services:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file: .env

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
```

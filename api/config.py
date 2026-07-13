from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    API_PORT: int = 8000
    PORT: int = 8000  # Railway overrides via $PORT
    API_BASE_URL: str = "http://localhost:8000"

    REDIS_URL: str = "redis://localhost:6379"
    APP_ENV: str = ""  # set to "test" in CI to disable rate limiting during tests

    AWS_KEY: str = ""
    AWS_SECRET: str = ""
    AWS_REGION: str = ""
    S3_BUCKET: str = ""

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

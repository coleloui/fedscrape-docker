from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    API_PORT: int = 8000
    PORT: int = 8000  # Railway overrides via $PORT
    API_BASE_URL: str = "http://localhost:8000"
    INTERNAL_API_URL: str = ""  # defaults to http://localhost:{PORT}; set explicitly to override

    @model_validator(mode="after")
    def set_internal_api_url(self) -> "Settings":
        if not self.INTERNAL_API_URL:
            self.INTERNAL_API_URL = f"http://localhost:{self.PORT}"
        return self

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

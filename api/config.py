from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://localhost:8000"

    AWS_KEY: str = ""
    AWS_SECRET: str = ""
    AWS_REGION: str = ""
    S3_BUCKET: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

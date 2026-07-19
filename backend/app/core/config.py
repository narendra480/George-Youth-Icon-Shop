from pydantic import AnyUrl, Field
from pydantic import field_validator

try:
    from pydantic import BaseSettings
except Exception:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "George's Youth Icon Shop API"
    project_description: str = "Enterprise footwear shopping API for George's Youth Icon Shop"
    api_version: str = "1.0.0"
    api_prefix: str = Field("/api/v1", env="API_PREFIX")
    secret_key: str = Field(..., env="SECRET_KEY")
    database_url: str = Field(
        "postgresql+psycopg2://postgres:postgres@db:5432/gyis",
        env="DATABASE_URL",
    )
    debug: bool = Field(False, env="DEBUG")
    cors_origins: list[str] = Field(["http://localhost:5173", "http://localhost:5174"], env="CORS_ORIGINS")
    environment: str = Field("development", env="ENVIRONMENT")
    frontend_url: AnyUrl = Field("http://localhost:5173", env="FRONTEND_URL")
    email_backend: str = Field("console", env="EMAIL_BACKEND")
    email_from: str = Field("no-reply@example.com", env="EMAIL_FROM")
    access_token_expires_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRES_MINUTES")
    refresh_token_expires_days: int = Field(30, env="REFRESH_TOKEN_EXPIRES_DAYS")
    password_reset_token_expires_hours: int = Field(1, env="PASSWORD_RESET_TOKEN_EXPIRES_HOURS")

    @field_validator("cors_origins", mode="before")
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

#print("DATABASE_URL =", settings.database_url)
#print("SECRET_KEY =", settings.secret_key)

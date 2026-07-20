from typing import List
import json

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    project_name: str = "George's Youth Icon Shop API"
    project_description: str = "Enterprise Footwear Shopping API"
    api_version: str = "1.0.0"
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/gyis",
        alias="DATABASE_URL",
    )

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        alias="CORS_ORIGINS",
    )

    frontend_url: AnyUrl = Field(
        default="http://localhost:5173",
        alias="FRONTEND_URL",
    )

    backend_url: str = Field(
        default="http://localhost:8000",
        alias="BACKEND_URL",
    )

    # Email
    email_backend: str = Field(default="console", alias="EMAIL_BACKEND")
    email_from: str = Field(default="no-reply@example.com", alias="EMAIL_FROM")

    # JWT
    access_token_expires_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRES_MINUTES",
    )

    refresh_token_expires_days: int = Field(
        default=30,
        alias="REFRESH_TOKEN_EXPIRES_DAYS",
    )

    password_reset_token_expires_hours: int = Field(
        default=1,
        alias="PASSWORD_RESET_TOKEN_EXPIRES_HOURS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """
        Supports:
        1. JSON Array:
           ["http://localhost:5173","https://app.vercel.app"]

        2. Comma-separated:
           http://localhost:5173,https://app.vercel.app

        3. Single URL:
           http://localhost:5173
        """
        if value is None or value == "":
            return ["http://localhost:5173"]

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            value = value.strip()

            # JSON array
            if value.startswith("["):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass

            # Comma separated or single URL
            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return value


settings = Settings()
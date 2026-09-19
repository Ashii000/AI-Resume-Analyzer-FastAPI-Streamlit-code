"""Application configuration using Pydantic v2 BaseSettings.

This module centralizes environment-driven configuration and provides
helpers for common derived values. Sensitive values are never hard-coded.
"""
from __future__ import annotations

import os
from typing import List, Optional
# Compatibility shim for BaseSettings import location across pydantic versions
try:
    # pydantic < 2.5
    from pydantic import BaseSettings  # type: ignore
except Exception:  # pragma: no cover - handles different pydantic packaging
    from pydantic_settings import BaseSettings  # type: ignore

from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional

# Load .env for local development; in production the environment should be configured externally
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        SECRET_KEY: cryptographic secret for JWT and other signing operations.
        APP_NAME: Human-friendly application name.
        BACKEND_HOST / BACKEND_PORT: host and port for uvicorn server.
        DATABASE_URL: SQLAlchemy-compatible URL. Use PostgreSQL in production.
        ALLOWED_ORIGINS: list of CORS origins.
        UPLOAD_DIR: base directory where uploads are stored.
        LOG_LEVEL: logging level.
        GEMINI_API_KEY / OPENAI_API_KEY: optional keys for AI providers.
    """

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    APP_NAME: str = Field("AI Resume Analyzer", env="APP_NAME")
    BACKEND_HOST: str = Field("127.0.0.1", env="BACKEND_HOST")
    BACKEND_PORT: int = Field(8000, env="BACKEND_PORT")
    DATABASE_URL: str = Field("sqlite:///./ai_resume_analyzer.db", env="DATABASE_URL")
    ALLOWED_ORIGINS: Optional[str] = Field("http://localhost:8501,http://localhost:3000", env="ALLOWED_ORIGINS")
    UPLOAD_DIR: str = Field("app/uploads", env="UPLOAD_DIR")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # AI provider keys (store in env / secrets manager in production)
    GEMINI_API_KEY: Optional[str] = Field(None, env="GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")

    # Optional Sentry DSN
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def allowed_origins_list(self) -> List[str]:
        """Return ALLOWED_ORIGINS as a list of strings.

        Comma-separated values are trimmed. If wildcard '*' is present, it is returned as-is.
        """
        if not self.ALLOWED_ORIGINS:
            return []
        # support both comma separated string or a single origin
        items = [s.strip() for s in self.ALLOWED_ORIGINS.split(",") if s.strip()]
        return items


# Instantiate a global settings object for application-wide usage
settings = Settings()

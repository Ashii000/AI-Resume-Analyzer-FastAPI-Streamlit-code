"""FastAPI application factory and entrypoint.

This module creates the FastAPI application, wires routers, configures CORS,
logging, and provides startup/shutdown hooks that initialize the database and
ensure upload directories exist.
"""
from __future__ import annotations

import logging
from logging.config import dictConfig
from contextlib import asynccontextmanager
from typing import AsyncIterator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.middleware import Middleware

from app.config import settings
from app.database.database import engine
from app.database.models import Base

BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)

# Import routers
from app.api import auth as auth_api
from app.api import resume as resume_api
from app.api import jobs as jobs_api
from app.api import ats as ats_api
from app.api import ai as ai_api
from app.api import dashboard as dashboard_api
from app.api import users as users_api


def configure_logging() -> None:
    """Configure structured logging for the application.

    Uses dictConfig so logging is initialized consistently in Uvicorn workers.
    """
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "logging.Formatter",
                "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": settings.LOG_LEVEL,
            }
        },
        "root": {"handlers": ["console"], "level": settings.LOG_LEVEL},
    })


def create_upload_directories(base_dir: str) -> None:
    """Create upload directories on application startup.

    Args:
        base_dir: Base uploads directory (relative or absolute).
    """
    base = Path(base_dir)
    try:
        resumes = base / "resumes"
        jobs = base / "jobs"
        for path in (base, resumes, jobs):
            path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - defensive
        logging.getLogger(__name__).exception("Failed to create upload directories: %s", exc)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup and shutdown events.

    Initializes logging, upload directories, and the database.
    """
    # Configure logging early so other startup tasks are logged
    configure_logging()
    logger = logging.getLogger("app.lifespan")
    logger.info("Starting application: %s", settings.APP_NAME)

    # Ensure upload directories exist
    create_upload_directories(settings.UPLOAD_DIR)

    # Initialize DB (tables) using helper from app.database.database
    try:
        from app.database.database import init_db

        init_db(Base)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Database init failed during startup: %s", exc)
        raise

    yield

    logger.info("Shutting down application: %s", settings.APP_NAME)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        Configured FastAPI application.
    """
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list or ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    app = FastAPI(
        title=settings.APP_NAME,
        description="AI Resume Analyzer & ATS Score Checker",
        version="0.1.0",
        lifespan=lifespan,
        middleware=middleware,
    )

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Register routers
    app.include_router(auth_api.router, prefix="/api/auth", tags=["auth"])
    app.include_router(users_api.router, prefix="/api/users", tags=["users"])
    app.include_router(resume_api.router, prefix="/api/resumes", tags=["resumes"])
    app.include_router(jobs_api.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(ats_api.router, prefix="/api/ats", tags=["ats"])
    app.include_router(ai_api.router, prefix="/api/ai", tags=["ai"])
    app.include_router(dashboard_api.router, prefix="/api/dashboard", tags=["dashboard"])

    # Health & root endpoints
    @app.get("/health", summary="Health check")
    async def health() -> JSONResponse:
        """Return a simple health status for monitoring."""
        return JSONResponse({"status": "ok"})

    @app.get("/", summary="Root")
    async def root(request: Request):
        """Serve the main UI page for browser requests, and JSON info for API clients."""
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            return HTMLResponse(jinja_env.get_template("index.html").render())
        return JSONResponse(
            {
                "app": settings.APP_NAME,
                "version": "0.1.0",
                "host": settings.BACKEND_HOST,
                "port": settings.BACKEND_PORT,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    # Allow running with `python -m app.main` for local development
    import uvicorn

    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)

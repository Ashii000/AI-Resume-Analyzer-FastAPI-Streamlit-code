"""Database connection and session utilities.

Provides a SQLAlchemy Engine and a Session factory suitable for use across the
application. Also exposes a get_db dependency for FastAPI route handlers and
helpers to initialize database tables.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine. Use check_same_thread for SQLite to allow multi-thread access.
_engine_kwargs: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

try:
    engine = create_engine(settings.DATABASE_URL, future=True, **_engine_kwargs)
except Exception as exc:  # pragma: no cover - will surface during app startup
    logger.exception("Failed to create engine for DATABASE_URL=%s: %s", settings.DATABASE_URL, exc)
    raise

# Session factory (SQLAlchemy 2.x style)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy Session.

    Yields:
        sqlalchemy.orm.Session: a database session that will be closed after use.
    """
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    except Exception:  # pragma: no cover - let calling code handle exceptions
        logger.exception("Session encountered an exception")
        raise
    finally:
        if db is not None:
            db.close()


def create_tables(base) -> None:
    """Create all tables defined on the provided SQLAlchemy declarative Base.

    Args:
        base: declarative Base that defines metadata (e.g., models.Base).
    """
    try:
        base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to create database tables: %s", exc)
        raise


def ensure_sqlite_dir_exists() -> None:
    """Ensure the parent directory for the SQLite file exists (development only).

    This is a convenience for file-based SQLite URIs like sqlite:///./path.db
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        # extract the file path after sqlite:///
        parts = settings.DATABASE_URL.split("sqlite:///", 1)
        if len(parts) == 2:
            db_path = parts[1]
            path = Path(db_path).resolve().parent
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.exception("Unable to create directory for sqlite db: %s", path)
                raise


def init_db(base) -> None:
    """Run DB initialization tasks: ensure file paths and create tables.

    Args:
        base: declarative Base (models.Base)
    """
    ensure_sqlite_dir_exists()
    create_tables(base)

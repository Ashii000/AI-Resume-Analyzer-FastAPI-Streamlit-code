"""Development run script.

This script launches the FastAPI application using uvicorn. For production
use a process manager (systemd, supervisord) or container orchestrator.
"""
from __future__ import annotations

import sys
import logging
import subprocess
from pathlib import Path

from app.config import settings


def run() -> int:
    """Run the application with uvicorn using settings from app.config.

    Returns the process exit code.
    """
    logger = logging.getLogger("run")
    logger.setLevel(settings.LOG_LEVEL)

    uvicorn_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        settings.BACKEND_HOST,
        "--port",
        str(settings.BACKEND_PORT),
        "--reload",
    ]

    logger.info("Starting uvicorn: %s", " ".join(uvicorn_cmd))
    try:
        return subprocess.call(uvicorn_cmd)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as exc:
        logger.exception("Failed to start server: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(run())

"""Domain-specific exceptions and a FastAPI handler that maps them to HTTP."""
from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base for application errors that should map to a specific HTTP status."""

    status_code: int = 500
    public_message: str = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.public_message)


class StoreNotFound(AppError):
    status_code = 404
    public_message = "One or more requested stores were not found"


class OpenAIUnavailable(AppError):
    status_code = 503
    public_message = "OpenAI API is not reachable"


class OpenAIError(AppError):
    status_code = 502
    public_message = "OpenAI returned an error"


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    logger.warning("AppError raised: %s (%s)", exc.__class__.__name__, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.public_message, "detail": str(exc)},
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.errors import AppError, app_error_handler, unhandled_error_handler
from app.logging_config import configure_logging
from app.routes import stores, wines
from app.services.assortment import AssortmentService
from app.services.ollama import OllamaClient


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info("Starting Wine AI backend")
    logger.info("Assortments dir: %s", settings.assortments_dir)
    logger.info("Ollama: %s (model=%s)", settings.ollama_url, settings.ollama_model)

    assortment_service = AssortmentService(settings.assortments_dir)
    assortment_service.load_stores()

    ollama_client = OllamaClient(
        base_url=settings.ollama_url,
        model=settings.ollama_model,
    )

    app.state.assortment = assortment_service
    app.state.ollama = ollama_client
    app.state.settings = settings

    try:
        yield
    finally:
        await ollama_client.aclose()
        logger.info("Wine AI backend stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Wine AI",
        version="1.0.0",
        description="Local wine recommender backed by Systembolaget data and Ollama.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(stores.router, prefix="/api")
    app.include_router(wines.router, prefix="/api")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

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
from app.services.ollama import OpenAIClient


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info("Starting Wine AI backend")
    logger.info("Assortments dir: %s", settings.assortments_dir)
    logger.info("OpenAI: %s (model=%s)", settings.openai_base_url, settings.openai_model)

    assortment_service = AssortmentService(settings.assortments_dir)
    assortment_service.load_stores()

    openai_client = OpenAIClient(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )

    app.state.assortment = assortment_service
    app.state.openai = openai_client
    app.state.settings = settings

    try:
        yield
    finally:
        await openai_client.aclose()
        logger.info("Wine AI backend stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Wine AI",
        version="1.0.0",
        description="Wine recommender backed by Systembolaget data and OpenAI.",
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

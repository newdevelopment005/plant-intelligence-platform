from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import router as api_router

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(settings.LOG_LEVEL),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI service", environment=settings.ENVIRONMENT)
    yield
    logger.info("Shutting down AI service")


def create_app() -> FastAPI:
    application = FastAPI(
        title="Plant Intelligence Platform - AI Service",
        description="AI-powered research assistant for plant science",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api/v1")

    @application.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": "pip-ai-service", "version": "0.1.0"}

    return application


app = create_app()

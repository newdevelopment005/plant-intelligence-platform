import json
import os
from contextlib import asynccontextmanager

import httpx
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.health import router as health_router
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.core.rate_limiter import RateLimitMiddleware
from app.core.security_headers import SecurityHeadersMiddleware

# Import all models to register them with SQLAlchemy metadata
from app.modules.auth.domain import models as _auth_models  # noqa: F401
from app.modules.project.domain import models as _project_models  # noqa: F401
from app.modules.germplasm.domain import models as _germplasm_models  # noqa: F401
from app.modules.phenotyping.domain import models as _phenotyping_models  # noqa: F401
from app.modules.genomics.domain import models as _genomics_models  # noqa: F401
from app.modules.molecular.domain import models as _molecular_models  # noqa: F401
from app.modules.bioinformatics.domain import models as _bioinformatics_models  # noqa: F401
from app.modules.literature.domain import models as _literature_models  # noqa: F401
from app.modules.knowledge_graph.domain import models as _kg_models  # noqa: F401
from app.modules.notebook.domain import models as _notebook_models  # noqa: F401
from app.modules.lims.domain import models as _lims_models  # noqa: F401
from app.modules.image_analysis.domain import models as _image_models  # noqa: F401
from app.modules.reporting.domain import models as _reporting_models  # noqa: F401
from app.modules.ai_assistant.domain import models as _ai_models  # noqa: F401
from app.modules.sharing.domain import models as _sharing_models  # noqa: F401
from app.modules.team.domain import models as _team_models  # noqa: F401
from app.modules.department.domain import models as _department_models  # noqa: F401
from app.modules.meeting.domain import models as _meeting_models  # noqa: F401

from app.modules.admin.api.router import router as admin_router
from app.modules.ai_assistant.api.router import router as ai_assistant_router
from app.modules.auth.api.router import router as auth_router
from app.modules.bioinformatics.api.router import router as bioinformatics_router
from app.modules.department.api.router import router as department_router
from app.modules.genomics.api.router import router as genomics_router
from app.modules.germplasm.api.router import router as germplasm_router
from app.modules.image_analysis.api.router import router as image_analysis_router
from app.modules.knowledge_graph.api.router import router as knowledge_graph_router
from app.modules.lims.api.router import router as lims_router
from app.modules.literature.api.router import router as literature_router
from app.modules.meeting.api.router import router as meeting_router
from app.modules.molecular.api.router import router as molecular_router
from app.modules.notebook.api.router import router as notebook_router
from app.modules.phenotyping.api.router import router as phenotyping_router
from app.modules.project.api.router import router as project_router
from app.modules.reporting.api.router import router as reporting_router
from app.modules.sharing.api.router import router as sharing_router
from app.modules.team.api.router import router as team_router

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
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
    logger.info("Starting API service", environment=settings.ENVIRONMENT)
    yield
    logger.info("Shutting down API service")


def create_app() -> FastAPI:
    application = FastAPI(
        title="Plant Intelligence Platform API",
        description="Enterprise-grade AI-powered scientific research platform for plant science",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RateLimitMiddleware)
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(application)

    application.include_router(health_router, tags=["Health"])
    application.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    application.include_router(ai_assistant_router, prefix="/api/v1/ai", tags=["AI Research Assistant"])
    application.include_router(project_router, prefix="/api/v1/projects", tags=["Projects"])
    application.include_router(germplasm_router, prefix="/api/v1/germplasm", tags=["Germplasm"])
    application.include_router(phenotyping_router, prefix="/api/v1/phenotyping", tags=["Phenotyping"])
    application.include_router(genomics_router, prefix="/api/v1/genomics", tags=["Genomics"])
    application.include_router(molecular_router, prefix="/api/v1/molecular", tags=["Molecular Biology"])
    application.include_router(bioinformatics_router, prefix="/api/v1/bioinformatics", tags=["Bioinformatics"])
    application.include_router(literature_router, prefix="/api/v1/literature", tags=["Literature"])
    application.include_router(knowledge_graph_router, prefix="/api/v1/knowledge-graph", tags=["Knowledge Graph"])
    application.include_router(notebook_router, prefix="/api/v1/notebook", tags=["Notebook"])
    application.include_router(lims_router, prefix="/api/v1/lims", tags=["LIMS"])
    application.include_router(image_analysis_router, prefix="/api/v1/images", tags=["Image Analysis"])
    application.include_router(reporting_router, prefix="/api/v1/reports", tags=["Reporting"])
    application.include_router(sharing_router, prefix="/api/v1/sharing", tags=["Sharing"])
    application.include_router(team_router, prefix="/api/v1/teams", tags=["Teams"])
    application.include_router(department_router, prefix="/api/v1/departments", tags=["Departments"])
    application.include_router(meeting_router, prefix="/api/v1/meetings", tags=["Meetings"])
    application.include_router(admin_router, prefix="/api/v1/admin", tags=["Administration"])

    @application.get("/storage/{file_path:path}")
    async def serve_storage(file_path: str):
        """Serve static files from the storage directory."""
        full_path = os.path.join(settings.STORAGE_LOCAL_PATH, file_path)
        if os.path.isfile(full_path):
            return FileResponse(full_path)
        return Response(status_code=404, content="File not found")

    @application.api_route("/ai-proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    @application.api_route("/api/v1/ai-proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    async def ai_proxy(path: str, request: Request):
        """Proxy requests to Ollama or AI microservice."""
        if request.method == "OPTIONS":
            return Response(status_code=204, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            })
        body = await request.body()
        ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
        try:
            client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))
            req = client.build_request(
                method=request.method,
                url=f"{ollama_url}/{path}",
                headers={k: v for k, v in request.headers.items() if k.lower() not in ("host",)},
                content=body,
            )
            resp = await client.send(req, stream=True)

            content_type = resp.headers.get("content-type", "application/json")

            async def stream_generator():
                try:
                    async for chunk in resp.aiter_bytes():
                        yield chunk
                finally:
                    await resp.aclose()
                    await client.aclose()

            return StreamingResponse(
                stream_generator(),
                status_code=resp.status_code,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": content_type,
                    "Cache-Control": "no-cache",
                },
            )
        except Exception as e:
            logger.error("ai_proxy_error", error=str(e))
            return Response(
                content=json.dumps({"error": str(e)}).encode(),
                status_code=502,
                headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            )

    return application


app = create_app()

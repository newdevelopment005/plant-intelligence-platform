"""Deep health check endpoint for production monitoring."""
import asyncio
import time

import structlog
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger()
router = APIRouter()


async def _check_postgres() -> dict:
    start = time.time()
    try:
        from app.database import async_session_factory

        async with async_session_factory() as session:
            await session.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        logger.warning("health_check_postgres_failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


async def _check_redis() -> dict:
    start = time.time()
    try:
        import redis.asyncio as aioredis

        from app.config import settings

        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=5)
        await r.ping()
        await r.aclose()
        return {"status": "healthy", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        logger.warning("health_check_redis_failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


async def _check_neo4j() -> dict:
    start = time.time()
    try:
        from neo4j import AsyncGraphDatabase

        from app.config import settings

        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        async with driver.session() as session:
            await session.run("RETURN 1")
        await driver.close()
        return {"status": "healthy", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        logger.warning("health_check_neo4j_failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


async def _check_qdrant() -> dict:
    start = time.time()
    try:
        import httpx

        from app.config import settings

        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.QDRANT_URL}/healthz")
            resp.raise_for_status()
        return {"status": "healthy", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        logger.warning("health_check_qdrant_failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


@router.get("/health")
async def deep_health_check():
    """Deep health check verifying all downstream dependencies."""
    checks = await asyncio.gather(
        _check_postgres(),
        _check_redis(),
        _check_neo4j(),
        _check_qdrant(),
        return_exceptions=True,
    )

    results = {
        "postgres": checks[0] if not isinstance(checks[0], Exception) else {"status": "unhealthy", "error": str(checks[0])},
        "redis": checks[1] if not isinstance(checks[1], Exception) else {"status": "unhealthy", "error": str(checks[1])},
        "neo4j": checks[2] if not isinstance(checks[2], Exception) else {"status": "unhealthy", "error": str(checks[2])},
        "qdrant": checks[3] if not isinstance(checks[3], Exception) else {"status": "unhealthy", "error": str(checks[3])},
    }

    all_healthy = all(c.get("status") == "healthy" for c in results.values())
    any_healthy = any(c.get("status") == "healthy" for c in results.values())

    if all_healthy:
        overall = "healthy"
        http_status = status.HTTP_200_OK
    elif any_healthy:
        overall = "degraded"
        http_status = status.HTTP_200_OK
    else:
        overall = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "status": overall,
            "service": "pip-api",
            "version": "0.1.0",
            "dependencies": results,
        },
    )


@router.get("/ready")
async def readiness_check():
    """Readiness probe - returns 200 only if critical dependencies are up."""
    checks = await asyncio.gather(
        _check_postgres(),
        _check_redis(),
        return_exceptions=True,
    )

    postgres_ok = isinstance(checks[0], dict) and checks[0].get("status") == "healthy"
    redis_ok = isinstance(checks[1], dict) and checks[1].get("status") == "healthy"

    if postgres_ok and redis_ok:
        return {"status": "ready"}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "postgres": "ok" if postgres_ok else "down", "redis": "ok" if redis_ok else "down"},
        )

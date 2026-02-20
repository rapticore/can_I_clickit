import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import feedback, health, recovery, scan
from app.cache.redis_client import close_redis
from app.core.config import get_settings
from app.db.database import close_db, init_db_schema

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db_schema()
    except Exception as exc:
        logger.error("db_init_failed", error=str(exc))
    logger.info("application_startup", version=get_settings().app_version)
    yield
    await close_redis()
    await close_db()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Personal Safety Assistant — A Seatbelt for the Internet",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router, prefix="/v1", tags=["Health"])
    application.include_router(scan.router, prefix="/v1", tags=["Scan"])
    application.include_router(recovery.router, prefix="/v1", tags=["Recovery"])
    application.include_router(feedback.router, prefix="/v1", tags=["Feedback"])

    return application


app = create_app()


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
        )
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    finally:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "request_completed",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code if response else 500,
            latency_ms=elapsed_ms,
        )
        if response:
            response.headers["X-Request-ID"] = request_id

    return response

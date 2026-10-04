"""Main FastAPI application entry point for INFRAPLUS."""

from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router
from app.api.projects import router as projects_router
from app.api.storage import router as storage_router
from app.config import (
    CORS_ORIGINS,
    ENVIRONMENT,
    FIREBASE_DATABASE_URL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LOG_FORMAT,
    LOG_LEVEL,
    MAX_FILE_SIZE_MB,
    RATE_LIMIT_ENABLED,
    TRUST_REVERSE_PROXY,
    UPLOAD_DIR,
)
from app.core.logging import (
    configure_logging,
    get_request_id,
    sanitize_request_id,
    set_request_id,
)
from app.core.rate_limiter import RateLimitExceeded

# Initialize centralized logging with request ID correlation
configure_logging(log_level=LOG_LEVEL, log_format=LOG_FORMAT)
logger = logging.getLogger("infraplus.main")
access_logger = logging.getLogger("infraplus.access")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifecycle manager for startup diagnostics and graceful shutdown."""
    logger.info(
        f"Starting INFRAPLUS API Server | Environment: {ENVIRONMENT} | LogLevel: {LOG_LEVEL} | LogFormat: {LOG_FORMAT} "
        f"| RateLimiter: {RATE_LIMIT_ENABLED} | TrustReverseProxy: {TRUST_REVERSE_PROXY} "
        f"| FirebaseConfigured: {bool(FIREBASE_DATABASE_URL)} | GeminiConfigured: {bool(GEMINI_API_KEY)} "
        f"| GeminiModel: {GEMINI_MODEL} | UploadDir: {UPLOAD_DIR} | MaxUploadMB: {MAX_FILE_SIZE_MB}"
    )
    yield
    # Graceful shutdown: close connection pools
    from app.services.firebase_service import close_firebase_http_client
    close_firebase_http_client()
    logger.info("INFRAPLUS API server shutting down gracefully.")


app = FastAPI(
    title="INFRAPLUS — Infrastructure Intelligence Platform API",
    description=(
        "Production backend for INFRAPLUS: Infrastructure project monitoring, "
        "deterministic risk calculation, Firebase Realtime Database integration, "
        "and grounded Gemini AI intelligence."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_correlation_middleware(request: Request, call_next):
    """
    Request correlation and access logging middleware.
    Extracts or generates sanitized X-Request-ID, binds it to ContextVar,
    measures request latency, injects X-Request-ID into response headers,
    and logs request lifecycle with safe metadata only.
    """
    raw_id = request.headers.get("X-Request-ID")
    req_id = sanitize_request_id(raw_id)
    set_request_id(req_id)

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Invalidate or set response correlation header
    response.headers["X-Request-ID"] = req_id

    # Safe access logging (zero body/credential/cookie dumping)
    access_logger.info(
        f"{request.method} {request.url.path} completed in {duration_ms}ms [status={response.status_code}, req_id={req_id}]",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "request_id": req_id,
        },
    )

    return response


@app.get("/", tags=["root"])
def root() -> dict:
    """Root platform discovery endpoint."""
    return {
        "service": "INFRAPLUS Infrastructure Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "operational",
    }


# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(projects_router)
app.include_router(chat_router)
app.include_router(storage_router)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_: Request, exc: RuntimeError) -> JSONResponse:
    """Handle runtime database configuration and connectivity errors gracefully."""
    req_id = get_request_id()
    logger.error(f"Runtime database error [req_id={req_id}]: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "request_id": req_id},
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    """Handle input or parsing value errors."""
    req_id = get_request_id()
    logger.warning(f"Value validation error [req_id={req_id}]: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "request_id": req_id},
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle 429 Too Many Requests with compliant retry and limit headers."""
    req_id = get_request_id()
    headers = dict(exc.headers or {})
    headers["X-Request-ID"] = req_id
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "retry_after": exc.retry_after,
            "limit": exc.limit,
            "window_seconds": exc.window_seconds,
            "request_id": req_id,
        },
        headers=headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Safe global unhandled exception handler masking stack traces from clients."""
    req_id = get_request_id()
    logger.error(f"Unhandled internal server error [req_id={req_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
            "request_id": req_id,
        },
        headers={"X-Request-ID": req_id},
    )



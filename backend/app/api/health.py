"""Health check and platform diagnostic route."""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.firebase_service import get_firebase_status, get_projects_count_shallow

router = APIRouter(tags=["health"])


@router.get("/health/live")
def liveness_check() -> dict:
    """Ultra-lightweight liveness probe with zero external I/O."""
    return {
        "status": "live",
        "service": "INFRAPLUS Infrastructure Monitoring Platform",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready")
def readiness_check() -> dict:
    """Lightweight readiness probe checking external dependency configuration."""
    fb_status = get_firebase_status()
    db_configured = bool(fb_status.get("configured"))
    ai_configured = bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")

    # Shallow verification without downloading data
    shallow_count = get_projects_count_shallow() if db_configured else None
    db_ready = shallow_count is not None

    ready = db_ready and ai_configured
    return {
        "status": "ready" if ready else "not_ready",
        "database_ready": db_ready,
        "ai_ready": ai_configured,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health")
def health_check() -> dict:
    """
    Return comprehensive platform health and connectivity status.
    Eliminates the expensive full-database download by performing a lightweight shallow count.
    Preserves 100% backward compatibility of response structure for existing consumers and E2E tests.
    """
    fb_status = get_firebase_status()

    projects_count = 0
    db_connected = False
    db_error = None

    if not fb_status.get("configured"):
        db_error = "Firebase Realtime Database is not configured. Please set FIREBASE_DATABASE_URL in .env."
    else:
        shallow_count = get_projects_count_shallow()
        if shallow_count is not None:
            projects_count = shallow_count
            db_connected = True
        else:
            db_error = "Unable to connect to Firebase Realtime Database. Please verify your network and credentials."

    return {
        "status": "ok",
        "service": "INFRAPLUS Infrastructure Monitoring Platform",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "connected": db_connected,
            "url": fb_status.get("database_url"),
            "admin_sdk_ready": fb_status.get("admin_sdk_ready"),
            "projects_count": projects_count,
            "error": db_error,
        },
        "ai_engine": {
            "gemini_configured": bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here"),
            "model": GEMINI_MODEL,
        },
    }


"""Authentication and user session verification API routes."""

from typing import Any
from fastapi import APIRouter, Depends

from app.core.security import get_current_user, get_optional_user
from app.services.firebase_service import get_firebase_status

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/status")
def auth_status() -> dict[str, Any]:
    """Return backend Firebase Auth readiness and configuration status."""
    fb_status = get_firebase_status()
    return {
        "configured": fb_status.get("configured", False),
        "admin_sdk_ready": fb_status.get("admin_sdk_ready", False),
        "auth_provider": "Firebase Authentication",
    }


@router.get("/me")
async def verify_token(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Verify caller's Firebase ID token server-side.
    Returns decoded token claims (uid, email, email_verified, etc.).
    Rejects missing, invalid, or expired tokens with HTTP 401.
    """
    return {
        "status": "authenticated",
        "uid": current_user.get("uid") or current_user.get("user_id"),
        "email": current_user.get("email"),
        "email_verified": current_user.get("email_verified", False),
        "claims": current_user,
    }


@router.get("/check-session")
async def check_session(
    user: dict[str, Any] | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """Non-blocking session check returning whether caller possesses valid bearer token."""
    return {
        "authenticated": user is not None,
        "user_id": (user.get("uid") or user.get("user_id")) if user else None,
    }

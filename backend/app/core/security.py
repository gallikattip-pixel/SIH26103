"""Backend authentication and security dependencies."""

from enum import Enum
import logging
from typing import Any
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import FIREBASE_SERVICE_ACCOUNT_KEY, is_production

logger = logging.getLogger("infraplus.security")

security_scheme = HTTPBearer(auto_error=False)


class UserRole(str, Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    VIEWER = "viewer"


VALID_ROLES = {UserRole.ADMIN.value, UserRole.OFFICER.value, UserRole.VIEWER.value}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
) -> dict[str, Any]:
    """
    Verify Firebase ID token server-side using Firebase Admin SDK.
    Rejects requests with missing or invalid tokens for protected routes (HTTP 401).
    In production mode, strictly fails closed if service account or verification is unavailable.
    In development/test mode, allows unverified JWT decoding only when service account is absent.
    Extracts trusted 'role' claim if present; missing/invalid role remains None (fails closed on write).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided. Expected Bearer ID token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # If Firebase Admin is initialized with service account
    try:
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(token)
    except ImportError:
        logger.error("firebase_admin not installed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication module is not properly configured.",
        )
    except Exception as exc:
        # In production mode: strictly fail closed. Never decode an unverified JWT as a production identity.
        if is_production():
            logger.error(
                "Production authentication failure: Firebase token verification failed or service account key is unconfigured."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Valid verified Firebase token required in production.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # In development/test mode: if service account is not yet configured, allow offline test decoding
        if not FIREBASE_SERVICE_ACCOUNT_KEY:
            logger.warning(f"Development mode token fallback: FIREBASE_SERVICE_ACCOUNT_KEY not set: {exc}")
            try:
                import jwt
                decoded_token = jwt.decode(token, options={"verify_signature": False})
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token format.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            logger.warning(f"Failed to verify Firebase ID token: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Normalize uid
    uid = decoded_token.get("uid") or decoded_token.get("user_id")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing valid user identity.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    decoded_token["uid"] = uid

    # Validate role claim strictly against trusted roles (admin, officer, viewer)
    # Fail closed: Do NOT infer role from email or default to officer
    raw_role = decoded_token.get("role")
    if raw_role and str(raw_role).lower() in VALID_ROLES:
        decoded_token["role"] = str(raw_role).lower()
    else:
        decoded_token["role"] = None

    return decoded_token


def require_roles(allowed_roles: list[str | UserRole]):
    """
    Reusable authorization dependency.
    Requires caller to be authenticated (401 if not) and possess an authorized role (403 if not).
    Missing or invalid role claim fails closed with HTTP 403 Forbidden.
    """
    normalized_allowed = {
        r.value if isinstance(r, UserRole) else str(r).lower() for r in allowed_roles
    }

    async def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role")
        if not user_role or user_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied: Operation requires one of roles: {sorted(list(normalized_allowed))}. "
                    f"Your role is '{user_role or 'none'}'."
                ),
            )
        return current_user

    return role_checker


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
) -> dict[str, Any] | None:
    """Optional authentication for endpoints that support both public and authenticated views."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

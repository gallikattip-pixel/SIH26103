"""Enterprise in-memory rate limiter for INFRAPLUS backend."""

from collections import defaultdict
import logging
import math
import threading
import time
from typing import Any, Protocol
from fastapi import HTTPException, Request, Response, status

from app.config import (
    RATE_LIMIT_ENABLED,
    TRUST_REVERSE_PROXY,
)

logger = logging.getLogger("infraplus.rate_limiter")


class RateLimitExceeded(HTTPException):
    """Exception raised when a client exceeds configured rate limits."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        retry_after: int,
        reset_epoch: int,
        detail: str = "Rate limit exceeded.",
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_epoch),
            },
        )
        self.limit = limit
        self.window_seconds = window_seconds
        self.retry_after = retry_after
        self.reset_epoch = reset_epoch


def resolve_client_ip(request: Request) -> str:
    """
    Safely resolve client IP.
    NEVER blindly trusts X-Forwarded-For unless TRUST_REVERSE_PROXY is explicitly True.
    """
    if TRUST_REVERSE_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            first_ip = forwarded.split(",")[0].strip()
            if first_ip:
                return first_ip
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


def resolve_client_identity(request: Request, current_user: dict[str, Any] | None = None) -> str:
    """
    Resolve client identity key:
    - Authenticated: user:<firebase_uid>
    - Anonymous: ip:<safely_resolved_client_ip>
    Never uses email, role, or raw tokens as identity.
    """
    if current_user:
        uid = current_user.get("uid") or current_user.get("user_id")
        if uid:
            return f"user:{uid}"

    client_ip = resolve_client_ip(request)
    return f"ip:{client_ip}"


class RateLimitStorage(Protocol):
    """Abstract interface to allow distributed backends (e.g. Redis) in the future."""

    def check_and_record(
        self,
        scope: str,
        identity: str,
        limit: int,
        window_seconds: int,
        bytes_cost: int = 0,
        max_bytes: int | None = None,
    ) -> tuple[bool, int, int, int]:
        ...

    def clear(self) -> None:
        ...


class InMemoryRateLimiter:
    """
    Thread-safe sliding-window in-memory rate limiter.
    Uses time.monotonic() for interval math to prevent system clock skew anomalies.
    Automatically purges expired entries to prevent unbounded memory growth.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # bucket_key -> list of (monotonic_timestamp, byte_size)
        self._records: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._check_counter = 0

    def check_and_record(
        self,
        scope: str,
        identity: str,
        limit: int,
        window_seconds: int,
        bytes_cost: int = 0,
        max_bytes: int | None = None,
    ) -> tuple[bool, int, int, int]:
        """
        Check rate limit and record usage if allowed.
        Returns:
            (allowed: bool, remaining: int, retry_after: int, reset_epoch: int)
        """
        if not RATE_LIMIT_ENABLED:
            wall_now = time.time()
            return True, limit, 0, int(wall_now + window_seconds)

        now = time.monotonic()
        wall_now = time.time()
        bucket_key = f"{scope}:{identity}"

        with self._lock:
            entries = self._records[bucket_key]
            # 1. Evict entries outside the sliding window
            cutoff = now - window_seconds
            valid_entries = [e for e in entries if e[0] >= cutoff]

            count = len(valid_entries)
            total_bytes = sum(e[1] for e in valid_entries)

            # 2. Check if count limit or byte volume limit is exceeded
            if count >= limit or (max_bytes is not None and (total_bytes + bytes_cost) > max_bytes):
                oldest_ts = valid_entries[0][0] if valid_entries else cutoff
                retry_after = max(1, int(math.ceil(window_seconds - (now - oldest_ts))))
                reset_epoch = int(wall_now + retry_after)
                self._records[bucket_key] = valid_entries
                return False, 0, retry_after, reset_epoch

            # 3. Request is allowed - record entry
            valid_entries.append((now, bytes_cost))
            self._records[bucket_key] = valid_entries
            remaining = max(0, limit - len(valid_entries))
            oldest_ts = valid_entries[0][0]
            time_until_oldest_expires = max(1, int(math.ceil(window_seconds - (now - oldest_ts))))
            reset_epoch = int(wall_now + time_until_oldest_expires)

            # 4. Periodic stale bucket sweep (every 100 checks)
            self._check_counter += 1
            if self._check_counter >= 100:
                self._cleanup_stale_locked(now)
                self._check_counter = 0

            return True, remaining, 0, reset_epoch

    def _cleanup_stale_locked(self, now: float, max_idle: float = 300.0) -> int:
        """Purge idle keys from memory (called with self._lock)."""
        stale_keys = []
        for key, entries in self._records.items():
            if not entries or (now - entries[-1][0]) > max_idle:
                stale_keys.append(key)
        for key in stale_keys:
            del self._records[key]
        return len(stale_keys)

    def cleanup_expired(self, max_idle_seconds: float = 0.0) -> int:
        """Public cleanup method for unit tests and maintenance."""
        now = time.monotonic()
        with self._lock:
            return self._cleanup_stale_locked(now, max_idle=max_idle_seconds)

    def clear(self) -> None:
        """Reset all rate limiter records (useful for test isolation)."""
        with self._lock:
            self._records.clear()
            self._check_counter = 0

    def get_bucket_count(self) -> int:
        """Return total tracked bucket count."""
        with self._lock:
            return len(self._records)


limiter = InMemoryRateLimiter()


def apply_rate_limit(
    scope: str,
    identity: str,
    limit: int,
    window_seconds: int,
    bytes_cost: int = 0,
    max_bytes: int | None = None,
    request: Request | None = None,
    response: Response | None = None,
) -> None:
    """
    Enforce rate limit for a given scope and identity.
    Sets response rate-limit headers if allowed; raises RateLimitExceeded (HTTP 429) if exceeded.
    """
    allowed, remaining, retry_after, reset_epoch = limiter.check_and_record(
        scope=scope,
        identity=identity,
        limit=limit,
        window_seconds=window_seconds,
        bytes_cost=bytes_cost,
        max_bytes=max_bytes,
    )

    if not allowed:
        from app.core.logging import get_request_id
        req_id = get_request_id()
        identity_type = "authenticated" if identity.startswith("user:") else "anonymous"
        path = request.url.path if request else "unknown"
        logger.warning(
            f"Rate limit exceeded [req_id={req_id}]: scope='{scope}', identity_type='{identity_type}', "
            f"path='{path}', limit={limit}/{window_seconds}s, retry_after={retry_after}s",
            extra={
                "request_id": req_id,
                "scope": scope,
                "identity_type": identity_type,
                "path": path,
                "limit": limit,
                "retry_after": retry_after,
            },
        )
        raise RateLimitExceeded(
            limit=limit,
            window_seconds=window_seconds,
            retry_after=retry_after,
            reset_epoch=reset_epoch,
            detail="Rate limit exceeded.",
        )

    if response is not None:
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_epoch)

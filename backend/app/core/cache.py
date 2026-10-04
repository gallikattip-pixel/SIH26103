"""Thread-safe in-memory TTL cache with cache-stampede protection.

Zero external infrastructure (no Redis, no memcached). Pure Python standard library.
"""

from collections.abc import Callable
import logging
import threading
import time
from typing import Generic, TypeVar

logger = logging.getLogger("infraplus.cache")

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Thread-safe TTL cache for a single computed resource with stampede protection."""

    def __init__(self, ttl_seconds: float = 20.0):
        self.ttl = ttl_seconds
        self._lock = threading.Lock()
        self._fetch_lock = threading.Lock()
        self._value: T | None = None
        self._expires_at: float = 0.0
        self._has_value: bool = False

    def get_or_compute(self, compute_fn: Callable[[], T]) -> T:
        """
        Get cached value if valid, or compute it under a fetch lock to prevent stampedes.
        If compute_fn raises an exception, the exception is propagated and not cached.
        """
        now = time.monotonic()
        with self._lock:
            if self._has_value and now < self._expires_at:
                return self._value  # type: ignore

        # Cache miss or expired: serialize fetch to avoid thundering herd / stampede
        with self._fetch_lock:
            # Double-checked locking under fetch_lock
            now = time.monotonic()
            with self._lock:
                if self._has_value and now < self._expires_at:
                    return self._value  # type: ignore

            # Compute new value outside value lock so readers aren't blocked,
            # but under fetch_lock so only 1 thread fetches
            val = compute_fn()

            with self._lock:
                self._value = val
                self._expires_at = time.monotonic() + self.ttl
                self._has_value = True

            return val

    def invalidate(self) -> None:
        """Clear cached value immediately."""
        with self._lock:
            self._value = None
            self._expires_at = 0.0
            self._has_value = False

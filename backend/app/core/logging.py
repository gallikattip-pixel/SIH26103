"""Production structured logging and request correlation core."""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import re
import sys
from typing import Any
import uuid

# Context variable for thread/async-safe request correlation ID
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

REQUEST_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def sanitize_request_id(incoming_id: str | None) -> str:
    """
    Validate and sanitize incoming X-Request-ID.
    Preserves valid IDs (1-64 alphanumeric, hyphen, underscore).
    Generates a new UUID4 hex if missing, malformed, or oversized.
    """
    if incoming_id and isinstance(incoming_id, str):
        clean_id = incoming_id.strip()
        if clean_id and REQUEST_ID_REGEX.match(clean_id):
            return clean_id
    return uuid.uuid4().hex


def get_request_id() -> str:
    """Retrieve the current request ID from context."""
    return _request_id_ctx.get()


def set_request_id(req_id: str) -> None:
    """Set the current request ID in context."""
    _request_id_ctx.set(req_id)


class RequestIdFilter(logging.Filter):
    """Logging filter that injects the current request_id into all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production observability."""

    def format(self, record: logging.LogRecord) -> str:
        record_dict: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }

        # Include structured attributes if attached
        for key in ("method", "path", "status", "duration_ms", "scope", "identity_type", "retry_after"):
            val = getattr(record, key, None)
            if val is not None:
                record_dict[key] = val

        if record.exc_info:
            record_dict["exception"] = self.formatException(record.exc_info)

        return json.dumps(record_dict, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable text log formatter for development and testing."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def configure_logging(log_level: str = "INFO", log_format: str = "text") -> None:
    """
    Configure application-wide logging with request ID correlation.
    Supports 'text' (development) and 'json' (production) formats.
    """
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Choose formatter
    formatter: logging.Formatter
    if log_format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter()

    # Clear existing handlers to prevent duplicates during re-configuration/tests
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    # Configure our specific app loggers
    for logger_name in ("infraplus", "infraplus.main", "infraplus.access", "infraplus.security",
                        "infraplus.rate_limiter", "infraplus.firebase", "infraplus.gemini",
                        "infraplus.projects", "infraplus.storage"):
        sub_logger = logging.getLogger(logger_name)
        sub_logger.setLevel(numeric_level)

"""Configuration loader for INFRAPLUS backend."""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env from backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / ".env")

def _parse_int(var_name: str, default: int) -> int:
    """Safely parse integer environment variables with a fallback default."""
    raw = os.getenv(var_name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _parse_bool(var_name: str, default: bool) -> bool:
    """Safely parse boolean environment variables."""
    raw = os.getenv(var_name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in ("true", "1", "yes", "on")


# =========================================================
# ENVIRONMENT & LOGGING CONFIGURATION
# =========================================================
ALLOWED_ENVIRONMENTS = {"development", "test", "production"}
raw_env = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).strip().lower()
if raw_env not in ALLOWED_ENVIRONMENTS:
    raise ValueError(
        f"Invalid ENVIRONMENT '{raw_env}'. Allowed values: {sorted(list(ALLOWED_ENVIRONMENTS))}"
    )
ENVIRONMENT = raw_env


def is_production() -> bool:
    """Check if server is executing in production environment."""
    return ENVIRONMENT == "production"


def is_test() -> bool:
    """Check if server is executing in automated test environment."""
    return ENVIRONMENT == "test"


def is_development() -> bool:
    """Check if server is executing in local development environment."""
    return ENVIRONMENT == "development"


ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
raw_log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
LOG_LEVEL = raw_log_level if raw_log_level in ALLOWED_LOG_LEVELS else "INFO"

ALLOWED_LOG_FORMATS = {"text", "json"}
default_log_format = "json" if is_production() else "text"
raw_log_format = os.getenv("LOG_FORMAT", default_log_format).strip().lower()
LOG_FORMAT = raw_log_format if raw_log_format in ALLOWED_LOG_FORMATS else default_log_format

# =========================================================
# GEMINI CONFIGURATION
# =========================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()

def require_gemini_api_key() -> str:
    """Fail clearly if the Gemini API key is missing."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add your Gemini API key to .env."
        )
    return GEMINI_API_KEY

# =========================================================
# FIREBASE REALTIME DATABASE & ADMIN CONFIGURATION
# =========================================================
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "").strip()
FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "").strip()

# =========================================================
# DATA & STORAGE PATHS
# =========================================================
# Developer seed/reference dataset ONLY.
# NEVER used as a production fallback when Firebase is empty or unavailable.
PROJECTS_FILE = BACKEND_ROOT / "data" / "projects.json"
UPLOAD_DIR = BACKEND_ROOT / os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE_MB = _parse_int("MAX_FILE_SIZE_MB", 10)

# =========================================================
# SERVER & CORS
# =========================================================
PORT = _parse_int("PORT", 8000)
HOST = os.getenv("HOST", "127.0.0.1").strip()
raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
CORS_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# =========================================================
# RATE LIMITING & ABUSE PROTECTION CONFIGURATION
# =========================================================
RATE_LIMIT_ENABLED = _parse_bool("RATE_LIMIT_ENABLED", True)
TRUST_REVERSE_PROXY = _parse_bool("TRUST_REVERSE_PROXY", False)

# AI Chat limits: 15/60s (burst 5) for Auth, 5/60s (burst 2) for Anon
RATE_LIMIT_AI_AUTH_LIMIT = _parse_int("RATE_LIMIT_AI_AUTH_LIMIT", 15)
RATE_LIMIT_AI_AUTH_WINDOW = _parse_int("RATE_LIMIT_AI_AUTH_WINDOW", 60)
RATE_LIMIT_AI_AUTH_BURST = _parse_int("RATE_LIMIT_AI_AUTH_BURST", 5)

RATE_LIMIT_AI_ANON_LIMIT = _parse_int("RATE_LIMIT_AI_ANON_LIMIT", 5)
RATE_LIMIT_AI_ANON_WINDOW = _parse_int("RATE_LIMIT_AI_ANON_WINDOW", 60)
RATE_LIMIT_AI_ANON_BURST = _parse_int("RATE_LIMIT_AI_ANON_BURST", 2)

# Document Upload limits: 10/60s (burst 3), 50 MB/60s volume ceiling
RATE_LIMIT_UPLOAD_LIMIT = _parse_int("RATE_LIMIT_UPLOAD_LIMIT", 10)
RATE_LIMIT_UPLOAD_WINDOW = _parse_int("RATE_LIMIT_UPLOAD_WINDOW", 60)
RATE_LIMIT_UPLOAD_BURST = _parse_int("RATE_LIMIT_UPLOAD_BURST", 3)
RATE_LIMIT_UPLOAD_MAX_MB = _parse_int("RATE_LIMIT_UPLOAD_MAX_MB", 50)

# Project Creation limits: 10/hour (burst 2)
RATE_LIMIT_PROJECT_CREATE_LIMIT = _parse_int("RATE_LIMIT_PROJECT_CREATE_LIMIT", 10)
RATE_LIMIT_PROJECT_CREATE_WINDOW = _parse_int("RATE_LIMIT_PROJECT_CREATE_WINDOW", 3600)
RATE_LIMIT_PROJECT_CREATE_BURST = _parse_int("RATE_LIMIT_PROJECT_CREATE_BURST", 2)

# Document Deletion limits: 20/60s
RATE_LIMIT_DOC_DELETE_LIMIT = _parse_int("RATE_LIMIT_DOC_DELETE_LIMIT", 20)
RATE_LIMIT_DOC_DELETE_WINDOW = _parse_int("RATE_LIMIT_DOC_DELETE_WINDOW", 60)

# Public Read limits: 120/60s (safe for Project 360 concurrent loads)
RATE_LIMIT_READS_LIMIT = _parse_int("RATE_LIMIT_READS_LIMIT", 120)
RATE_LIMIT_READS_WINDOW = _parse_int("RATE_LIMIT_READS_WINDOW", 60)



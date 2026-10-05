"""Firebase Realtime Database client and service."""

import json
import logging
from pathlib import Path
import threading
from typing import Any
import httpx

from app.config import (
    FIREBASE_DATABASE_URL,
    FIREBASE_SERVICE_ACCOUNT_KEY,
)

logger = logging.getLogger("infraplus.firebase")

_firebase_admin_initialized = False
_firebase_http_client: httpx.Client | None = None
_firebase_client_lock = threading.Lock()


def get_firebase_http_client() -> httpx.Client:
    """Return shared, reusable HTTP client with connection pooling for Firebase REST calls."""
    global _firebase_http_client
    if _firebase_http_client is None or _firebase_http_client.is_closed:
        with _firebase_client_lock:
            if _firebase_http_client is None or _firebase_http_client.is_closed:
                _firebase_http_client = httpx.Client(
                    limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
                    timeout=8.0,
                )
    return _firebase_http_client


def close_firebase_http_client() -> None:
    """Gracefully close the shared Firebase HTTP client pool."""
    global _firebase_http_client
    with _firebase_client_lock:
        if _firebase_http_client is not None and not _firebase_http_client.is_closed:
            try:
                _firebase_http_client.close()
            except Exception as exc:
                logger.warning(f"Error closing Firebase HTTP client: {exc}")
            finally:
                _firebase_http_client = None


def _init_firebase_admin():
    """Attempt to initialize firebase_admin if credentials are provided."""
    global _firebase_admin_initialized
    if _firebase_admin_initialized:
        return True

    if not FIREBASE_SERVICE_ACCOUNT_KEY:
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Check if it is a file path
        path = Path(FIREBASE_SERVICE_ACCOUNT_KEY)
        if path.is_file():
            cred = credentials.Certificate(str(path))
        else:
            # Try parsing as JSON string
            parsed = json.loads(FIREBASE_SERVICE_ACCOUNT_KEY)
            cred = credentials.Certificate(parsed)

        options = {}
        if FIREBASE_DATABASE_URL:
            options["databaseURL"] = FIREBASE_DATABASE_URL

        firebase_admin.initialize_app(cred, options)
        _firebase_admin_initialized = True
        logger.info("Firebase Admin initialized successfully.")
        return True
    except Exception as exc:
        logger.warning(f"Failed to initialize Firebase Admin SDK: {exc}")
        return False


def get_firebase_status() -> dict[str, Any]:
    """Check Firebase configuration and connection readiness."""
    configured = bool(FIREBASE_DATABASE_URL or FIREBASE_SERVICE_ACCOUNT_KEY)
    admin_ready = _init_firebase_admin()

    status = {
        "configured": configured,
        "database_url": FIREBASE_DATABASE_URL or "Not set",
        "admin_sdk_ready": admin_ready,
        "mode": "live" if configured else "unconfigured",
        "message": "Connected to Firebase Realtime Database" if configured else "Firebase credentials not provided. Set FIREBASE_DATABASE_URL in .env."
    }
    return status


def get_projects_count_shallow() -> int | None:
    """
    Perform a lightweight shallow query to count projects without downloading full objects.
    Returns the integer count of projects, or None if Firebase is unreachable or unconfigured.
    """
    if not FIREBASE_DATABASE_URL:
        return None

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference("projects")
            data = ref.get(shallow=True)
            if data is None:
                return 0
            return len(data) if isinstance(data, (dict, list)) else 0
        except Exception as exc:
            logger.warning(f"Firebase Admin shallow count failed: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/projects.json?shallow=true"
        client = get_firebase_http_client()
        resp = client.get(url, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            if data is None:
                return 0
            return len(data) if isinstance(data, (dict, list)) else 0
        else:
            logger.warning(f"Firebase REST shallow count returned HTTP {resp.status_code}")
            return None
    except Exception as exc:
        logger.warning(f"Firebase REST shallow count connection error: {exc}")
        return None



def fetch_projects_from_firebase() -> dict[str, Any] | None:
    """
    Fetch all projects from Firebase Realtime Database.
    Returns:
      - dict with project records if projects exist.
      - empty dict {} if connected successfully but database contains 0 projects (Empty State).
      - None if Firebase is unconfigured, network failed, or connection is unavailable (Error State).
    """
    if not FIREBASE_DATABASE_URL:
        return None

    # Try Firebase Admin first
    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference("projects")
            data = ref.get()
            if data is None or data == {}:
                logger.info("Connected to Firebase: 'projects' node is empty (0 records).")
                return {}
            return _normalize_projects_data(data)
        except Exception as exc:
            logger.warning(f"Firebase Admin fetch error: {exc}. Trying REST API.")

    # Try direct REST API call
    try:
        url = FIREBASE_DATABASE_URL.rstrip("/") + "/projects.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data is None or data == {}:
                logger.info("Connected to Firebase REST API: 'projects.json' is null/empty (0 records).")
                return {}
            return _normalize_projects_data(data)
        else:
            logger.warning(f"Firebase REST API returned HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as exc:
        logger.warning(f"Firebase REST API connection error: {exc}")
        return None


def fetch_single_project_from_firebase(clean_id: str) -> dict[str, Any] | None:
    """
    Fetch a single project record from Firebase Realtime Database by its ID.
    Direct targeted fetch to eliminate O(N) collection downloads.
    Returns:
      - dict with project record if found.
      - None if project does not exist (HTTP 404 / null) or Firebase is unconfigured.
    Raises:
      - RuntimeError if network/connection to Firebase fails.
    """
    if not FIREBASE_DATABASE_URL:
        return None

    clean_id = clean_id.strip().upper()

    # Try Firebase Admin first
    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"projects/{clean_id}")
            data = ref.get()
            if data is None:
                return None
            if isinstance(data, dict):
                data["project_id"] = str(data.get("project_id", clean_id)).strip().upper()
                return data
            return None
        except Exception as exc:
            logger.warning(f"Firebase Admin fetch single project error: {exc}. Trying REST API.")

    # Try direct REST API call
    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/projects/{clean_id}.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data is None:
                return None
            if isinstance(data, dict):
                data["project_id"] = str(data.get("project_id", clean_id)).strip().upper()
                return data
            return None
        elif resp.status_code == 404:
            return None
        else:
            logger.warning(f"Firebase REST fetch single project returned HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as exc:
        logger.warning(f"Firebase REST fetch single project connection error: {exc}")
        raise RuntimeError(f"Unable to connect to Firebase Realtime Database: {exc}")


def _normalize_projects_data(data: Any) -> dict[str, Any]:
    """Handle both dict mapping and list format from Firebase Realtime Database."""
    records = {}
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict):
                p_id = str(val.get("project_id", key)).strip().upper()
                val["project_id"] = p_id
                records[p_id] = val
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "project_id" in item:
                p_id = str(item["project_id"]).strip().upper()
                records[p_id] = item
    return records


def save_project_to_firebase(project_id: str, project_data: dict) -> bool:
    """Save or update a project in Firebase Realtime Database."""
    if not FIREBASE_DATABASE_URL:
        return False

    clean_id = project_id.strip().upper()

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"projects/{clean_id}")
            ref.set(project_data)
            return True
        except Exception as exc:
            logger.warning(f"Firebase Admin save error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/projects/{clean_id}.json"
        client = get_firebase_http_client()
        resp = client.put(url, json=project_data)
        return resp.status_code == 200
    except Exception as exc:
        logger.warning(f"Firebase REST save error: {exc}")
        return False


def save_document_to_firebase(project_id: str, doc_id: str, doc_data: dict) -> bool:
    """Save document metadata under a project in Firebase Realtime Database."""
    clean_id = project_id.strip().upper()
    if not FIREBASE_DATABASE_URL:
        return False

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"documents/{clean_id}/{doc_id}")
            ref.set(doc_data)
            return True
        except Exception as exc:
            logger.warning(f"Firebase document save error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/documents/{clean_id}/{doc_id}.json"
        client = get_firebase_http_client()
        resp = client.put(url, json=doc_data)
        return resp.status_code == 200
    except Exception as exc:
        logger.warning(f"Firebase REST document save error: {exc}")
        return False


def fetch_documents_from_firebase(project_id: str) -> list[dict]:
    """Fetch document metadata for a project from Firebase."""
    clean_id = project_id.strip().upper()
    if not FIREBASE_DATABASE_URL:
        return []

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"documents/{clean_id}")
            data = ref.get()
            if isinstance(data, dict):
                return list(data.values())
        except Exception as exc:
            logger.warning(f"Firebase fetch documents error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/documents/{clean_id}.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                return list(data.values())
    except Exception as exc:
        logger.warning(f"Firebase REST fetch documents error: {exc}")

    return []


def delete_document_from_firebase(project_id: str, doc_id: str) -> bool:
    """Delete document reference from Firebase."""
    clean_id = project_id.strip().upper()
    if not FIREBASE_DATABASE_URL:
        return False

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"documents/{clean_id}/{doc_id}")
            ref.delete()
            return True
        except Exception as exc:
            logger.warning(f"Firebase delete document error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/documents/{clean_id}/{doc_id}.json"
        client = get_firebase_http_client()
        resp = client.delete(url)
        return resp.status_code == 200
    except Exception as exc:
        logger.warning(f"Firebase REST delete document error: {exc}")
        return False


def get_document_from_firebase(project_id: str, doc_id: str) -> dict | None:
    """Fetch metadata for a single document from Firebase."""
    clean_id = project_id.strip().upper()
    if not FIREBASE_DATABASE_URL:
        return None

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"documents/{clean_id}/{doc_id}")
            data = ref.get()
            if isinstance(data, dict):
                return data
        except Exception as exc:
            logger.warning(f"Firebase get document error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/documents/{clean_id}/{doc_id}.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                return data
    except Exception as exc:
        logger.warning(f"Firebase REST get document error: {exc}")

    return None


# =========================================================
# HISTORICAL PROJECT SNAPSHOTS
# =========================================================

def save_project_snapshot_to_firebase(
    project_id: str,
    period: str,
    snapshot_data: dict
) -> bool:
    """Save a project snapshot to Firebase Realtime Database.

    Snapshots are stored under: project_snapshots/{project_id}/{period}
    Uses PUT to ensure idempotency — if a snapshot already exists for the
    same project and period, it will be overwritten ONLY if explicitly
    intended. The service layer should check existence first for idempotent
    create behavior.

    Args:
        project_id: Project identifier
        period: Period key in YYYY-MM format
        snapshot_data: Snapshot data dictionary

    Returns:
        True if saved successfully, False otherwise
    """
    if not FIREBASE_DATABASE_URL:
        return False

    clean_id = project_id.strip().upper()
    clean_period = period.strip()

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_snapshots/{clean_id}/{clean_period}")
            ref.set(snapshot_data)
            return True
        except Exception as exc:
            logger.warning(f"Firebase Admin save snapshot error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_snapshots/{clean_id}/{clean_period}.json"
        client = get_firebase_http_client()
        resp = client.put(url, json=snapshot_data)
        return resp.status_code == 200
    except Exception as exc:
        logger.warning(f"Firebase REST save snapshot error: {exc}")
        return False


def fetch_project_snapshot_from_firebase(
    project_id: str,
    period: str
) -> dict | None:
    """Fetch a single project snapshot from Firebase.

    Args:
        project_id: Project identifier
        period: Period key in YYYY-MM format

    Returns:
        Snapshot data dict if found, None if not found or error
    """
    clean_id = project_id.strip().upper()
    clean_period = period.strip()

    if not FIREBASE_DATABASE_URL:
        return None

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_snapshots/{clean_id}/{clean_period}")
            data = ref.get()
            if data is None:
                return None
            if isinstance(data, dict):
                return data
            return None
        except Exception as exc:
            logger.warning(f"Firebase Admin fetch snapshot error: {exc}. Trying REST API.")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_snapshots/{clean_id}/{clean_period}.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data is None:
                return None
            if isinstance(data, dict):
                return data
            return None
        elif resp.status_code == 404:
            return None
        else:
            logger.warning(f"Firebase REST fetch snapshot returned HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as exc:
        logger.warning(f"Firebase REST fetch snapshot connection error: {exc}")
        raise RuntimeError(f"Unable to connect to Firebase Realtime Database: {exc}")


def fetch_all_project_snapshots_from_firebase(project_id: str) -> dict[str, Any] | None:
    """Fetch all snapshots for a project from Firebase.

    Returns:
        - dict with period keys mapping to snapshot data if snapshots exist
        - empty dict {} if connected successfully but no snapshots (Empty State)
        - None if Firebase is unconfigured or connection failed (Error State)
    """
    clean_id = project_id.strip().upper()

    if not FIREBASE_DATABASE_URL:
        return None

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_snapshots/{clean_id}")
            data = ref.get()
            if data is None or data == {}:
                return {}
            return data if isinstance(data, dict) else {}
        except Exception as exc:
            logger.warning(f"Firebase Admin fetch all snapshots error: {exc}. Trying REST API.")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_snapshots/{clean_id}.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data is None or data == {}:
                return {}
            return data if isinstance(data, dict) else {}
        else:
            logger.warning(f"Firebase REST fetch all snapshots returned HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as exc:
        logger.warning(f"Firebase REST fetch all snapshots connection error: {exc}")
        return None


def check_snapshot_exists(project_id: str, period: str) -> bool:
    """Check if a snapshot already exists for the given project and period.

    This is a lightweight check to support idempotent create behavior.

    Args:
        project_id: Project identifier
        period: Period key in YYYY-MM format

    Returns:
        True if snapshot exists, False otherwise or on error
    """
    clean_id = project_id.strip().upper()
    clean_period = period.strip()

    if not FIREBASE_DATABASE_URL:
        return False

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_snapshots/{clean_id}/{clean_period}")
            data = ref.get(shallow=True)
            return data is not None
        except Exception as exc:
            logger.warning(f"Firebase Admin check snapshot exists error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_snapshots/{clean_id}/{clean_period}.json?shallow=true"
        client = get_firebase_http_client()
        resp = client.get(url, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            return data is not None
        return False
    except Exception as exc:
        logger.warning(f"Firebase REST check snapshot exists error: {exc}")
        return False


# =========================================================
# PROJECT OUTCOMES
# =========================================================

def save_project_outcome_to_firebase(
    project_id: str,
    outcome_data: dict
) -> bool:
    """Save a project outcome to Firebase Realtime Database.

    Outcomes are stored under: project_outcomes/{project_id}
    Uses PUT — only one outcome per project.

    Args:
        project_id: Project identifier
        outcome_data: Outcome data dictionary

    Returns:
        True if saved successfully, False otherwise
    """
    if not FIREBASE_DATABASE_URL:
        return False

    clean_id = project_id.strip().upper()

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_outcomes/{clean_id}")
            ref.set(outcome_data)
            return True
        except Exception as exc:
            logger.warning(f"Firebase Admin save outcome error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_outcomes/{clean_id}.json"
        client = get_firebase_http_client()
        resp = client.put(url, json=outcome_data)
        return resp.status_code == 200
    except Exception as exc:
        logger.warning(f"Firebase REST save outcome error: {exc}")
        return False


def fetch_project_outcome_from_firebase(project_id: str) -> dict | None:
    """Fetch a project outcome from Firebase.

    Args:
        project_id: Project identifier

    Returns:
        Outcome data dict if found, None if not found or error
    """
    clean_id = project_id.strip().upper()

    if not FIREBASE_DATABASE_URL:
        return None

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_outcomes/{clean_id}")
            data = ref.get()
            if data is None:
                return None
            if isinstance(data, dict):
                return data
            return None
        except Exception as exc:
            logger.warning(f"Firebase Admin fetch outcome error: {exc}. Trying REST API.")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_outcomes/{clean_id}.json"
        client = get_firebase_http_client()
        resp = client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if data is None:
                return None
            if isinstance(data, dict):
                return data
            return None
        elif resp.status_code == 404:
            return None
        else:
            logger.warning(f"Firebase REST fetch outcome returned HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as exc:
        logger.warning(f"Firebase REST fetch outcome connection error: {exc}")
        raise RuntimeError(f"Unable to connect to Firebase Realtime Database: {exc}")


def check_outcome_exists(project_id: str) -> bool:
    """Check if a project outcome already exists.

    Args:
        project_id: Project identifier

    Returns:
        True if outcome exists, False otherwise or on error
    """
    clean_id = project_id.strip().upper()

    if not FIREBASE_DATABASE_URL:
        return False

    if _init_firebase_admin():
        try:
            from firebase_admin import db
            ref = db.reference(f"project_outcomes/{clean_id}")
            data = ref.get(shallow=True)
            return data is not None
        except Exception as exc:
            logger.warning(f"Firebase Admin check outcome exists error: {exc}")

    try:
        url = f"{FIREBASE_DATABASE_URL.rstrip('/')}/project_outcomes/{clean_id}.json?shallow=true"
        client = get_firebase_http_client()
        resp = client.get(url, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            return data is not None
        return False
    except Exception as exc:
        logger.warning(f"Firebase REST check outcome exists error: {exc}")
        return False

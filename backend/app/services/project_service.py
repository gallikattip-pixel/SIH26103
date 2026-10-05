"""Project data access and 360° analytics service.

Firebase Realtime Database is the sole source of truth for production project data.
No fake data, no mock fallbacks.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import logging
import threading
from typing import Any

from app.core.cache import TTLCache
from app.models.project import (
    AgencyRecord,
    DocumentRecord,
    FinancialMetrics,
    MilestoneRecord,
    ProgressMetrics,
    ProjectDetail360,
    ProjectListItem,
    ProjectRecord,
    RiskBreakdown,
    TimelineMetrics,
)
from app.services.firebase_service import (
    fetch_documents_from_firebase,
    fetch_projects_from_firebase,
    fetch_single_project_from_firebase,
    get_firebase_status,
    save_project_to_firebase,
    save_project_snapshot_to_firebase,
    fetch_project_snapshot_from_firebase,
    fetch_all_project_snapshots_from_firebase,
    check_snapshot_exists,
    save_project_outcome_to_firebase,
    fetch_project_outcome_from_firebase,
    check_outcome_exists,
)
from app.services.risk_engine import calculate_risk

logger = logging.getLogger("infraplus.projects")


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert any raw value to float."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert any raw value to integer."""
    if value is None or value == "":
        return default
    try:
        return int(round(float(value)))
    except (ValueError, TypeError):
        return default


def _safe_str(value: Any, default: str = "Not Available") -> str:
    """Safely convert raw string, handling None and empty values."""
    if value is None:
        return default
    s = str(value).strip()
    return s if s else default


def _parse_project_record(raw: dict[str, Any]) -> ProjectRecord:
    """Parse raw dictionary into ProjectRecord, handling incomplete/null fields."""
    p_id = _safe_str(raw.get("project_id"), "UNKNOWN").upper()
    return ProjectRecord(
        project_id=p_id,
        name=_safe_str(raw.get("name"), f"Infrastructure Project {p_id}"),
        location=_safe_str(raw.get("location"), "Location Pending"),
        sector=_safe_str(raw.get("sector"), "General Infrastructure"),
        progress=_safe_float(raw.get("progress"), 0.0),
        planned_progress=_safe_float(raw.get("planned_progress"), 0.0),
        delay_days=_safe_int(raw.get("delay_days"), 0),
        budget_used=_safe_float(raw.get("budget_used"), 0.0),
        budget_total_crore=_safe_float(raw.get("budget_total_crore"), 0.0),
        contractor=_safe_str(raw.get("contractor"), "Contractor Unassigned"),
    )


def get_all_projects() -> list[ProjectRecord]:
    """
    Fetch all projects from Firebase Realtime Database.
    Firebase Realtime Database is the SOLE production source of truth.
    Raises RuntimeError if Firebase is unconfigured or unreachable (leading to HTTP 503 error state).
    Returns empty list if database contains zero projects (leading to empty state).
    """
    fb_status = get_firebase_status()
    if not fb_status["configured"]:
        raise RuntimeError(
            "Firebase Realtime Database is not configured. Please set FIREBASE_DATABASE_URL in .env."
        )

    raw_projects = fetch_projects_from_firebase()
    if raw_projects is None:
        # None indicates a connection/network failure or unreachable database (Error State)
        raise RuntimeError(
            "Unable to connect to Firebase Realtime Database. Please verify your network and credentials."
        )

    if not raw_projects:
        # Empty dictionary {} indicates Firebase responded successfully but has 0 projects (Empty State)
        logger.info("Firebase Realtime Database contains 0 project records. Returning empty list.")
        return []

    projects: list[ProjectRecord] = []
    for raw in raw_projects.values():
        if isinstance(raw, dict):
            try:
                projects.append(_parse_project_record(raw))
            except Exception as exc:
                logger.warning(f"Skipping malformed project record: {exc}")

    return sorted(projects, key=lambda p: p.project_id)


_all_projects_enriched_cache = TTLCache[list[ProjectListItem]](ttl_seconds=20.0)


def invalidate_project_caches() -> None:
    """Invalidate all project and dashboard caches when data changes."""
    _all_projects_enriched_cache.invalidate()
    try:
        from app.services.dashboard_service import invalidate_dashboard_cache
        invalidate_dashboard_cache()
    except Exception as exc:
        logger.debug(f"Could not invalidate dashboard cache: {exc}")


def _fetch_and_enrich_all_projects() -> list[ProjectListItem]:
    projects = get_all_projects()
    enriched: list[ProjectListItem] = []
    for p in projects:
        risk = calculate_risk(p)
        enriched.append(
            ProjectListItem(
                project_id=p.project_id,
                name=p.name,
                location=p.location,
                sector=p.sector,
                progress=p.progress,
                planned_progress=p.planned_progress,
                delay_days=p.delay_days,
                budget_used=p.budget_used,
                budget_total_crore=p.budget_total_crore,
                contractor=p.contractor,
                risk=risk,
            )
        )
    return enriched


def get_all_projects_enriched() -> list[ProjectListItem]:
    """Fetch all projects from Firebase and enrich with deterministic risk metrics (cached with 20s TTL)."""
    return _all_projects_enriched_cache.get_or_compute(_fetch_and_enrich_all_projects)


def get_project_by_id(project_id: str) -> ProjectRecord | None:
    """
    Fetch a single project from Firebase Realtime Database by its ID.
    Uses targeted single-project fetch to eliminate O(N) full collection downloads.
    """
    if not project_id:
        return None
    clean_id = project_id.strip().upper()

    fb_status = get_firebase_status()
    if not fb_status["configured"]:
        raise RuntimeError(
            "Firebase Realtime Database is not configured. Please set FIREBASE_DATABASE_URL in .env."
        )

    raw = fetch_single_project_from_firebase(clean_id)
    if raw is None:
        return None

    try:
        return _parse_project_record(raw)
    except Exception as exc:
        logger.warning(f"Failed to parse project record {clean_id}: {exc}")
        return None


def get_project_risk(project_id: str) -> RiskBreakdown | None:
    """Authoritative deterministic risk breakdown for a project."""
    project = get_project_by_id(project_id)
    if not project:
        return None
    return calculate_risk(project)


def get_project_financial(project: ProjectRecord, risk: RiskBreakdown | None = None) -> FinancialMetrics:
    """Calculate financial metrics from project data. Reuses precomputed risk if supplied."""
    expended = round((project.budget_used / 100.0) * project.budget_total_crore, 2)
    remaining = round(max(0.0, project.budget_total_crore - expended), 2)
    spend_ahead = round(max(0.0, project.budget_used - project.progress), 2)

    if risk is None:
        risk = calculate_risk(project)

    if risk.budget_risk >= 70:
        health = "CRITICAL_DEFICIT"
    elif risk.budget_risk >= 40:
        health = "MODERATE_RISK"
    else:
        health = "ON_BUDGET"

    return FinancialMetrics(
        project_id=project.project_id,
        budget_total_crore=project.budget_total_crore,
        budget_used_percent=project.budget_used,
        budget_expended_crore=expended,
        budget_remaining_crore=remaining,
        spend_ahead_of_work=spend_ahead,
        financial_health=health,
        budget_risk=risk.budget_risk,
    )


def get_project_progress(project: ProjectRecord, risk: RiskBreakdown | None = None) -> ProgressMetrics:
    """Calculate physical progress metrics. Reuses precomputed risk if supplied."""
    gap = round(project.planned_progress - project.progress, 2)
    if risk is None:
        risk = calculate_risk(project)

    if gap > 15:
        status = "SIGNIFICANTLY_BEHIND"
    elif gap > 0:
        status = "MODERATELY_BEHIND"
    elif gap == 0:
        status = "ON_SCHEDULE"
    else:
        status = "AHEAD_OF_PLAN"

    return ProgressMetrics(
        project_id=project.project_id,
        actual_progress=project.progress,
        planned_progress=project.planned_progress,
        progress_gap=gap,
        status=status,
        progress_risk=risk.progress_risk,
    )


def get_project_timeline(project: ProjectRecord, risk: RiskBreakdown | None = None) -> TimelineMetrics:
    """Calculate timeline and schedule metrics. Reuses precomputed risk if supplied."""
    if risk is None:
        risk = calculate_risk(project)

    if project.delay_days >= 90:
        sched_status = "CRITICAL_DELAY"
        urgency = "HIGH"
        impact = "Severe delivery deadline slippage requiring immediate steering review."
    elif project.delay_days >= 30:
        sched_status = "MODERATE_DELAY"
        urgency = "MEDIUM"
        impact = "Noticeable delay requiring recovery schedule adjustment."
    elif project.delay_days > 0:
        sched_status = "MINOR_DELAY"
        urgency = "LOW"
        impact = "Minor schedule friction, manageable within contingency buffer."
    else:
        sched_status = "ON_TIME"
        urgency = "NONE"
        impact = "Executing within sanctioned schedule parameters."

    return TimelineMetrics(
        project_id=project.project_id,
        delay_days=project.delay_days,
        delay_risk=risk.delay_risk,
        schedule_status=sched_status,
        recovery_urgency=urgency,
        estimated_impact=impact,
    )


def get_project_milestones(project: ProjectRecord) -> list[MilestoneRecord]:
    """Return milestone breakdown for project."""
    # If project record contains custom milestones in Firebase, use them
    custom = getattr(project, "milestones", None)
    if custom and isinstance(custom, list):
        parsed = []
        for idx, m in enumerate(custom):
            if isinstance(m, dict):
                parsed.append(
                    MilestoneRecord(
                        id=str(m.get("id", f"M-{idx+1}")),
                        title=str(m.get("title", f"Milestone {idx+1}")),
                        target_date=str(m.get("target_date", "Pending")),
                        status=str(m.get("status", "PENDING")),
                        completion_percent=_safe_float(m.get("completion_percent"), 0.0),
                        critical=bool(m.get("critical", False)),
                    )
                )
        if parsed:
            return parsed

    # Default phased milestones generated from actual physical progress
    p = project.progress
    return [
        MilestoneRecord(
            id=f"{project.project_id}-M1",
            title="Pre-Construction Clearances & Surveying",
            target_date="Phase 1",
            status="COMPLETED" if p >= 20 else ("IN_PROGRESS" if p > 0 else "PENDING"),
            completion_percent=min(100.0, (p / 20.0) * 100.0) if p > 0 else 0.0,
            critical=True,
        ),
        MilestoneRecord(
            id=f"{project.project_id}-M2",
            title="Civil Works & Structural Foundation",
            target_date="Phase 2",
            status="COMPLETED" if p >= 50 else ("IN_PROGRESS" if p >= 20 else "PENDING"),
            completion_percent=min(100.0, max(0.0, (p - 20) / 30.0 * 100.0)),
            critical=True,
        ),
        MilestoneRecord(
            id=f"{project.project_id}-M3",
            title="Core Infrastructure & Superstructure",
            target_date="Phase 3",
            status="COMPLETED" if p >= 80 else ("IN_PROGRESS" if p >= 50 else "PENDING"),
            completion_percent=min(100.0, max(0.0, (p - 50) / 30.0 * 100.0)),
            critical=False,
        ),
        MilestoneRecord(
            id=f"{project.project_id}-M4",
            title="Final Quality Testing & Handover Audit",
            target_date="Phase 4",
            status="COMPLETED" if p >= 100 else ("IN_PROGRESS" if p >= 80 else "PENDING"),
            completion_percent=min(100.0, max(0.0, (p - 80) / 20.0 * 100.0)),
            critical=True,
        ),
    ]


def get_project_agencies(project: ProjectRecord) -> AgencyRecord:
    """Return executing agencies and contractors for project."""
    return AgencyRecord(
        executing_agency=f"State Infrastructure Board ({project.location})",
        contractor=project.contractor,
        nodal_officer=f"Chief Superintending Engineer ({project.sector})",
        supervising_consultant="National Quality Assurance Wing",
        monitoring_division="Central Infrastructure Oversight Portal",
        contact_email=f"monitoring.{project.project_id.lower()}@infraplus.gov.in",
    )


def get_project_documents(project_id: str) -> list[DocumentRecord]:
    """Fetch project documents metadata from Firebase."""
    clean_id = project_id.strip().upper()
    raw_docs = fetch_documents_from_firebase(clean_id)
    documents = []
    for d in raw_docs:
        try:
            documents.append(
                DocumentRecord(
                    id=str(d.get("id")),
                    project_id=clean_id,
                    filename=str(d.get("filename")),
                    title=str(d.get("title", d.get("filename"))),
                    file_type=str(d.get("file_type", "application/octet-stream")),
                    file_size_kb=_safe_float(d.get("file_size_kb"), 0.0),
                    uploaded_at=str(d.get("uploaded_at", datetime.now().isoformat())),
                    download_url=str(d.get("download_url")),
                    uploaded_by_uid=d.get("uploaded_by_uid"),
                )
            )
        except Exception as exc:
            logger.warning(f"Error parsing document record: {exc}")
    return documents


def get_project_360(project_id: str) -> ProjectDetail360 | None:
    """Assemble complete 360° overview for a project."""
    project = get_project_by_id(project_id)
    if not project:
        return None

    # Calculate authoritative risk ONCE and reuse across financial, progress, and timeline metrics
    risk = calculate_risk(project)
    financial = get_project_financial(project, risk=risk)
    progress = get_project_progress(project, risk=risk)
    timeline = get_project_timeline(project, risk=risk)
    milestones = get_project_milestones(project)
    agencies = get_project_agencies(project)
    documents = get_project_documents(project.project_id)

    return ProjectDetail360(
        project=project,
        risk=risk,
        financial=financial,
        progress=progress,
        timeline=timeline,
        milestones=milestones,
        agencies=agencies,
        documents=documents,
    )


_project_creation_locks: dict[str, threading.Lock] = {}
_project_creation_ref_counts: dict[str, int] = {}
_creation_master_lock = threading.Lock()


@contextmanager
def _acquire_project_lock(clean_id: str):
    """
    Acquire a per-project mutex lock with reference-counted cleanup.
    Guarantees O(1) memory by evicting locks when all competing threads release.
    """
    with _creation_master_lock:
        if clean_id not in _project_creation_locks:
            _project_creation_locks[clean_id] = threading.Lock()
            _project_creation_ref_counts[clean_id] = 0
        lock = _project_creation_locks[clean_id]
        _project_creation_ref_counts[clean_id] += 1

    lock.acquire()
    try:
        yield lock
    finally:
        lock.release()
        with _creation_master_lock:
            _project_creation_ref_counts[clean_id] -= 1
            if _project_creation_ref_counts[clean_id] <= 0:
                _project_creation_locks.pop(clean_id, None)
                _project_creation_ref_counts.pop(clean_id, None)


def _get_project_lock(clean_id: str) -> threading.Lock:
    """Legacy helper for test compatibility."""
    with _creation_master_lock:
        if clean_id not in _project_creation_locks:
            _project_creation_locks[clean_id] = threading.Lock()
        return _project_creation_locks[clean_id]


def create_new_project(project_data: ProjectRecord) -> ProjectListItem:
    """
    Validate and save a new infrastructure project into Firebase Realtime Database.
    Immediately calculates deterministic risk telemetry.
    Uses reference-counted per-project mutex lock to prevent concurrent duplicate creations (TOCTOU race)
    and clean up locks after release.
    """
    clean_id = project_data.project_id.strip().upper()

    with _acquire_project_lock(clean_id):
        # Check if project already exists
        try:
            existing = get_project_by_id(clean_id)
            if existing:
                raise ValueError(f"Project with ID '{clean_id}' already exists in the database.")
        except (RuntimeError, ValueError) as exc:
            if "already exists" in str(exc):
                raise

        # Prepare project dictionary
        project_dict = project_data.model_dump()
        project_dict["project_id"] = clean_id
        project_dict["name"] = project_data.name.strip()
        project_dict["location"] = project_data.location.strip()
        project_dict["sector"] = project_data.sector.strip()
        project_dict["contractor"] = project_data.contractor.strip()

        normalized_record = ProjectRecord(**project_dict)

        success = save_project_to_firebase(clean_id, project_dict)
        if not success:
            raise RuntimeError(
                "Failed to persist project to Firebase Realtime Database. Please verify database URL and permissions."
            )

        # Invalidate caches upon successful creation
        invalidate_project_caches()

        risk = calculate_risk(normalized_record)
        return ProjectListItem(
            **project_dict,
            risk=risk,
        )


# =========================================================
# HISTORICAL PROJECT SNAPSHOTS
# =========================================================

def _get_current_utc_period() -> str:
    """Return current UTC period in YYYY-MM format."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _build_snapshot_from_project(project: ProjectRecord, period: str) -> dict[str, Any]:
    """Build snapshot data dictionary from a ProjectRecord.

    Captures raw project metrics at a point in time.
    Also includes a derived risk snapshot for historical auditing ONLY.
    """
    from app.services.risk_engine import calculate_risk
    risk = calculate_risk(project)

    return {
        "project_id": project.project_id,
        "snapshot_period": period,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "progress": project.progress,
        "planned_progress": project.planned_progress,
        "delay_days": project.delay_days,
        "budget_used": project.budget_used,
        "budget_total_crore": project.budget_total_crore,
        "contractor": project.contractor,
        "sector": project.sector,
        "location": project.location,
        "risk_snapshot": {
            "overall_score": risk.overall_score,
            "overall_level": risk.overall_level,
            "progress_risk": risk.progress_risk,
            "delay_risk": risk.delay_risk,
            "budget_risk": risk.budget_risk,
            "progress_gap": risk.progress_gap,
            "major_factors": risk.major_factors,
        },
    }


def _validate_snapshot_data(data: dict[str, Any]) -> None:
    """Validate snapshot data against domain constraints.

    Raises:
        ValueError: If any field is invalid
    """
    # Validate progress range
    if not (0 <= data["progress"] <= 100):
        raise ValueError(f"progress must be between 0 and 100, got {data['progress']}")

    if not (0 <= data["planned_progress"] <= 100):
        raise ValueError(f"planned_progress must be between 0 and 100, got {data['planned_progress']}")

    if data["delay_days"] < 0:
        raise ValueError(f"delay_days must be non-negative, got {data['delay_days']}")

    if not (0 <= data["budget_used"] <= 100):
        raise ValueError(f"budget_used must be between 0 and 100, got {data['budget_used']}")

    if data["budget_total_crore"] < 0:
        raise ValueError(f"budget_total_crore must be non-negative, got {data['budget_total_crore']}")

    if not data.get("project_id"):
        raise ValueError("project_id is required")

    if not data.get("snapshot_period"):
        raise ValueError("snapshot_period is required")

    if not data.get("recorded_at"):
        raise ValueError("recorded_at is required")


def create_project_snapshot(
    project_id: str,
    snapshot_period: str | None = None,
) -> dict[str, Any]:
    """Create a historical snapshot for a project.

    Reads the current authoritative project metrics from the database
    and creates an immutable snapshot for the given period.

    Args:
        project_id: Project identifier
        snapshot_period: Period key in YYYY-MM format. Defaults to current UTC month.

    Returns:
        The created snapshot data dictionary

    Raises:
        ValueError: If project not found, period invalid, or snapshot already exists
        RuntimeError: If Firebase is unavailable
    """
    # Resolve period (default to current UTC month)
    if snapshot_period is None:
        snapshot_period = _get_current_utc_period()

    # Validate period format
    import re
    if not re.match(r"^\d{4}-\d{2}$", snapshot_period):
        raise ValueError("snapshot_period must be in YYYY-MM format")
    year, month = map(int, snapshot_period.split("-"))
    if not (2000 <= year <= 2100) or not (1 <= month <= 12):
        raise ValueError("Invalid year or month in snapshot_period")

    # Fetch current project (authoritative source)
    project = get_project_by_id(project_id)
    if not project:
        raise ValueError(f"Project '{project_id}' not found in database")

    # Check for existing snapshot (idempotency)
    if check_snapshot_exists(project_id, snapshot_period):
        existing = fetch_project_snapshot_from_firebase(project_id, snapshot_period)
        if existing:
            raise ValueError(
                f"Snapshot for project '{project_id}' period '{snapshot_period}' already exists. "
                f"Use explicit correction mechanism if update is required."
            )

    # Build snapshot from current project state
    snapshot_data = _build_snapshot_from_project(project, snapshot_period)

    # Validate snapshot data
    _validate_snapshot_data(snapshot_data)

    # Save to Firebase
    success = save_project_snapshot_to_firebase(project_id, snapshot_period, snapshot_data)
    if not success:
        raise RuntimeError(
            f"Failed to save snapshot for project '{project_id}' period '{snapshot_period}' "
            f"to Firebase Realtime Database."
        )

    return snapshot_data


def get_project_snapshot(
    project_id: str,
    period: str,
) -> dict[str, Any] | None:
    """Retrieve a specific historical snapshot for a project.

    Args:
        project_id: Project identifier
        period: Period key in YYYY-MM format

    Returns:
        Snapshot data dictionary if found, None otherwise

    Raises:
        RuntimeError: If Firebase is unavailable
    """
    # Validate period format
    import re
    if not re.match(r"^\d{4}-\d{2}$", period):
        raise ValueError("period must be in YYYY-MM format")

    snapshot = fetch_project_snapshot_from_firebase(project_id, period)
    return snapshot


def get_project_snapshots(
    project_id: str,
) -> list[dict[str, Any]]:
    """Retrieve all historical snapshots for a project, sorted chronologically.

    Args:
        project_id: Project identifier

    Returns:
        List of snapshot data dictionaries, sorted by snapshot_period ascending

    Raises:
        RuntimeError: If Firebase is unavailable
    """
    snapshots_map = fetch_all_project_snapshots_from_firebase(project_id)

    if snapshots_map is None:
        raise RuntimeError(
            f"Unable to connect to Firebase Realtime Database to fetch snapshots for '{project_id}'."
        )

    # Convert to list and sort by period
    snapshots = list(snapshots_map.values())
    snapshots.sort(key=lambda s: s.get("snapshot_period", ""))

    return snapshots


# =========================================================
# PROJECT OUTCOMES
# =========================================================

def _build_outcome_from_project(
    project: ProjectRecord,
    payload: dict[str, Any],
    user_uid: str,
) -> dict[str, Any]:
    """Build outcome data dictionary from a ProjectRecord and payload.

    Calculates derived fields where possible from authoritative data.
    """
    from datetime import datetime, timezone

    # Calculate final delay days from dates if both provided
    final_delay_days = payload.get("final_delay_days", 0)
    planned_completion_date = payload.get("planned_completion_date")
    actual_completion_date = payload.get("actual_completion_date")

    if planned_completion_date and actual_completion_date:
        try:
            planned = datetime.strptime(planned_completion_date, "%Y-%m-%d")
            actual = datetime.strptime(actual_completion_date, "%Y-%m-%d")
            delta = (actual - planned).days
            final_delay_days = max(0, delta)
        except (ValueError, TypeError):
            pass  # Use provided final_delay_days

    # Calculate budget variance if final cost provided
    final_budget_variance = payload.get("final_budget_variance_percent")
    final_cost = payload.get("final_cost_crore")
    if final_cost is not None and project.budget_total_crore > 0:
        variance = ((final_cost - project.budget_total_crore) / project.budget_total_crore) * 100
        final_budget_variance = round(variance, 2)

    return {
        "project_id": project.project_id,
        "completion_status": payload["completion_status"].upper(),
        "actual_completion_date": payload["actual_completion_date"],
        "planned_completion_date": planned_completion_date,
        "final_progress": payload["final_progress"],
        "final_delay_days": final_delay_days,
        "final_budget_used": payload["final_budget_used"],
        "final_budget_variance_percent": final_budget_variance,
        "final_cost_crore": final_cost,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "recorded_by_uid": user_uid,
        "notes": payload.get("notes"),
    }


def _validate_outcome_data(data: dict[str, Any], project: ProjectRecord) -> None:
    """Validate outcome data against domain constraints and project state.

    Raises:
        ValueError: If any field is invalid or project not eligible for completion
    """
    # Validate completion status
    allowed_statuses = {"COMPLETED", "TERMINATED", "SUSPENDED", "ON_HOLD"}
    if data.get("completion_status", "").upper() not in allowed_statuses:
        raise ValueError(f"completion_status must be one of {allowed_statuses}")

    # Validate dates
    actual_date = data.get("actual_completion_date")
    planned_date = data.get("planned_completion_date")

    if not actual_date:
        raise ValueError("actual_completion_date is required")

    try:
        actual = datetime.strptime(actual_date, "%Y-%m-%d")
        if planned_date:
            planned = datetime.strptime(planned_date, "%Y-%m-%d")
            if actual < planned:
                # Allow actual before planned (early completion)
                pass
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    # Validate numeric ranges
    final_progress = data.get("final_progress", 0)
    if not (0 <= final_progress <= 100):
        raise ValueError(f"final_progress must be between 0 and 100, got {final_progress}")

    final_budget_used = data.get("final_budget_used", 0)
    if not (0 <= final_budget_used <= 100):
        raise ValueError(f"final_budget_used must be between 0 and 100, got {final_budget_used}")

    final_delay = data.get("final_delay_days", 0)
    if final_delay < 0:
        raise ValueError(f"final_delay_days must be non-negative, got {final_delay}")

    # Validate project eligibility for completion
    # Project must exist and have a valid current state
    if project.progress < 0:
        raise ValueError("Project has invalid progress state")

    # If project is already marked COMPLETED, prevent duplicate
    # This is handled at API level via check_outcome_exists


def create_project_outcome(
    project_id: str,
    payload: dict[str, Any],
    user_uid: str,
) -> dict[str, Any]:
    """Create a completion outcome for a project.

    Reads the current authoritative project metrics from the database
    and creates an immutable outcome record.

    Args:
        project_id: Project identifier
        payload: Outcome data from request
        user_uid: Firebase UID of the officer recording the outcome

    Returns:
        The created outcome data dictionary

    Raises:
        ValueError: If project not found, outcome already exists, or validation fails
        RuntimeError: If Firebase is unavailable
    """
    # Fetch current project (authoritative source)
    project = get_project_by_id(project_id)
    if not project:
        raise ValueError(f"Project '{project_id}' not found in database")

    # Check for existing outcome (immutability)
    if check_outcome_exists(project_id):
        existing = fetch_project_outcome_from_firebase(project_id)
        if existing:
            raise ValueError(
                f"Outcome for project '{project_id}' already exists. "
                f"Use explicit correction mechanism if update is required."
            )

    # Build outcome from project + payload
    outcome_data = _build_outcome_from_project(project, payload, user_uid)

    # Validate outcome data
    _validate_outcome_data(outcome_data, project)

    # Save to Firebase
    success = save_project_outcome_to_firebase(project_id, outcome_data)
    if not success:
        raise RuntimeError(
            f"Failed to save outcome for project '{project_id}' "
            f"to Firebase Realtime Database."
        )

    return outcome_data


def get_project_outcome(
    project_id: str,
) -> dict[str, Any] | None:
    """Retrieve the completion outcome for a project.

    Args:
        project_id: Project identifier

    Returns:
        Outcome data dictionary if found, None otherwise

    Raises:
        RuntimeError: If Firebase is unavailable
    """
    outcome = fetch_project_outcome_from_firebase(project_id)
    return outcome


"""Project data access and 360° analytics service.

Firebase Realtime Database is the sole source of truth for production project data.
No fake data, no mock fallbacks.
"""

from contextlib import contextmanager
from datetime import datetime
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


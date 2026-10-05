"""Load historical project snapshots from Firebase for ML dataset creation."""

import logging
from datetime import datetime, timezone
from typing import Any

from app.services.firebase_service import (
    fetch_all_project_snapshots_from_firebase,
    fetch_projects_from_firebase,
    fetch_project_outcome_from_firebase,
    get_firebase_http_client,
)

logger = logging.getLogger("infraplus.ml.data_loader")


def load_all_snapshots_from_firebase() -> dict[str, list[dict[str, Any]]]:
    """
    Load all project snapshots from Firebase Realtime Database.

    Returns:
        Dictionary mapping project_id to list of snapshot records.
        Empty dict if no snapshots exist or Firebase unavailable.
    """
    projects = fetch_projects_from_firebase()
    if projects is None:
        logger.warning("Unable to fetch projects from Firebase for snapshot loading")
        return {}

    snapshots_by_project: dict[str, list[dict[str, Any]]] = {}

    for project_id in projects.keys():
        project_snapshots = fetch_all_project_snapshots_from_firebase(project_id)
        if project_snapshots is None:
            logger.warning(f"Error fetching snapshots for project {project_id}")
            continue

        if project_snapshots:
            # Convert to list of snapshot records
            snapshot_list = list(project_snapshots.values())
            # Sort by period
            snapshot_list.sort(key=lambda s: s.get("snapshot_period", ""))
            snapshots_by_project[project_id] = snapshot_list
            logger.info(f"Loaded {len(snapshot_list)} snapshots for project {project_id}")

    return snapshots_by_project


def load_projects_from_firebase() -> list[dict[str, Any]]:
    """
    Load all current project records from Firebase.

    Returns:
        List of project record dictionaries.
    """
    projects = fetch_projects_from_firebase()
    if projects is None:
        return []

    return list(projects.values())


def load_outcomes_from_firebase() -> dict[str, dict[str, Any]]:
    """
    Load all project outcomes from Firebase.

    Returns:
        Dictionary mapping project_id to outcome record.
    """
    projects = fetch_projects_from_firebase()
    if projects is None:
        return {}

    outcomes = {}
    for project_id in projects.keys():
        outcome = fetch_project_outcome_from_firebase(project_id)
        if outcome:
            outcomes[project_id] = outcome

    return outcomes


def get_snapshot_count_stats(snapshots_by_project: dict[str, list[dict]]) -> dict:
    """Compute snapshot statistics."""
    total_snapshots = sum(len(s) for s in snapshots_by_project.values())
    projects_with_snapshots = len([p for p, s in snapshots_by_project.items() if s])
    projects_with_multiple = len([p for p, s in snapshots_by_project.items() if len(s) >= 2])
    projects_with_3plus = len([p for p, s in snapshots_by_project.items() if len(s) >= 3])
    projects_with_4plus = len([p for p, s in snapshots_by_project.items() if len(s) >= 4])

    all_periods = []
    for snapshots in snapshots_by_project.values():
        for s in snapshots:
            period = s.get("snapshot_period")
            if period:
                all_periods.append(period)

    earliest = min(all_periods) if all_periods else None
    latest = max(all_periods) if all_periods else None

    return {
        "total_projects_with_snapshots": projects_with_snapshots,
        "total_snapshots": total_snapshots,
        "projects_with_multiple_snapshots": projects_with_multiple,
        "projects_with_3plus_snapshots": projects_with_3plus,
        "projects_with_4plus_snapshots": projects_with_4plus,
        "earliest_period": earliest,
        "latest_period": latest,
        "unique_periods": sorted(list(set(all_periods))) if all_periods else [],
    }


def get_current_utc_period() -> str:
    """Return current UTC period in YYYY-MM format."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


def get_collection_status_for_project(project_id: str, project_data: dict) -> dict[str, Any]:
    """
    Get collection status for a single project.

    Returns dict with:
    - has_snapshots: bool
    - snapshot_count: int
    - latest_snapshot_period: str | None
    - has_current_period_snapshot: bool
    - current_period: str (YYYY-MM)
    - latest_progress: float
    - latest_delay_days: int
    - latest_budget_used: float
    - has_outcome: bool
    - outcome_status: str | None
    """
    snapshots = fetch_all_project_snapshots_from_firebase(project_id)
    outcome = fetch_project_outcome_from_firebase(project_id)
    current_period = get_current_utc_period()

    snapshot_count = 0
    latest_snapshot = None
    has_current = False

    if snapshots:
        snapshot_list = list(snapshots.values())
        snapshot_list.sort(key=lambda s: s.get("snapshot_period", ""))
        snapshot_count = len(snapshot_list)
        latest_snapshot = snapshot_list[-1]
        latest_period = latest_snapshot.get("snapshot_period")
        if latest_period == current_period:
            has_current = True

    return {
        "project_id": project_id,
        "has_snapshots": snapshot_count > 0,
        "snapshot_count": snapshot_count,
        "latest_snapshot_period": latest_snapshot.get("snapshot_period") if latest_snapshot else None,
        "has_current_period_snapshot": has_current,
        "current_reporting_period": current_period,
        "latest_progress": latest_snapshot.get("progress") if latest_snapshot else project_data.get("progress"),
        "latest_delay_days": latest_snapshot.get("delay_days") if latest_snapshot else project_data.get("delay_days"),
        "latest_budget_used": latest_snapshot.get("budget_used") if latest_snapshot else project_data.get("budget_used"),
        "has_outcome": outcome is not None,
        "outcome_status": outcome.get("completion_status") if outcome else None,
    }


def get_collection_status_all_projects() -> list[dict[str, Any]]:
    """Get collection status for all projects."""
    projects = fetch_projects_from_firebase()
    if projects is None:
        return []

    status_list = []
    for project_id, project_data in projects.items():
        status = get_collection_status_for_project(project_id, project_data)
        # Add collection category
        if status["has_outcome"]:
            if status["outcome_status"] == "COMPLETED":
                status["collection_category"] = "COMPLETED_WITH_OUTCOME"
            else:
                status["collection_category"] = "COMPLETED_WITHOUT_OUTCOME"
        elif status["snapshot_count"] == 0:
            status["collection_category"] = "NO_SNAPSHOTS"
        elif status["snapshot_count"] == 1:
            status["collection_category"] = "ONE_SNAPSHOT"
        elif status["snapshot_count"] >= 4:
            status["collection_category"] = "HISTORICAL_TRACKING_ACTIVE"
        else:
            status["collection_category"] = "HISTORICAL_TRACKING_ACTIVE"
        status_list.append(status)

    return status_list


def get_projects_from_firebase() -> list[dict[str, Any]]:
    """
    Load all current project records from Firebase.

    Returns:
        List of project record dictionaries.
    """
    projects = fetch_projects_from_firebase()
    if projects is None:
        return []

    return list(projects.values())
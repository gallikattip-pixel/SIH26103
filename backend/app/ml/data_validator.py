"""Validate historical project snapshots for ML dataset quality."""

import logging
import re
from datetime import datetime
from typing import Any

from app.models.project import ProjectRecord

logger = logging.getLogger("infraplus.ml.data_validator")


class SnapshotValidationError(Exception):
    """Raised when a snapshot fails validation."""
    pass


def validate_snapshot_period(period: str) -> bool:
    """Validate YYYY-MM format."""
    if not period or not isinstance(period, str):
        return False
    if not re.match(r"^\d{4}-\d{2}$", period):
        return False
    try:
        year, month = map(int, period.split("-"))
        return 2000 <= year <= 2100 and 1 <= month <= 12
    except ValueError:
        return False


def validate_recorded_at(recorded_at: str) -> bool:
    """Validate ISO format timestamp."""
    if not recorded_at or not isinstance(recorded_at, str):
        return False
    try:
        datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_numeric_range(value: Any, field_name: str, min_val: float, max_val: float) -> bool:
    """Validate numeric field within range."""
    if value is None:
        return False
    try:
        num = float(value)
        return min_val <= num <= max_val
    except (ValueError, TypeError):
        return False


def validate_snapshot(snapshot: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a single snapshot record.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    required_fields = [
        "project_id", "snapshot_period", "recorded_at",
        "progress", "planned_progress", "delay_days",
        "budget_used", "budget_total_crore",
        "contractor", "sector", "location"
    ]

    for field in required_fields:
        if field not in snapshot or snapshot[field] is None:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate period format
    if not validate_snapshot_period(snapshot["snapshot_period"]):
        errors.append(f"Invalid snapshot_period format: {snapshot['snapshot_period']}")

    # Validate recorded_at
    if not validate_recorded_at(snapshot["recorded_at"]):
        errors.append(f"Invalid recorded_at format: {snapshot['recorded_at']}")

    # Validate numeric ranges
    if not validate_numeric_range(snapshot["progress"], "progress", 0, 100):
        errors.append(f"Progress out of range [0,100]: {snapshot['progress']}")

    if not validate_numeric_range(snapshot["planned_progress"], "planned_progress", 0, 100):
        errors.append(f"Planned progress out of range [0,100]: {snapshot['planned_progress']}")

    if not validate_numeric_range(snapshot["delay_days"], "delay_days", 0, 10000):
        errors.append(f"Delay days out of range [0,10000]: {snapshot['delay_days']}")

    if not validate_numeric_range(snapshot["budget_used"], "budget_used", 0, 100):
        errors.append(f"Budget used out of range [0,100]: {snapshot['budget_used']}")

    if not validate_numeric_range(snapshot["budget_total_crore"], "budget_total_crore", 0, 100000):
        errors.append(f"Budget total out of range: {snapshot['budget_total_crore']}")

    # Validate categorical fields are non-empty strings
    for cat_field in ["project_id", "contractor", "sector", "location"]:
        val = snapshot.get(cat_field)
        if not val or not isinstance(val, str) or not val.strip():
            errors.append(f"Invalid {cat_field}: {val}")

    # Validate risk_snapshot if present (for auditing only, not ML features)
    risk_snap = snapshot.get("risk_snapshot")
    if risk_snap and isinstance(risk_snap, dict):
        risk_fields = ["overall_score", "overall_level", "progress_risk", "delay_risk", "budget_risk"]
        for rf in risk_fields:
            if rf not in risk_snap:
                errors.append(f"Incomplete risk_snapshot missing {rf}")

    return len(errors) == 0, errors


def validate_snapshot_collection(snapshots: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    """
    Validate a collection of snapshots.

    Returns:
        (valid_snapshots, invalid_snapshots_with_errors)
    """
    valid = []
    invalid = []

    for snap in snapshots:
        is_valid, errors = validate_snapshot(snap)
        if is_valid:
            valid.append(snap)
        else:
            invalid.append({"snapshot": snap, "errors": errors})

    logger.info(f"Validated {len(valid)} snapshots, {len(invalid)} invalid")
    return valid, invalid


def detect_duplicate_snapshots(snapshots: list[dict[str, Any]]) -> list[dict]:
    """
    Detect duplicate snapshots (same project_id + snapshot_period).

    Returns:
        List of duplicate snapshot groups.
    """
    seen = {}
    duplicates = []

    for snap in snapshots:
        key = (snap.get("project_id"), snap.get("snapshot_period"))
        if key in seen:
            if key not in duplicates:
                duplicates.append(key)
        else:
            seen[key] = snap

    return duplicates


def check_temporal_consistency(snapshots: list[dict[str, Any]]) -> list[str]:
    """
    Check for temporal inconsistencies in snapshots for the same project.

    Returns:
        List of warnings.
    """
    warnings = []

    # Group by project
    by_project = {}
    for snap in snapshots:
        pid = snap.get("project_id")
        if pid not in by_project:
            by_project[pid] = []
        by_project[pid].append(snap)

    for pid, proj_snaps in by_project.items():
        if len(proj_snaps) < 2:
            continue

        # Sort by period
        proj_snaps.sort(key=lambda s: s.get("snapshot_period", ""))

        for i in range(1, len(proj_snaps)):
            prev = proj_snaps[i-1]
            curr = proj_snaps[i]

            # Check recorded_at is monotonic
            try:
                prev_time = datetime.fromisoformat(prev["recorded_at"].replace("Z", "+00:00"))
                curr_time = datetime.fromisoformat(curr["recorded_at"].replace("Z", "+00:00"))
                if curr_time < prev_time:
                    warnings.append(
                        f"Project {pid}: recorded_at goes backwards from "
                        f"{prev['snapshot_period']} to {curr['snapshot_period']}"
                    )
            except (ValueError, KeyError):
                pass

            # Check for large jumps that might indicate missing data
            # (This is informational, not an error)
            pass

    return warnings
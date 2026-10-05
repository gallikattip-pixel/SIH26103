"""Feature engineering for ML dataset from historical project snapshots."""

import logging
from typing import Any

import numpy as np

from app.ml.data_validator import validate_snapshot

logger = logging.getLogger("infraplus.ml.feature_engineering")


# Fields that are SAFE for ML features (raw observations)
SAFE_FEATURE_FIELDS = [
    "project_id",
    "snapshot_period",
    "progress",
    "planned_progress",
    "delay_days",
    "budget_used",
    "budget_total_crore",
    "contractor",
    "sector",
    "location",
]

# Fields that are DERIVED/LEAKAGE-PRONE - EXCLUDE from ML features
LEAKAGE_FEATURE_FIELDS = [
    "risk_snapshot",           # Contains risk_score, risk_level, progress_risk, etc.
    "overall_score",           # Deterministic risk output
    "overall_level",           # Deterministic risk output
    "progress_risk",           # Deterministic risk component
    "delay_risk",              # Deterministic risk component
    "budget_risk",             # Deterministic risk component
    "progress_gap",            # Derived from progress/planned
    "spend_ahead_of_work",     # Derived from budget_used - progress
    "financial_health",        # Derived from budget risk
    "schedule_status",         # Derived from delay
    "recovery_urgency",        # Derived from delay
]


def extract_safe_features(snapshot: dict[str, Any]) -> dict[str, Any]:
    """
    Extract only leakage-safe features from a snapshot.

    Returns dict with only raw observable metrics.
    """
    features = {}

    for field in SAFE_FEATURE_FIELDS:
        if field in snapshot:
            features[field] = snapshot[field]

    # Compute safe derived features (these don't leak future outcomes)
    # progress_gap is computable from current observations
    if "progress" in features and "planned_progress" in features:
        features["progress_gap"] = features["planned_progress"] - features["progress"]

    # spend_ahead_of_work is computable from current observations
    if "budget_used" in features and "progress" in features:
        features["spend_ahead_of_work"] = max(0, features["budget_used"] - features["progress"])

    return features


def extract_temporal_features(
    snapshots: list[dict[str, Any]],
    min_periods: int = 2
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract temporal features from sequential snapshots.

    Only computes features from REAL consecutive observations.
    Does NOT interpolate or fabricate missing periods.

    Args:
        snapshots: List of validated snapshots, sorted by snapshot_period
        min_periods: Minimum snapshots required to compute temporal features

    Returns:
        Dictionary mapping project_id to list of snapshots with temporal features added
    """
    if len(snapshots) < min_periods:
        return {}

    # First, extract safe features (including derived features like progress_gap)
    safe_snapshots = [extract_safe_features(s) for s in snapshots]

    # Group by project
    by_project = {}
    for snap in safe_snapshots:
        pid = snap.get("project_id")
        if pid not in by_project:
            by_project[pid] = []
        by_project[pid].append(snap)

    temporal_by_project = {}

    for pid, proj_snaps in by_project.items():
        if len(proj_snaps) < min_periods:
            continue

        # Sort by period
        proj_snaps.sort(key=lambda s: s.get("snapshot_period", ""))

        # Add temporal features to each snapshot (except first)
        enhanced = []
        for i in range(len(proj_snaps)):
            base = proj_snaps[i].copy()

            if i > 0:
                prev = proj_snaps[i-1]

                # Progress change
                if "progress" in base and "progress" in prev:
                    base["progress_change"] = base["progress"] - prev["progress"]

                # Planned progress change
                if "planned_progress" in base and "planned_progress" in prev:
                    base["planned_progress_change"] = base["planned_progress"] - prev["planned_progress"]

                # Delay change
                if "delay_days" in base and "delay_days" in prev:
                    base["delay_change"] = base["delay_days"] - prev["delay_days"]

                # Budget used change
                if "budget_used" in base and "budget_used" in prev:
                    base["budget_used_change"] = base["budget_used"] - prev["budget_used"]

                # Progress gap change
                if "progress_gap" in base and "progress_gap" in prev:
                    base["progress_gap_change"] = base["progress_gap"] - prev["progress_gap"]

                # Budget consumption rate (budget used / progress)
                if base.get("progress", 0) > 0:
                    base["budget_per_progress"] = base["budget_used"] / base["progress"]
                if prev.get("progress", 0) > 0:
                    base["budget_per_progress_change"] = (
                        base.get("budget_per_progress", 0) - prev.get("budget_per_progress", 0)
                    )

            enhanced.append(base)

        temporal_by_project[pid] = enhanced

    return temporal_by_project


def encode_categorical_feature(values: list[str], max_categories: int = 50) -> dict[str, int]:
    """
    Create label encoding for categorical feature.

    Rare categories (below threshold) are grouped as 'OTHER'.
    """
    from collections import Counter

    counts = Counter(values)
    # Keep top categories, group rest as OTHER
    top_categories = [cat for cat, _ in counts.most_common(max_categories - 1)]

    encoding = {cat: i for i, cat in enumerate(top_categories)}
    encoding["OTHER"] = len(top_categories)
    encoding["UNKNOWN"] = len(top_categories) + 1

    return encoding


def prepare_categorical_encodings(snapshots: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """
    Prepare categorical encodings from snapshot data.

    Returns dict of field_name -> {category: encoded_value}
    """
    categorical_fields = ["sector", "location", "contractor"]
    encodings = {}

    for field in categorical_fields:
        values = [s.get(field, "UNKNOWN") for s in snapshots if s.get(field)]
        if values:
            encodings[field] = encode_categorical_feature(values)

    return encodings


def apply_categorical_encoding(
    snapshots: list[dict[str, Any]],
    encodings: dict[str, dict[str, int]]
) -> list[dict[str, Any]]:
    """Apply categorical encodings to snapshots."""
    encoded = []

    for snap in snapshots:
        new_snap = snap.copy()
        for field, encoding in encodings.items():
            raw_val = snap.get(field, "UNKNOWN")
            encoded_val = encoding.get(raw_val, encoding.get("OTHER", encoding.get("UNKNOWN", 0)))
            new_snap[f"{field}_encoded"] = encoded_val
        encoded.append(new_snap)

    return encoded


def build_feature_matrix(
    snapshots: list[dict[str, Any]],
    target_field: str | None = None
) -> tuple[list[dict], list[float] | None, list[str]]:
    """
    Build ML feature matrix from validated snapshots.

    Args:
        snapshots: List of validated snapshots
        target_field: Optional target field name for supervised learning

    Returns:
        (feature_list, target_list or None, feature_names)
    """
    # Extract safe features
    feature_snapshots = [extract_safe_features(s) for s in snapshots]

    # Prepare categorical encodings
    encodings = prepare_categorical_encodings(feature_snapshots)

    # Apply encodings
    feature_snapshots = apply_categorical_encoding(feature_snapshots, encodings)

    # Add temporal features if available
    temporal = extract_temporal_features(feature_snapshots)
    if temporal:
        # Merge temporal features back
        temporal_lookup = {}
        for pid, proj_snaps in temporal.items():
            for snap in proj_snaps:
                key = (pid, snap.get("snapshot_period"))
                temporal_lookup[key] = snap

        merged = []
        for snap in feature_snapshots:
            key = (snap.get("project_id"), snap.get("snapshot_period"))
            if key in temporal_lookup:
                # Merge temporal features
                temp_snap = temporal_lookup[key]
                for k, v in temp_snap.items():
                    if k not in snap:
                        snap[k] = v
            merged.append(snap)
        feature_snapshots = merged

    # Define feature columns (exclude identifiers and target)
    exclude_fields = {"project_id", "snapshot_period", "recorded_at"}
    if target_field:
        exclude_fields.add(target_field)

    # Get all feature names from first snapshot
    if feature_snapshots:
        feature_names = [k for k in feature_snapshots[0].keys() if k not in exclude_fields]
        feature_names.sort()  # Consistent ordering
    else:
        feature_names = []

    # Extract target if specified
    targets = None
    if target_field:
        targets = []
        for snap in snapshots:
            val = snap.get(target_field)
            if val is not None:
                try:
                    targets.append(float(val))
                except (ValueError, TypeError):
                    targets.append(None)
            else:
                targets.append(None)

    return feature_snapshots, targets, feature_names


def get_feature_schema() -> dict:
    """
    Return the feature schema for documentation.

    Describes each feature, its type, and whether it's safe for ML.
    """
    return {
        "safe_raw_features": {
            "progress": "float, 0-100, current physical progress",
            "planned_progress": "float, 0-100, current planned progress",
            "delay_days": "int, >=0, current schedule delay",
            "budget_used": "float, 0-100, current budget utilization",
            "budget_total_crore": "float, >=0, total sanctioned budget",
            "sector": "categorical, infrastructure sector",
            "location": "categorical, state/location",
            "contractor": "categorical, contractor name",
        },
        "safe_derived_features": {
            "progress_gap": "float, planned_progress - progress",
            "spend_ahead_of_work": "float, max(0, budget_used - progress)",
            "budget_per_progress": "float, budget_used / progress (when progress > 0)",
        },
        "temporal_features": {
            "progress_change": "float, progress - previous_progress",
            "planned_progress_change": "float, planned_progress - previous_planned",
            "delay_change": "int, delay_days - previous_delay",
            "budget_used_change": "float, budget_used - previous_budget_used",
            "progress_gap_change": "float, progress_gap - previous_gap",
            "budget_per_progress_change": "float, budget_per_progress - previous",
        },
        "excluded_leakage_features": [
            "risk_score / overall_score",
            "risk_level / overall_level",
            "progress_risk",
            "delay_risk",
            "budget_risk",
            "final_delay_days (outcome)",
            "final_budget_variance (outcome)",
            "project_outcome_label (outcome)",
        ],
        "categorical_encodings": {
            "sector_encoded": "label encoding of sector",
            "location_encoded": "label encoding of location",
            "contractor_encoded": "label encoding of contractor (high cardinality)",
        },
    }
"""Generate ML dataset audit report from historical snapshots."""

import json
import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from app.ml.data_loader import (
    load_all_snapshots_from_firebase,
    get_snapshot_count_stats,
    load_outcomes_from_firebase,
    load_projects_from_firebase,
    get_collection_status_all_projects,
    get_current_utc_period,
)
from app.ml.data_validator import (
    validate_snapshot_collection,
    detect_duplicate_snapshots,
    check_temporal_consistency,
)
from app.ml.feature_engineering import get_feature_schema

logger = logging.getLogger("infraplus.ml.dataset_report")


def generate_dataset_audit() -> dict[str, Any]:
    """
    Generate comprehensive dataset audit report.

    Returns:
        Dictionary with all audit metrics and findings.
    """
    logger.info("Generating ML dataset audit report...")

    # Load raw snapshots
    snapshots_by_project = load_all_snapshots_from_firebase()

    # Load outcomes
    outcomes_by_project = load_outcomes_from_firebase()

    # Load current projects
    projects = load_projects_from_firebase()

    # Flatten all snapshots
    all_snapshots = []
    for pid, snaps in snapshots_by_project.items():
        for snap in snaps:
            snap["project_id"] = pid
            all_snapshots.append(snap)

    # Validate all snapshots
    valid_snapshots, invalid_snapshots = validate_snapshot_collection(all_snapshots)

    # Check for duplicates
    duplicates = detect_duplicate_snapshots(valid_snapshots)

    # Check temporal consistency
    temporal_warnings = check_temporal_consistency(valid_snapshots)

    # Get snapshot statistics
    stats = get_snapshot_count_stats(snapshots_by_project)

    # Analyze field completeness
    field_completeness = analyze_field_completeness(valid_snapshots)

    # Analyze categorical distributions
    categorical_distributions = analyze_categorical_distributions(valid_snapshots)

    # Analyze numeric distributions
    numeric_distributions = analyze_numeric_distributions(valid_snapshots)

    # Check target feasibility
    target_feasibility = analyze_target_feasibility(valid_snapshots)

    # Get collection status for all projects
    collection_status = get_collection_status_all_projects()

    # Load all projects
    projects = load_projects_from_firebase()

    # Get outcomes
    outcomes = load_outcomes_from_firebase()

    # Build report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "Firebase Realtime Database / project_snapshots & project_outcomes",
        "summary": {
            "total_projects_in_db": len(load_projects_from_firebase()),
            "total_snapshots": stats.get("total_snapshots", 0),
            "valid_snapshots": len(valid_snapshots),
            "invalid_snapshots": len(invalid_snapshots),
            "projects_with_snapshots": stats.get("total_projects_with_snapshots", 0),
            "projects_without_snapshots": len(load_projects_from_firebase()) - stats.get("total_projects_with_snapshots", 0),
            "projects_with_multiple_snapshots": stats.get("projects_with_multiple_snapshots", 0),
            "projects_with_3plus_snapshots": stats.get("projects_with_3plus_snapshots", 0),
            "projects_with_4plus_snapshots": stats.get("projects_with_4plus_snapshots", 0),
            "earliest_period": stats.get("earliest_period"),
            "latest_period": stats.get("latest_period"),
            "unique_periods": stats.get("unique_periods", []),
        },
        "collection_status": {
            "projects_with_no_snapshots": len([p for p in get_collection_status_all_projects() if p["snapshot_count"] == 0]),
            "projects_with_one_snapshot": len([p for p in get_collection_status_all_projects() if p["snapshot_count"] == 1]),
            "projects_with_2plus_snapshots": stats.get("projects_with_multiple_snapshots", 0),
            "projects_with_3plus_snapshots": stats.get("projects_with_3plus_snapshots", 0),
            "projects_with_4plus_snapshots": stats.get("projects_with_4plus_snapshots", 0),
            "projects_with_outcomes": len(load_outcomes_from_firebase()),
            "projects_with_current_period_snapshot": len([p for p in get_collection_status_all_projects() if p["has_current_period_snapshot"]]),
            "current_reporting_period": get_current_utc_period(),
        },
        "outcomes": {
            "total_outcomes": len(load_outcomes_from_firebase()),
            "completed_outcomes": len([o for o in load_outcomes_from_firebase().values() if o.get("completion_status") == "COMPLETED"]),
            "terminated_outcomes": len([o for o in load_outcomes_from_firebase().values() if o.get("completion_status") == "TERMINATED"]),
            "suspended_outcomes": len([o for o in load_outcomes_from_firebase().values() if o.get("completion_status") in ["SUSPENDED", "ON_HOLD"]]),
            "outcomes_with_complete_target_info": len([o for o in load_outcomes_from_firebase().values() if o.get("final_delay_days") is not None and o.get("final_budget_used") is not None]),
        },
        "field_completeness": analyze_field_completeness(valid_snapshots),
        "categorical_distributions": analyze_categorical_distributions(valid_snapshots),
        "numeric_distributions": analyze_numeric_distributions(valid_snapshots),
        "data_quality": {
            "duplicate_project_period_pairs": len(duplicates),
            "temporal_consistency_warnings": len(temporal_warnings),
            "invalid_records": len(invalid_snapshots),
            "invalid_record_details": invalid_snapshots[:5] if invalid_snapshots else [],
        },
        "target_feasibility": analyze_target_feasibility(valid_snapshots),
        "feature_schema": get_feature_schema(),
        "ml_readiness": assess_ml_readiness(stats, valid_snapshots, target_feasibility),
    }

    return report


def analyze_field_completeness(snapshots: list[dict[str, Any]]) -> dict[str, dict]:
    """Analyze completeness of each field across snapshots."""
    if not snapshots:
        return {}

    fields = [
        "project_id", "snapshot_period", "recorded_at",
        "progress", "planned_progress", "delay_days",
        "budget_used", "budget_total_crore",
        "contractor", "sector", "location",
        "risk_snapshot"
    ]

    total = len(snapshots)
    completeness = {}

    for field in fields:
        present = sum(1 for s in snapshots if field in s and s[field] is not None)
        completeness[field] = {
            "present": present,
            "missing": total - present,
            "completeness_pct": round(present / total * 100, 1) if total > 0 else 0
        }

    return completeness


def analyze_categorical_distributions(snapshots: list[dict[str, Any]]) -> dict[str, dict]:
    """Analyze distribution of categorical fields."""
    categorical_fields = ["sector", "location", "contractor"]
    distributions = {}

    for field in categorical_fields:
        values = [s.get(field) for s in snapshots if s.get(field)]
        if values:
            counts = Counter(values)
            distributions[field] = {
                "unique_count": len(counts),
                "top_categories": dict(counts.most_common(10)),
                "total": len(values),
            }

    return distributions


def analyze_numeric_distributions(snapshots: list[dict[str, Any]]) -> dict[str, dict]:
    """Analyze distribution of numeric fields."""
    numeric_fields = ["progress", "planned_progress", "delay_days", "budget_used", "budget_total_crore"]
    distributions = {}

    for field in numeric_fields:
        values = [s.get(field) for s in snapshots if s.get(field) is not None]
        if values:
            try:
                num_values = [float(v) for v in values]
                distributions[field] = {
                    "count": len(num_values),
                    "min": min(num_values),
                    "max": max(num_values),
                    "mean": round(sum(num_values) / len(num_values), 2),
                    "median": sorted(num_values)[len(num_values) // 2],
                }
            except (ValueError, TypeError):
                distributions[field] = {"error": "Non-numeric values found"}

    return distributions


def analyze_target_feasibility(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyze whether supervised ML targets can be derived from current data.

    Returns feasibility assessment for each potential target.
    """
    # Group by project
    by_project = {}
    for snap in snapshots:
        pid = snap.get("project_id")
        if pid not in by_project:
            by_project[pid] = []
        by_project[pid].append(snap)

    # Count projects with multiple snapshots (for temporal features)
    projects_with_temporal = sum(1 for snaps in by_project.values() if len(snaps) >= 2)
    projects_with_3plus = sum(1 for snaps in by_project.values() if len(snaps) >= 3)

    # Check for project completion outcomes
    # We need: projects that have reached completion (progress=100%)
    completed_projects = []
    for pid, snaps in by_project.items():
        for snap in snaps:
            if snap.get("progress", 0) >= 100:
                completed_projects.append(pid)
                break

    # Current data feasibility
    feasibility = {
        "delay_prediction": {
            "feasible": False,
            "reason": "No project completion outcomes observed. Need projects with final delay at completion.",
            "required_data": "Completed projects with final delay_days at progress=100%",
            "current_observations": 0,
        },
        "cost_overrun_prediction": {
            "feasible": False,
            "reason": "No project completion outcomes observed. Need projects with final budget variance at completion.",
            "required_data": "Completed projects with final budget_used at progress=100%",
            "current_observations": 0,
        },
        "risk_classification": {
            "feasible": False,
            "reason": "Deterministic risk_level is derived from current metrics, not an outcome. Using it as target would cause leakage.",
            "required_data": "Actual project outcomes (delay, cost overrun, completion status) not derived risk metrics",
            "current_observations": 0,
        },
        "implementation_risk": {
            "feasible": False,
            "reason": "No binary outcome labels (success/failure, on_time/late) available.",
            "required_data": "Projects with known final implementation status",
            "current_observations": 0,
        },
        "temporal_features": {
            "feasible": projects_with_temporal > 0,
            "projects_with_2plus_snapshots": projects_with_temporal,
            "projects_with_3plus_snapshots": projects_with_3plus,
            "note": "Temporal features can be computed for projects with multiple snapshots, but without outcomes they cannot be used for supervised learning",
        },
    }

    return feasibility


def assess_ml_readiness(stats: dict, valid_snapshots: list, target_feasibility: dict) -> dict:
    """Assess overall ML readiness of the dataset."""
    total_snapshots = stats.get("total_snapshots", 0)
    projects_multi = stats.get("projects_with_multiple_snapshots", 0)

    # Check if any target is feasible
    any_feasible = any(t.get("feasible", False) for t in target_feasibility.values())

    if total_snapshots == 0:
        status = "NO_DATA"
        message = "No historical snapshots exist in the database."
    elif not any_feasible and total_snapshots < 50:
        status = "INSUFFICIENT_DATA"
        message = f"Only {total_snapshots} snapshots across {projects_multi} projects with temporal data. No supervised targets available."
    elif not any_feasible:
        status = "UNLABELED_DATA"
        message = f"{total_snapshots} snapshots available but no labeled outcomes for supervised ML. Can only do unsupervised/temporal analysis."
    else:
        status = "READY"
        message = "Sufficient labeled data exists for model development."

    return {
        "status": status,
        "message": message,
        "total_snapshots": total_snapshots,
        "projects_with_temporal_data": projects_multi,
        "any_supervised_target_feasible": any_feasible,
        "recommended_next_step": get_recommended_next_step(status, total_snapshots, projects_multi),
    }


def get_recommended_next_step(status: str, total_snapshots: int, projects_multi: int) -> str:
    """Get recommended next step based on ML readiness."""
    if status == "NO_DATA":
        return "Implement monthly snapshot collection workflow (Step 3). Allow authorized officers to record real project observations over time."
    elif status == "INSUFFICIENT_DATA":
        return f"Continue collecting real monthly snapshots. Need at least 50+ completed projects with temporal history for supervised ML."
    elif status == "UNLABELED_DATA":
        return "Wait for projects to reach completion (progress=100%) to generate outcome labels. Then supervised targets become feasible."
    elif status == "READY":
        return "Proceed to Step 5: Model training and evaluation with temporal cross-validation."
    else:
        return "Assess data quality and collection process."


def export_audit_report(report: dict[str, Any], output_path: str | None = None) -> str:
    """Export audit report as JSON string or to file."""
    json_str = json.dumps(report, indent=2, default=str)

    if output_path:
        with open(output_path, "w") as f:
            f.write(json_str)
        logger.info(f"Audit report saved to {output_path}")

    return json_str


def print_audit_summary(report: dict[str, Any]) -> None:
    """Print human-readable audit summary."""
    summary = report["summary"]
    ml_ready = report["ml_readiness"]

    print("=" * 60)
    print("INFRAPLUS ML DATASET AUDIT REPORT")
    print("=" * 60)
    print(f"Generated: {report['generated_at']}")
    print(f"Data Source: {report['data_source']}")
    print()
    print("SNAPSHOT SUMMARY")
    print("-" * 40)
    print(f"  Total snapshots: {summary['total_snapshots']}")
    print(f"  Valid snapshots: {summary['valid_snapshots']}")
    print(f"  Projects with snapshots: {summary['total_projects_in_db']}")
    print(f"  Projects with ≥2 snapshots: {summary['projects_with_multiple_snapshots']}")
    print(f"  Projects with ≥3 snapshots: {summary['projects_with_3plus_snapshots']}")
    print(f"  Period range: {summary['earliest_period']} to {summary['latest_period']}")
    print(f"  Unique periods: {summary['unique_periods']}")
    print()
    print("DATA QUALITY")
    print("-" * 40)
    dq = report["data_quality"]
    print(f"  Duplicate project-period pairs: {dq['duplicate_project_period_pairs']}")
    print(f"  Temporal consistency warnings: {dq['temporal_consistency_warnings']}")
    print(f"  Invalid records: {dq['invalid_records']}")
    print()
    print("TARGET FEASIBILITY")
    print("-" * 40)
    for target, info in report["target_feasibility"].items():
        feasible = "✓" if info.get("feasible", False) else "✗"
        print(f"  {feasible} {target}: {info.get('reason', 'N/A')}")
    print()
    print("ML READINESS")
    print("-" * 40)
    print(f"  Status: {ml_ready['status']}")
    print(f"  Message: {ml_ready['message']}")
    print(f"  Recommended next step: {ml_ready['recommended_next_step']}")
    print("=" * 60)
"""Dashboard metrics calculation service.

All metrics are calculated dynamically from real Firebase project data and
authoritative Python Risk Engine calculations.
"""

from app.core.cache import TTLCache
from app.models.dashboard import (
    DashboardSummary,
    EarlyWarning,
    RiskDistribution,
    SectorStat,
)
from app.models.project import ProjectListItem
from app.services.project_service import get_all_projects_enriched

_dashboard_summary_cache = TTLCache[DashboardSummary](ttl_seconds=20.0)


def invalidate_dashboard_cache() -> None:
    """Invalidate the cached dashboard summary."""
    _dashboard_summary_cache.invalidate()


def _compute_dashboard_summary() -> DashboardSummary:
    """Compute executive dashboard metrics directly from real projects."""
    projects = get_all_projects_enriched()

    total = len(projects)
    if total == 0:
        return DashboardSummary(
            total_projects=0,
            high_risk_projects=0,
            medium_risk_projects=0,
            low_risk_projects=0,
            delayed_projects_count=0,
            average_progress=0.0,
            total_sanctioned_budget_crore=0.0,
            total_expended_budget_crore=0.0,
            risk_distribution=RiskDistribution(
                high_count=0,
                medium_count=0,
                low_count=0,
                total=0,
            ),
            sectors=[],
            early_warnings=[],
            highest_risk_projects=[],
        )

    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    delayed_count = 0
    total_progress = 0.0
    total_sanctioned = 0.0
    total_expended = 0.0

    sector_map: dict[str, dict] = {}
    early_warnings: list[EarlyWarning] = []

    for item in projects:
        # Risk level count
        if item.risk.overall_level == "HIGH":
            high_risk_count += 1
        elif item.risk.overall_level == "MEDIUM":
            medium_risk_count += 1
        else:
            low_risk_count += 1

        # Delay count
        if item.delay_days > 0:
            delayed_count += 1

        # Metrics sum
        total_progress += item.progress
        total_sanctioned += item.budget_total_crore
        expended = (item.budget_used / 100.0) * item.budget_total_crore
        total_expended += expended

        # Sector tracking
        sec = item.sector or "Unspecified"
        if sec not in sector_map:
            sector_map[sec] = {
                "count": 0,
                "total_progress": 0.0,
                "high_risk_count": 0,
            }
        sector_map[sec]["count"] += 1
        sector_map[sec]["total_progress"] += item.progress
        if item.risk.overall_level == "HIGH":
            sector_map[sec]["high_risk_count"] += 1

        # Early Warning evaluation based on deterministic risk metrics
        if item.delay_days >= 90:
            early_warnings.append(
                EarlyWarning(
                    project_id=item.project_id,
                    project_name=item.name,
                    warning_type="CRITICAL_DELAY",
                    severity="CRITICAL",
                    description=f"Critical schedule slippage of {item.delay_days} days exceeding 90-day threshold.",
                    metric_value=f"{item.delay_days} days delay",
                )
            )
        elif item.risk.progress_gap >= 20:
            early_warnings.append(
                EarlyWarning(
                    project_id=item.project_id,
                    project_name=item.name,
                    warning_type="PROGRESS_LAG",
                    severity="HIGH",
                    description=f"Physical progress lags {item.risk.progress_gap} points behind planned schedule.",
                    metric_value=f"{item.risk.progress_gap}% gap",
                )
            )
        elif item.budget_used >= 85 and item.progress < 60:
            early_warnings.append(
                EarlyWarning(
                    project_id=item.project_id,
                    project_name=item.name,
                    warning_type="BUDGET_OVERRUN",
                    severity="HIGH",
                    description=f"High budget utilization ({item.budget_used}%) with physical execution at only {item.progress}%.",
                    metric_value=f"{item.budget_used}% utilized",
                )
            )

    sectors: list[SectorStat] = [
        SectorStat(
            sector=s,
            count=data["count"],
            avg_progress=round(data["total_progress"] / data["count"], 1),
            high_risk_count=data["high_risk_count"],
        )
        for s, data in sorted(sector_map.items())
    ]

    # Highest risk projects sorted
    highest_risk_sorted = sorted(
        projects,
        key=lambda p: p.risk.overall_score,
        reverse=True,
    )

    return DashboardSummary(
        total_projects=total,
        high_risk_projects=high_risk_count,
        medium_risk_projects=medium_risk_count,
        low_risk_projects=low_risk_count,
        delayed_projects_count=delayed_count,
        average_progress=round(total_progress / total, 1),
        total_sanctioned_budget_crore=round(total_sanctioned, 2),
        total_expended_budget_crore=round(total_expended, 2),
        risk_distribution=RiskDistribution(
            high_count=high_risk_count,
            medium_count=medium_risk_count,
            low_count=low_risk_count,
            total=total,
        ),
        sectors=sectors,
        early_warnings=early_warnings,
        highest_risk_projects=highest_risk_sorted[:5],
    )


def get_dashboard_summary() -> DashboardSummary:
    """Calculate executive dashboard metrics from real projects (cached 20s with stampede protection)."""
    return _dashboard_summary_cache.get_or_compute(_compute_dashboard_summary)

"""Dashboard models for INFRAPLUS executive command center."""

from pydantic import BaseModel
from app.models.project import ProjectListItem


class RiskDistribution(BaseModel):
    high_count: int
    medium_count: int
    low_count: int
    total: int


class SectorStat(BaseModel):
    sector: str
    count: int
    avg_progress: float
    high_risk_count: int


class EarlyWarning(BaseModel):
    project_id: str
    project_name: str
    warning_type: str  # "CRITICAL_DELAY", "PROGRESS_LAG", "BUDGET_OVERRUN", "COMBINED_RISK"
    severity: str      # "CRITICAL", "HIGH", "WARNING"
    description: str
    metric_value: str


class DashboardSummary(BaseModel):
    total_projects: int
    high_risk_projects: int
    medium_risk_projects: int
    low_risk_projects: int
    delayed_projects_count: int
    average_progress: float
    total_sanctioned_budget_crore: float
    total_expended_budget_crore: float
    risk_distribution: RiskDistribution
    sectors: list[SectorStat]
    early_warnings: list[EarlyWarning]
    highest_risk_projects: list[ProjectListItem]

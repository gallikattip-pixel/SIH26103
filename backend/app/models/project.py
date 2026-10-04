"""Project and Risk models for INFRAPLUS."""

from typing import Any
from pydantic import BaseModel, Field


class ProjectRecord(BaseModel):
    """Base project record from database or JSON."""

    project_id: str
    name: str
    location: str
    sector: str
    progress: float
    planned_progress: float
    delay_days: int
    budget_used: float
    budget_total_crore: float
    contractor: str

    # Extra fields allowed for extensions
    model_config = {
        "extra": "allow"
    }


class RiskBreakdown(BaseModel):
    """Deterministic risk calculated by Python Risk Engine."""

    progress_gap: float
    progress_risk: int
    delay_risk: int
    budget_risk: int
    overall_score: int
    overall_level: str
    major_factors: list[str]
    metrics: dict[str, Any]


class ProjectListItem(BaseModel):
    """Project record enriched with computed risk metrics for listings."""

    project_id: str
    name: str
    location: str
    sector: str
    progress: float
    planned_progress: float
    delay_days: int
    budget_used: float
    budget_total_crore: float
    contractor: str
    risk: RiskBreakdown


class FinancialMetrics(BaseModel):
    """Financial breakdown for Project 360°."""

    project_id: str
    budget_total_crore: float
    budget_used_percent: float
    budget_expended_crore: float
    budget_remaining_crore: float
    spend_ahead_of_work: float
    financial_health: str
    budget_risk: int


class ProgressMetrics(BaseModel):
    """Physical progress breakdown for Project 360°."""

    project_id: str
    actual_progress: float
    planned_progress: float
    progress_gap: float
    status: str
    progress_risk: int


class TimelineMetrics(BaseModel):
    """Timeline and schedule metrics for Project 360°."""

    project_id: str
    delay_days: int
    delay_risk: int
    schedule_status: str
    recovery_urgency: str
    estimated_impact: str


class MilestoneRecord(BaseModel):
    """Milestone record."""

    id: str
    title: str
    target_date: str
    status: str  # "COMPLETED", "IN_PROGRESS", "DELAYED", "PENDING"
    completion_percent: float
    critical: bool = False


class AgencyRecord(BaseModel):
    """Agency and stakeholder contacts."""

    executing_agency: str
    contractor: str
    nodal_officer: str
    supervising_consultant: str
    monitoring_division: str
    contact_email: str | None = None


class DocumentRecord(BaseModel):
    """Document metadata."""

    id: str
    project_id: str
    filename: str
    title: str
    file_type: str
    file_size_kb: float
    uploaded_at: str
    download_url: str
    uploaded_by_uid: str | None = None


class ProjectDetail360(BaseModel):
    """Complete 360° project view."""

    project: ProjectRecord
    risk: RiskBreakdown
    financial: FinancialMetrics
    progress: ProgressMetrics
    timeline: TimelineMetrics
    milestones: list[MilestoneRecord]
    agencies: AgencyRecord
    documents: list[DocumentRecord]

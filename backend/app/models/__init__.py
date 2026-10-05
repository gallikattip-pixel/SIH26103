"""Pydantic models package."""

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
from app.models.snapshot import (
    ProjectSnapshot,
    SnapshotCreateRequest,
    SnapshotListResponse,
)
from app.models.outcome import (
    ProjectOutcome,
    ProjectOutcomeCreateRequest,
    ProjectOutcomeResponse,
)
from app.models.dashboard import (
    DashboardSummary,
    EarlyWarning,
    RiskDistribution,
    SectorStat,
)
from app.models.ai import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    ProjectRiskSummary,
)

__all__ = [
    # Project models
    "AgencyRecord",
    "DocumentRecord",
    "FinancialMetrics",
    "MilestoneRecord",
    "ProgressMetrics",
    "ProjectDetail360",
    "ProjectListItem",
    "ProjectRecord",
    "RiskBreakdown",
    "TimelineMetrics",
    # Snapshot models
    "ProjectSnapshot",
    "SnapshotCreateRequest",
    "SnapshotListResponse",
    # Outcome models
    "ProjectOutcome",
    "ProjectOutcomeCreateRequest",
    "ProjectOutcomeResponse",
    # Dashboard models
    "DashboardSummary",
    "EarlyWarning",
    "RiskDistribution",
    "SectorStat",
    # AI models
    "ChatRequest",
    "ChatResponse",
    "ErrorResponse",
    "ProjectRiskSummary",
]
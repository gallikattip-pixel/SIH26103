"""Historical project snapshot models for INFRAPLUS."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Any


class ProjectSnapshot(BaseModel):
    """Historical snapshot of a project at a specific point in time.

    Snapshots are immutable historical records captured at a specific period
    (e.g., monthly). They preserve raw project metrics for future ML dataset
    creation and historical auditing.

    DO NOT use derived risk metrics (risk_score, risk_level, progress_risk, etc.)
    as ML input features — they are deterministic functions of the raw metrics
    and would cause target leakage.
    """

    project_id: str = Field(..., description="Project identifier")
    snapshot_period: str = Field(
        ..., description="Period key in YYYY-MM format (e.g., 2026-10)"
    )
    recorded_at: datetime = Field(
        ..., description="Server-side UTC timestamp when snapshot was recorded"
    )
    progress: float = Field(..., ge=0, le=100, description="Physical progress percentage")
    planned_progress: float = Field(..., ge=0, le=100, description="Planned progress percentage")
    delay_days: int = Field(..., ge=0, description="Schedule delay in days")
    budget_used: float = Field(..., ge=0, le=100, description="Budget utilization percentage")
    budget_total_crore: float = Field(..., ge=0, description="Total sanctioned budget in crores")
    contractor: str = Field(..., description="Contractor name at snapshot time")
    sector: str = Field(..., description="Project sector at snapshot time")
    location: str = Field(..., description="Project location at snapshot time")

    # Derived risk snapshot for historical auditing ONLY — NOT for ML features
    risk_snapshot: dict[str, Any] | None = Field(
        default=None,
        description="Deterministic risk breakdown at snapshot time (for auditing only)"
    )

    @field_validator("snapshot_period")
    @classmethod
    def validate_period_format(cls, v: str) -> str:
        """Validate YYYY-MM format."""
        import re
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("snapshot_period must be in YYYY-MM format")
        year, month = map(int, v.split("-"))
        if not (2000 <= year <= 2100) or not (1 <= month <= 12):
            raise ValueError("Invalid year or month in snapshot_period")
        return v

    @field_validator("recorded_at", mode="before")
    @classmethod
    def ensure_utc(cls, v: Any) -> datetime:
        """Ensure recorded_at is timezone-aware UTC."""
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=None)  # Treat naive as UTC
            return dt
        return v


class SnapshotCreateRequest(BaseModel):
    """Request model for creating a project snapshot.

    The snapshot period is optional — if not provided, the current UTC month
    (YYYY-MM) will be used. This ensures server-side control over the period.
    """

    snapshot_period: str | None = Field(
        default=None,
        description="Optional period key in YYYY-MM format. Defaults to current UTC month."
    )

    @field_validator("snapshot_period")
    @classmethod
    def validate_period_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("snapshot_period must be in YYYY-MM format")
        year, month = map(int, v.split("-"))
        if not (2000 <= year <= 2100) or not (1 <= month <= 12):
            raise ValueError("Invalid year or month in snapshot_period")
        return v


class SnapshotListResponse(BaseModel):
    """Response model for listing project snapshots."""

    project_id: str
    snapshots: list[ProjectSnapshot]
    total_count: int
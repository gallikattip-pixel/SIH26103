"""Project completion outcome models for INFRAPLUS."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional


class ProjectOutcome(BaseModel):
    """Final project outcome recorded upon completion.

    This represents the authoritative final state of a completed project.
    Only one outcome per project is allowed.
    """

    project_id: str = Field(..., description="Project identifier")
    completion_status: str = Field(
        ...,
        description="Final completion status: COMPLETED, TERMINATED, SUSPENDED, ON_HOLD"
    )
    actual_completion_date: str = Field(
        ...,
        description="Actual completion date in YYYY-MM-DD format"
    )
    planned_completion_date: Optional[str] = Field(
        default=None,
        description="Original planned completion date in YYYY-MM-DD format"
    )
    final_progress: float = Field(
        ..., ge=0, le=100, description="Final physical progress percentage"
    )
    final_delay_days: int = Field(
        ..., ge=0, description="Final schedule delay in days (derived if dates provided)"
    )
    final_budget_used: float = Field(
        ..., ge=0, le=100, description="Final budget utilization percentage"
    )
    final_budget_variance_percent: Optional[float] = Field(
        default=None,
        description="Final cost variance percentage (derived if final cost available)"
    )
    final_cost_crore: Optional[float] = Field(
        default=None,
        description="Final actual cost in crores"
    )
    recorded_at: datetime = Field(
        ...,
        description="Server-side UTC timestamp when outcome was recorded"
    )
    recorded_by_uid: str = Field(
        ...,
        description="Firebase UID of the officer who recorded the outcome"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the completion"
    )

    @field_validator("completion_status")
    @classmethod
    def validate_completion_status(cls, v: str) -> str:
        """Validate completion status is one of allowed values."""
        allowed = {"COMPLETED", "TERMINATED", "SUSPENDED", "ON_HOLD"}
        if v.upper() not in allowed:
            raise ValueError(f"completion_status must be one of {allowed}")
        return v.upper()

    @field_validator("actual_completion_date", "planned_completion_date", mode="before")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format YYYY-MM-DD."""
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        # Validate it's a real date
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date")
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


class ProjectOutcomeCreateRequest(BaseModel):
    """Request model for creating a project outcome."""

    completion_status: str = Field(
        ...,
        description="Final completion status: COMPLETED, TERMINATED, SUSPENDED, ON_HOLD"
    )
    actual_completion_date: str = Field(
        ...,
        description="Actual completion date in YYYY-MM-DD format"
    )
    planned_completion_date: Optional[str] = Field(
        default=None,
        description="Original planned completion date in YYYY-MM-DD format"
    )
    final_progress: float = Field(
        ..., ge=0, le=100, description="Final physical progress percentage"
    )
    final_budget_used: float = Field(
        ..., ge=0, le=100, description="Final budget utilization percentage"
    )
    final_budget_variance_percent: Optional[float] = Field(
        default=None,
        description="Final cost variance percentage"
    )
    final_cost_crore: Optional[float] = Field(
        default=None,
        description="Final actual cost in crores"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the completion"
    )

    @field_validator("completion_status")
    @classmethod
    def validate_completion_status(cls, v: str) -> str:
        allowed = {"COMPLETED", "TERMINATED", "SUSPENDED", "ON_HOLD"}
        if v.upper() not in allowed:
            raise ValueError(f"completion_status must be one of {allowed}")
        return v.upper()

    @field_validator("actual_completion_date", "planned_completion_date", mode="before")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date")
        return v


class ProjectOutcomeResponse(BaseModel):
    """Response model for project outcome."""

    project_id: str
    outcome: Optional[ProjectOutcome] = Field(
        default=None,
        description="Project outcome if recorded, null otherwise"
    )
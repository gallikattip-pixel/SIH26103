"""AI chat request and response models."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    project_id: str | None = Field(
        default=None,
        min_length=1,
        examples=["P42"],
    )
    question: str = Field(
        ...,
        min_length=1,
        examples=["Why is this project at high risk?"],
    )


class ProjectRiskSummary(BaseModel):
    """Risk summary for one project in a multi-project response."""

    project_id: str
    project_name: str
    risk_level: str
    risk_score: int


class ChatResponse(BaseModel):
    """Response returned by the AI assistant."""

    answer: str
    risk_level: str
    risk_score: int
    major_factors: list[str]
    recommended_actions: list[str]
    projects: list[ProjectRiskSummary] = []


class ErrorResponse(BaseModel):
    detail: str

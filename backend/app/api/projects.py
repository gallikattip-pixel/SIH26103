"""Projects API routes for listing, filtering, and Project 360° sub-views."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app.config import (
    RATE_LIMIT_PROJECT_CREATE_LIMIT,
    RATE_LIMIT_PROJECT_CREATE_WINDOW,
    RATE_LIMIT_READS_LIMIT,
    RATE_LIMIT_READS_WINDOW,
)
from app.core.rate_limiter import apply_rate_limit, resolve_client_identity
from app.core.security import UserRole, get_optional_user, require_roles
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
from app.services.project_service import (
    create_new_project,
    get_all_projects_enriched,
    get_project_360,
    get_project_agencies,
    get_project_by_id,
    get_project_documents,
    get_project_financial,
    get_project_milestones,
    get_project_progress,
    get_project_risk,
    get_project_timeline,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectListItem])
def list_projects(
    search: str | None = Query(default=None, description="Search term across name, ID, contractor, location"),
    sector: str | None = Query(default=None, description="Filter by infrastructure sector"),
    risk_level: str | None = Query(default=None, description="Filter by risk level (HIGH, MEDIUM, LOW)"),
    delayed_only: bool = Query(default=False, description="Filter only projects with schedule delay"),
    sort_by: str = Query(default="risk_score", description="Sort field: risk_score, delay, progress_gap, budget, name"),
    order: str = Query(default="desc", description="Sort order: asc, desc"),
) -> list[ProjectListItem]:
    """
    List all infrastructure projects from Firebase Realtime Database.
    Includes real-time deterministic risk assessment and filtering.
    """
    try:
        items = get_all_projects_enriched()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    # Filtering
    if search:
        q = search.lower().strip()
        items = [
            p for p in items
            if q in p.project_id.lower()
            or q in p.name.lower()
            or q in p.location.lower()
            or q in p.contractor.lower()
        ]

    if sector and sector.lower() != "all":
        items = [p for p in items if p.sector.lower() == sector.lower()]

    if risk_level and risk_level.lower() != "all":
        items = [p for p in items if p.risk.overall_level.upper() == risk_level.upper()]

    if delayed_only:
        items = [p for p in items if p.delay_days > 0]

    # Sorting
    reverse = order.lower() == "desc"
    if sort_by == "risk_score":
        items.sort(key=lambda p: p.risk.overall_score, reverse=reverse)
    elif sort_by == "delay":
        items.sort(key=lambda p: p.delay_days, reverse=reverse)
    elif sort_by == "progress_gap":
        items.sort(key=lambda p: p.risk.progress_gap, reverse=reverse)
    elif sort_by == "budget":
        items.sort(key=lambda p: p.budget_total_crore, reverse=reverse)
    elif sort_by == "name":
        items.sort(key=lambda p: p.name.lower(), reverse=reverse)

    return items


@router.post("", response_model=ProjectListItem, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectRecord,
    request: Request,
    response: Response,
    current_user: dict[str, Any] = Depends(require_roles([UserRole.ADMIN, UserRole.OFFICER])),
) -> ProjectListItem:
    """
    Create and register a new infrastructure project directly in Firebase Realtime Database.
    Calculates deterministic risk scores immediately.
    Requires ADMIN or OFFICER role (401 unauthenticated, 403 viewer).
    Rate-limited by user identity (10 creations / hour).
    """
    uploader_uid = current_user.get("uid")
    if uploader_uid:
        apply_rate_limit(
            request=request,
            response=response,
            scope="project_create",
            identity=f"user:{uploader_uid}",
            limit=RATE_LIMIT_PROJECT_CREATE_LIMIT,
            window_seconds=RATE_LIMIT_PROJECT_CREATE_WINDOW,
        )
    try:
        return create_new_project(project)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )


@router.get("/{project_id}", response_model=ProjectDetail360)
def get_project_detail(project_id: str) -> ProjectDetail360:
    """Return complete Project 360° overview including all dimensions."""
    try:
        detail = get_project_360(project_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' was not found in the database.",
        )
    return detail


@router.get("/{project_id}/financial", response_model=FinancialMetrics)
def get_financial(project_id: str) -> FinancialMetrics:
    """Return financial breakdown for project."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_project_financial(project)


@router.get("/{project_id}/progress", response_model=ProgressMetrics)
def get_progress(project_id: str) -> ProgressMetrics:
    """Return physical progress and planned variance metrics."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_project_progress(project)


@router.get("/{project_id}/timeline", response_model=TimelineMetrics)
def get_timeline(project_id: str) -> TimelineMetrics:
    """Return schedule and delay risk metrics."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_project_timeline(project)


@router.get("/{project_id}/milestones", response_model=list[MilestoneRecord])
def get_milestones(project_id: str) -> list[MilestoneRecord]:
    """Return milestone schedule for project."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_project_milestones(project)


@router.get("/{project_id}/agencies", response_model=AgencyRecord)
def get_agencies(project_id: str) -> AgencyRecord:
    """Return executing agency and contractor information."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_project_agencies(project)


@router.get("/{project_id}/documents", response_model=list[DocumentRecord])
def get_documents(project_id: str) -> list[DocumentRecord]:
    """Return project documents metadata."""
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return get_project_documents(project_id)


@router.get("/{project_id}/risk", response_model=RiskBreakdown)
def get_risk(project_id: str) -> RiskBreakdown:
    """Return authoritative deterministic risk breakdown computed by Python Risk Engine."""
    risk = get_project_risk(project_id)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return risk

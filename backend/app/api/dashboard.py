"""Dashboard API route for executive summary."""

from fastapi import APIRouter, HTTPException, status
from app.models.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary)
def get_dashboard() -> DashboardSummary:
    """
    Return executive command center metrics.
    All data is derived from real projects in Firebase Realtime Database.
    """
    try:
        return get_dashboard_summary()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

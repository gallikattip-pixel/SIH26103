"""Services package for INFRAPLUS backend."""

from app.services.project_service import (
    create_new_project,
    create_project_snapshot,
    create_project_outcome,
    get_all_projects,
    get_all_projects_enriched,
    get_project_360,
    get_project_agencies,
    get_project_by_id,
    get_project_documents,
    get_project_financial,
    get_project_milestones,
    get_project_outcome,
    get_project_progress,
    get_project_risk,
    get_project_snapshot,
    get_project_snapshots,
    get_project_timeline,
    invalidate_project_caches,
)
from app.services.risk_engine import calculate_risk
from app.services.dashboard_service import get_dashboard_summary, invalidate_dashboard_cache
from app.services.gemini_service import generate_ai_explanation, generate_multi_project_explanation
from app.services.query_engine import (
    analyze_all_projects,
    find_budget_problem_projects,
    find_delayed_projects,
    find_high_risk_projects,
    find_highest_risk,
    find_low_progress_projects,
    find_most_delayed_project,
    find_projects_behind_schedule,
    sort_by_risk,
)
from app.services.firebase_service import (
    fetch_documents_from_firebase,
    fetch_projects_from_firebase,
    fetch_single_project_from_firebase,
    fetch_all_project_snapshots_from_firebase,
    fetch_project_snapshot_from_firebase,
    fetch_project_outcome_from_firebase,
    get_firebase_status,
    save_project_to_firebase,
    save_project_snapshot_to_firebase,
    save_project_outcome_to_firebase,
    save_document_to_firebase,
    delete_document_from_firebase,
    get_document_from_firebase,
    check_snapshot_exists,
    check_outcome_exists,
)
from app.services.prompt_builder import build_prompt, build_multi_project_prompt

__all__ = [
    # Project service
    "create_new_project",
    "create_project_snapshot",
    "create_project_outcome",
    "get_all_projects",
    "get_all_projects_enriched",
    "get_project_360",
    "get_project_agencies",
    "get_project_by_id",
    "get_project_documents",
    "get_project_financial",
    "get_project_milestones",
    "get_project_outcome",
    "get_project_progress",
    "get_project_risk",
    "get_project_snapshot",
    "get_project_snapshots",
    "get_project_timeline",
    "invalidate_project_caches",
    # Risk engine
    "calculate_risk",
    # Dashboard service
    "get_dashboard_summary",
    "invalidate_dashboard_cache",
    # Gemini service
    "generate_ai_explanation",
    "generate_multi_project_explanation",
    # Query engine
    "analyze_all_projects",
    "find_budget_problem_projects",
    "find_delayed_projects",
    "find_high_risk_projects",
    "find_highest_risk",
    "find_low_progress_projects",
    "find_most_delayed_project",
    "find_projects_behind_schedule",
    "sort_by_risk",
    # Firebase service
    "fetch_documents_from_firebase",
    "fetch_projects_from_firebase",
    "fetch_single_project_from_firebase",
    "fetch_all_project_snapshots_from_firebase",
    "fetch_project_snapshot_from_firebase",
    "fetch_project_outcome_from_firebase",
    "get_firebase_status",
    "save_project_to_firebase",
    "save_project_snapshot_to_firebase",
    "save_project_outcome_to_firebase",
    "save_document_to_firebase",
    "delete_document_from_firebase",
    "get_document_from_firebase",
    "check_snapshot_exists",
    "check_outcome_exists",
    # Prompt builder
    "build_prompt",
    "build_multi_project_prompt",
]
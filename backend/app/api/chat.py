"""HTTP routes for the AI assistant.

Preserves the authoritative AI module business logic while connecting to
real project data from Firebase Realtime Database.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.config import (
    RATE_LIMIT_AI_ANON_LIMIT,
    RATE_LIMIT_AI_ANON_WINDOW,
    RATE_LIMIT_AI_AUTH_LIMIT,
    RATE_LIMIT_AI_AUTH_WINDOW,
)
from app.core.rate_limiter import apply_rate_limit, resolve_client_ip
from app.core.security import get_optional_user
from app.models.ai import (
    ChatRequest,
    ChatResponse,
    ProjectRiskSummary,
)
from app.services.gemini_service import (
    generate_ai_explanation,
    generate_multi_project_explanation,
)
from app.services.project_service import (
    get_all_projects,
    get_project_by_id,
)
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
from app.services.risk_engine import calculate_risk


def build_project_summaries(
    project_risks: list[dict],
) -> list[ProjectRiskSummary]:
    """Build project risk summaries for multi-project responses."""
    return [
        ProjectRiskSummary(
            project_id=item["project"].project_id,
            project_name=item["project"].name,
            risk_level=item["risk"].overall_level,
            risk_score=item["risk"].overall_score,
        )
        for item in project_risks
    ]


router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat_with_project_assistant(
    payload: ChatRequest,
    request: Request,
    response: Response,
    current_user: dict[str, Any] | None = Depends(get_optional_user),
) -> ChatResponse:
    """
    Handle project-specific and multi-project questions using real data
    and deterministic Python Risk Engine calculations.
    Rate-limited by Firebase UID for authenticated callers; safely resolved IP for anonymous.
    """
    # Rate limit check: Authenticated (15/60s) vs Anonymous (5/60s)
    if current_user and current_user.get("uid"):
        identity = f"user:{current_user['uid']}"
        limit = RATE_LIMIT_AI_AUTH_LIMIT
        window = RATE_LIMIT_AI_AUTH_WINDOW
    else:
        client_ip = resolve_client_ip(request)
        identity = f"ip:{client_ip}"
        limit = RATE_LIMIT_AI_ANON_LIMIT
        window = RATE_LIMIT_AI_ANON_WINDOW

    apply_rate_limit(
        request=request,
        response=response,
        scope="ai_chat",
        identity=identity,
        limit=limit,
        window_seconds=window,
    )
    # =================================================
    # MODE 1: SPECIFIC PROJECT
    # =================================================
    if payload.project_id:
        try:
            project = get_project_by_id(payload.project_id)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{payload.project_id}' was not found in the database.",
            )

        risk = calculate_risk(project)
        ai = generate_ai_explanation(
            project,
            risk,
            payload.question,
        )

        return ChatResponse(
            answer=ai["answer"],
            risk_level=risk.overall_level,
            risk_score=risk.overall_score,
            major_factors=risk.major_factors,
            recommended_actions=ai.get("recommended_actions", []),
        )

    # =================================================
    # MODE 2: MULTI-PROJECT QUESTIONS
    # =================================================
    try:
        projects = get_all_projects()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No infrastructure projects are currently available in the database.",
        )

    question = payload.question.lower().strip()
    project_risks = analyze_all_projects(projects)

    # =================================================
    # HIGHEST-RISK PROJECT
    # =================================================
    if (
        "highest risk" in question
        or "most risky" in question
        or "maximum risk" in question
    ):
        result = find_highest_risk(project_risks)
        project = result["project"]
        risk = result["risk"]

        ai = generate_ai_explanation(
            project,
            risk,
            payload.question,
        )

        answer = (
            f"The highest-risk project is {project.project_id} ({project.name}). "
            + ai["answer"]
        )

        return ChatResponse(
            answer=answer,
            risk_level=risk.overall_level,
            risk_score=risk.overall_score,
            major_factors=risk.major_factors,
            recommended_actions=ai.get("recommended_actions", []),
            projects=[
                ProjectRiskSummary(
                    project_id=project.project_id,
                    project_name=project.name,
                    risk_level=risk.overall_level,
                    risk_score=risk.overall_score,
                )
            ],
        )

    # =================================================
    # MOST DELAYED PROJECT
    # =================================================
    if (
        "most delayed" in question
        or "highest delay" in question
        or "maximum delay" in question
    ):
        result = find_most_delayed_project(projects)
        if result is None:
            return ChatResponse(
                answer="There are currently no delayed projects in the database.",
                risk_level="LOW",
                risk_score=0,
                major_factors=[],
                recommended_actions=["Continue routine progress tracking."],
                projects=[],
            )

        project = result["project"]
        risk = result["risk"]

        return ChatResponse(
            answer=(
                f"The most delayed project is {project.project_id} "
                f"({project.name}) with an execution delay of {project.delay_days} days."
            ),
            risk_level=risk.overall_level,
            risk_score=risk.overall_score,
            major_factors=risk.major_factors,
            recommended_actions=[
                "Review the project schedule critical path",
                "Assess root causes of the contractor delay",
                "Require an urgent recovery plan from the nodal agency",
            ],
            projects=[
                ProjectRiskSummary(
                    project_id=project.project_id,
                    project_name=project.name,
                    risk_level=risk.overall_level,
                    risk_score=risk.overall_score,
                )
            ],
        )

    # =================================================
    # LOW PHYSICAL PROGRESS
    # =================================================
    if (
        "low physical progress" in question
        or "low progress" in question
        or "lowest progress" in question
    ):
        results = find_low_progress_projects(projects)
        if not results:
            return ChatResponse(
                answer="No projects currently have low physical progress below threshold.",
                risk_level="LOW",
                risk_score=0,
                major_factors=[],
                recommended_actions=[],
                projects=[],
            )

        progress_list = ", ".join(
            f"{item['project'].project_id} ({item['project'].progress}%)"
            for item in results
        )
        highest = max(results, key=lambda item: item["risk"].overall_score)

        return ChatResponse(
            answer=f"Projects with low physical progress: {progress_list}.",
            risk_level=highest["risk"].overall_level,
            risk_score=highest["risk"].overall_score,
            major_factors=highest["risk"].major_factors,
            recommended_actions=[
                "Review physical progress against sanctioned baseline",
                "Identify on-site construction bottlenecks",
                "Increase inspection frequency by supervising engineers",
            ],
            projects=build_project_summaries(results),
        )

    # =================================================
    # PROJECTS BEHIND SCHEDULE
    # =================================================
    if (
        "behind schedule" in question
        or "behind the schedule" in question
        or "behind plan" in question
        or "behind planned progress" in question
    ):
        results = find_projects_behind_schedule(projects)
        if not results:
            return ChatResponse(
                answer="No projects are currently behind their planned schedule.",
                risk_level="LOW",
                risk_score=0,
                major_factors=[],
                recommended_actions=[],
                projects=[],
            )

        schedule_list = ", ".join(
            f"{item['project'].project_id} (actual {item['project'].progress}%, planned {item['project'].planned_progress}%)"
            for item in results
        )
        highest = max(results, key=lambda item: item["risk"].overall_score)

        return ChatResponse(
            answer=f"Projects lagging behind planned progress: {schedule_list}.",
            risk_level=highest["risk"].overall_level,
            risk_score=highest["risk"].overall_score,
            major_factors=highest["risk"].major_factors,
            recommended_actions=[
                "Analyze cause of milestone variance",
                "Enact milestone recovery schedules with contractors",
                "Conduct inter-departmental coordination meeting",
            ],
            projects=build_project_summaries(results),
        )

    # =================================================
    # HIGH-RISK PROJECTS
    # =================================================
    if "high risk" in question or "high-risk" in question:
        results = find_high_risk_projects(project_risks)
        if not results:
            return ChatResponse(
                answer="There are currently no HIGH-risk infrastructure projects in the database.",
                risk_level="LOW",
                risk_score=0,
                major_factors=[],
                recommended_actions=["Maintain current supervisory controls."],
                projects=[],
            )

        total_matching = len(results)
        top_results = results[:10]
        selected_projects = [(item["project"], item["risk"]) for item in top_results]
        ai = generate_multi_project_explanation(selected_projects, payload.question)
        names = [item["project"].project_id for item in top_results]
        highest = max(results, key=lambda item: item["risk"].overall_score)

        answer = f"High-risk projects: {', '.join(names)}. " + ai["answer"]
        if total_matching > 10:
            answer += f" (Note: Analysis focused on top 10 of {total_matching} high-risk projects.)"

        return ChatResponse(
            answer=answer,
            risk_level=highest["risk"].overall_level,
            risk_score=highest["risk"].overall_score,
            major_factors=highest["risk"].major_factors,
            recommended_actions=ai.get("recommended_actions", []),
            projects=build_project_summaries(results),
        )

    # =================================================
    # DELAYED PROJECTS
    # =================================================
    if "delayed" in question or "delay" in question:
        results = find_delayed_projects(projects)
        if not results:
            return ChatResponse(
                answer="There are currently no delayed projects.",
                risk_level="LOW",
                risk_score=0,
                major_factors=[],
                recommended_actions=[],
                projects=[],
            )

        total_matching = len(results)
        top_results = results[:10]
        selected_projects = [(item["project"], item["risk"]) for item in top_results]
        ai = generate_multi_project_explanation(selected_projects, payload.question)
        delay_list = ", ".join(
            f"{item['project'].project_id} ({item['project'].delay_days} days)"
            for item in top_results
        )
        highest = max(results, key=lambda item: item["risk"].overall_score)

        answer = f"Delayed projects, ordered by delay: {delay_list}. " + ai["answer"]
        if total_matching > 10:
            answer += f" (Note: Analysis focused on top 10 of {total_matching} delayed projects.)"

        return ChatResponse(
            answer=answer,
            risk_level=highest["risk"].overall_level,
            risk_score=highest["risk"].overall_score,
            major_factors=highest["risk"].major_factors,
            recommended_actions=ai.get("recommended_actions", []),
            projects=build_project_summaries(results),
        )

    # =================================================
    # BUDGET PROBLEM PROJECTS
    # =================================================
    if "budget problem" in question or "budget problems" in question or "budget issue" in question:
        results = find_budget_problem_projects(project_risks)
        if not results:
            return ChatResponse(
                answer="There are currently no projects exhibiting critical budget problems.",
                risk_level="LOW",
                risk_score=0,
                major_factors=[],
                recommended_actions=[],
                projects=[],
            )

        total_matching = len(results)
        top_results = results[:10]
        selected_projects = [(item["project"], item["risk"]) for item in top_results]
        ai = generate_multi_project_explanation(selected_projects, payload.question)
        budget_list = ", ".join(
            f"{item['project'].project_id} ({item['project'].budget_used:.0f}% used)"
            for item in top_results
        )
        highest = max(results, key=lambda item: item["project"].budget_used)

        answer = f"Projects with high budget utilization: {budget_list}. " + ai["answer"]
        if total_matching > 10:
            answer += f" (Note: Analysis focused on top 10 of {total_matching} budget-impacted projects.)"

        return ChatResponse(
            answer=answer,
            risk_level=highest["risk"].overall_level,
            risk_score=highest["risk"].overall_score,
            major_factors=highest["risk"].major_factors,
            recommended_actions=ai.get("recommended_actions", []),
            projects=build_project_summaries(results),
        )

    # =================================================
    # RISK RANKING
    # =================================================
    if (
        "risk order" in question
        or "order by risk" in question
        or "risk ranking" in question
        or "rank projects" in question
    ):
        results = sort_by_risk(project_risks)
        ranking = ", ".join(
            f"{item['project'].project_id} ({item['risk'].overall_score}/100, {item['risk'].overall_level})"
            for item in results
        )
        highest = results[0]

        return ChatResponse(
            answer=f"Projects ordered from highest risk to lowest risk: {ranking}.",
            risk_level=highest["risk"].overall_level,
            risk_score=highest["risk"].overall_score,
            major_factors=highest["risk"].major_factors,
            recommended_actions=[
                "Prioritize executive review on top-ranked projects",
                "Deploy audit teams to high-risk project locations",
            ],
            projects=build_project_summaries(results),
        )

    # =================================================
    # GENERAL INQUIRY / SUMMARY
    # =================================================
    # Send top-10 projects sorted by risk to multi-project explanation
    sorted_by_risk = sort_by_risk(project_risks)
    total_matching = len(sorted_by_risk)
    top_results = sorted_by_risk[:10]
    selected_projects = [(item["project"], item["risk"]) for item in top_results]
    ai = generate_multi_project_explanation(selected_projects, payload.question)
    highest = max(project_risks, key=lambda item: item["risk"].overall_score)

    answer = ai["answer"]
    if total_matching > 10:
        answer += f" (Note: Analysis focused on top 10 of {total_matching} projects ordered by risk.)"

    return ChatResponse(
        answer=answer,
        risk_level=highest["risk"].overall_level,
        risk_score=highest["risk"].overall_score,
        major_factors=highest["risk"].major_factors,
        recommended_actions=ai.get("recommended_actions", []),
        projects=build_project_summaries(project_risks[:5]),
    )

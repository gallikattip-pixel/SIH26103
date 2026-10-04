"""Understand and process project questions."""

from app.models.project import ProjectRecord
from app.services.risk_engine import calculate_risk


def analyze_all_projects(
    projects: list[ProjectRecord],
) -> list[dict]:
    """Calculate risk for every project."""

    results = []

    for project in projects:
        risk = calculate_risk(project)

        results.append(
            {
                "project": project,
                "risk": risk,
            }
        )

    return results


def find_highest_risk(
    project_risks: list[dict],
) -> dict:
    """Return the project with the highest risk score."""

    if not project_risks:
        raise ValueError(
            "No project risk data available."
        )

    return max(
        project_risks,
        key=lambda item: item["risk"].overall_score,
    )


def sort_by_risk(
    project_risks: list[dict],
) -> list[dict]:
    """Return projects from highest risk to lowest risk."""

    return sorted(
        project_risks,
        key=lambda item: item["risk"].overall_score,
        reverse=True,
    )


def find_high_risk_projects(
    project_risks: list[dict],
) -> list[dict]:
    """Return all projects classified as HIGH risk."""

    return [
        item
        for item in project_risks
        if item["risk"].overall_level == "HIGH"
    ]


def find_delayed_projects(
    projects: list[ProjectRecord],
) -> list[dict]:
    """Return projects that have schedule delays."""

    delayed = []

    for project in projects:

        if project.delay_days > 0:

            delayed.append(
                {
                    "project": project,
                    "risk": calculate_risk(project),
                }
            )

    return sorted(
        delayed,
        key=lambda item: item["project"].delay_days,
        reverse=True,
    )


def find_most_delayed_project(
    projects: list[ProjectRecord],
) -> dict | None:
    """Return the project with the highest delay."""

    delayed = find_delayed_projects(
        projects
    )

    if not delayed:
        return None

    return delayed[0]


def find_budget_problem_projects(
    project_risks: list[dict],
) -> list[dict]:
    """Return projects with high budget utilization."""

    return [
        item
        for item in project_risks
        if item["project"].budget_used >= 80
    ]


def find_low_progress_projects(
    projects: list[ProjectRecord],
    threshold: float = 50,
) -> list[dict]:
    """Return projects with physical progress below a threshold."""

    results = []

    for project in projects:

        if project.progress < threshold:

            results.append(
                {
                    "project": project,
                    "risk": calculate_risk(project),
                }
            )

    return sorted(
        results,
        key=lambda item: item["project"].progress,
    )


def find_projects_behind_schedule(
    projects: list[ProjectRecord],
) -> list[dict]:
    """Return projects where actual progress is below planned progress."""

    results = []

    for project in projects:

        if project.progress < project.planned_progress:

            results.append(
                {
                    "project": project,
                    "risk": calculate_risk(project),
                }
            )

    return sorted(
        results,
        key=lambda item: (
            item["project"].planned_progress
            - item["project"].progress
        ),
        reverse=True,
    )

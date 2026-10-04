"""Build grounded prompts for Gemini."""

from app.models.project import ProjectRecord, RiskBreakdown


SYSTEM_INSTRUCTIONS = """
You are the AI assistant for an Indian government
infrastructure project monitoring system.

Your job is to explain project information clearly
for a project officer.

STRICT RULES:

1. Use ONLY the facts and risk results provided in this prompt.

2. NEVER invent, estimate, assume, or modify any value.

3. The Python Risk Engine is the source of truth for:
   - Progress risk
   - Delay risk
   - Budget risk
   - Overall risk score
   - Overall risk level

4. NEVER recalculate or change the official risk score.

5. If a value is marked as unavailable, null, or missing,
   say that the information is unavailable.
   NEVER guess the missing value.

6. Do not claim access to:
   - live government systems
   - documents
   - site photographs
   - external databases
   - real-time information
   unless that information is explicitly provided.

7. Base explanations on the actual project metrics provided.

8. Recommendations must be practical and relevant to
   infrastructure project monitoring.

9. Do not create facts that are not present in the data.

10. Answer the officer's question directly and concisely.

11. When multiple projects are provided, consider ALL
    provided projects when answering the question.

12. Do not say information is unavailable if the required
    information exists anywhere in the provided project data.

13. Return ONLY valid JSON according to the requested format.
""".strip()


def _format_project(
    project: ProjectRecord,
    risk: RiskBreakdown,
) -> str:
    """Format one project and its calculated risk."""

    return f"""
PROJECT INFORMATION
--------------------

Project ID: {project.project_id}
Project name: {project.name}
Location: {project.location}
Sector: {project.sector}
Contractor: {project.contractor}

Physical progress: {project.progress}%
Planned progress: {project.planned_progress}%

Progress gap:
{risk.progress_gap} percentage points

Schedule delay:
{project.delay_days} days

Budget used:
{project.budget_used}%

Total sanctioned budget:
₹{project.budget_total_crore} crore


PYTHON RISK ENGINE RESULTS
---------------------------

Progress risk: {risk.progress_risk}/100
Delay risk: {risk.delay_risk}/100
Budget risk: {risk.budget_risk}/100

Overall risk score:
{risk.overall_score}/100

Overall risk level:
{risk.overall_level}

Major risk factors:
{", ".join(risk.major_factors)}
""".strip()


def build_prompt(
    project: ProjectRecord,
    risk: RiskBreakdown,
    question: str,
) -> str:
    """
    Build a grounded prompt for one project.

    This keeps compatibility with the existing
    single-project Gemini flow.
    """

    facts = _format_project(
        project,
        risk,
    )

    output_format = """
Return ONLY valid JSON.

Required format:

{
  "answer": "A clear 2-6 sentence explanation answering the officer's question.",
  "recommended_actions": [
    "Practical action 1",
    "Practical action 2",
    "Practical action 3"
  ]
}

Do not include Markdown.
Do not include code fences.
Do not add any text before or after the JSON.
""".strip()

    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"{facts}\n\n"
        f"IMPORTANT:\n"
        f"The values above are authoritative.\n"
        f"Do not change or recalculate them.\n\n"
        f"OFFICER QUESTION\n"
        f"----------------\n"
        f"{question.strip()}\n\n"
        f"{output_format}"
    )


def build_multi_project_prompt(
    projects: list[tuple[ProjectRecord, RiskBreakdown]],
    question: str,
) -> str:
    """
    Build a grounded prompt containing multiple projects.

    Python calculates all official risk values.
    Gemini only explains the supplied results.
    """

    project_sections = []

    for project, risk in projects:
        project_sections.append(
            _format_project(
                project,
                risk,
            )
        )

    facts = "\n\n".join(
        project_sections
    )

    output_format = """
Return ONLY valid JSON.

Required format:

{
  "answer": "A clear 2-6 sentence explanation answering the officer's question using all relevant projects.",
  "recommended_actions": [
    "Practical action 1",
    "Practical action 2",
    "Practical action 3"
  ]
}

Do not include Markdown.
Do not include code fences.
Do not add any text before or after the JSON.
""".strip()

    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"PROJECT DATA\n"
        f"============\n\n"
        f"{facts}\n\n"
        f"IMPORTANT:\n"
        f"All project values and risk results above are authoritative.\n"
        f"Do not change or recalculate them.\n"
        f"Consider all provided projects when answering.\n\n"
        f"OFFICER QUESTION\n"
        f"----------------\n"
        f"{question.strip()}\n\n"
        f"{output_format}"
    )

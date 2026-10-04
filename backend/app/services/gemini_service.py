"""Call Gemini to explain calculated project risk."""

import json
import logging
import re
import time

from google import genai
from google.genai import types

from app.config import (
    GEMINI_MODEL,
    require_gemini_api_key,
)
from app.models.project import ProjectRecord, RiskBreakdown
from app.services.prompt_builder import (
    build_multi_project_prompt,
    build_prompt,
)

logger = logging.getLogger("infraplus.gemini")


def _extract_json(text: str) -> dict:
    """Parse JSON even if Gemini returns Markdown code fences."""

    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

    return json.loads(cleaned)


def _fallback_explanation(
    project: ProjectRecord,
    risk: RiskBreakdown,
) -> dict:
    """Return a useful answer when Gemini is unavailable."""

    metrics = risk.metrics

    answer = (
        f"{project.project_id} ({project.name}) is assessed as "
        f"{risk.overall_level} risk with a score of "
        f"{risk.overall_score}/100. "
        f"Physical progress is {metrics['progress']}% against "
        f"a planned {metrics['planned_progress']}%, with a "
        f"progress gap of {risk.progress_gap} points. "
        f"The project has a schedule delay of "
        f"{metrics['delay_days']} days and budget utilization "
        f"of {metrics['budget_used']}%. "
        f"Main factors: {', '.join(risk.major_factors)}."
    )

    if risk.overall_level == "HIGH":
        actions = [
            "Review contractor performance",
            "Reassess the project schedule",
            "Conduct a financial review",
        ]

    elif risk.overall_level == "MEDIUM":
        actions = [
            "Review current project progress",
            "Monitor schedule and expenditure closely",
            "Follow up on emerging risk factors",
        ]

    else:
        actions = [
            "Continue routine monitoring",
            "Keep progress and expenditure aligned",
            "Monitor for emerging risk factors",
        ]

    return {
        "answer": answer,
        "recommended_actions": actions,
    }


def _fallback_multi_project_explanation(
    projects: list[tuple[ProjectRecord, RiskBreakdown]],
) -> dict:
    """Return a useful answer when Gemini is unavailable."""

    if not projects:
        return {
            "answer": "No relevant project data was found.",
            "recommended_actions": [],
        }

    ordered = sorted(
        projects,
        key=lambda item: item[1].overall_score,
        reverse=True,
    )

    project_summary = ", ".join(
        f"{project.project_id} "
        f"({risk.overall_score}/100, {risk.overall_level})"
        for project, risk in ordered
    )

    highest_project, highest_risk = ordered[0]

    answer = (
        f"Projects ordered by risk are: {project_summary}. "
        f"The highest-risk project is "
        f"{highest_project.project_id} with a risk score of "
        f"{highest_risk.overall_score}/100."
    )

    return {
        "answer": answer,
        "recommended_actions": [
            "Review the highest-risk projects first",
            "Monitor schedule and physical progress",
            "Review expenditure against project execution",
        ],
    }


def _call_gemini(prompt: str) -> dict:
    """Send a prompt to Gemini and return parsed JSON."""

    client = genai.Client(
        api_key=require_gemini_api_key(),
        http_options=types.HttpOptions(timeout=15000),
    )

    response = None
    max_retries = 3
    start_time = time.perf_counter()

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                f"Gemini API call completed in {duration_ms}ms | model={GEMINI_MODEL} | attempt={attempt + 1}"
            )
            break

        except Exception as exc:
            error_text = str(exc)
            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            )

            if not is_temporary_error or attempt == max_retries - 1:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.error(
                    f"Gemini upstream call failed after {duration_ms}ms | model={GEMINI_MODEL} "
                    f"| error_type={type(exc).__name__} | is_temporary={is_temporary_error}"
                )
                raise

            wait_time = 2 ** attempt
            logger.warning(
                f"Gemini temporarily unavailable (attempt {attempt + 1}/{max_retries}). "
                f"Retrying in {wait_time}s | model={GEMINI_MODEL}"
            )
            time.sleep(wait_time)

    if response is None:
        raise RuntimeError("Gemini did not return a response.")

    parsed = _extract_json(response.text or "")

    answer = str(parsed.get("answer", "")).strip()
    actions = parsed.get("recommended_actions", [])

    if not isinstance(actions, list):
        actions = [str(actions)]

    actions = [
        str(action).strip()
        for action in actions
        if str(action).strip()
    ]

    if not answer:
        raise ValueError("Gemini returned an empty answer.")

    return {
        "answer": answer,
        "recommended_actions": actions[:6],
    }


def generate_ai_explanation(
    project: ProjectRecord,
    risk: RiskBreakdown,
    question: str,
) -> dict:
    """
    Ask Gemini to explain the calculated risk for one project.

    Python calculates the official risk.
    Gemini explains the result and recommends actions.
    """

    prompt = build_prompt(
        project,
        risk,
        question,
    )

    try:
        return _call_gemini(prompt)

    except Exception as exc:
        logger.warning(
            f"Gemini explanation generation failed: {type(exc).__name__}. "
            f"Activating deterministic fallback explanation | project_id={project.project_id}"
        )
        return _fallback_explanation(
            project,
            risk,
        )


def generate_multi_project_explanation(
    projects: list[tuple[ProjectRecord, RiskBreakdown]],
    question: str,
) -> dict:
    """
    Ask Gemini to explain multiple projects.

    Python calculates all official risk values.
    Gemini only explains the supplied results.
    """

    if not projects:
        return {
            "answer": "No relevant project data was found.",
            "recommended_actions": [],
        }

    # Hard cap prompt context to top 10 to prevent prompt bloat and latency spikes
    capped_projects = projects[:10]

    prompt = build_multi_project_prompt(
        capped_projects,
        question,
    )

    try:
        return _call_gemini(prompt)

    except Exception as exc:
        logger.warning(
            f"Gemini multi-project explanation failed: {type(exc).__name__}. "
            f"Activating deterministic multi-project fallback explanation | projects_count={len(capped_projects)}"
        )
        return _fallback_multi_project_explanation(
            capped_projects,
        )


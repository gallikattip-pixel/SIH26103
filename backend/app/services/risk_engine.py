"""Deterministic risk scoring. Gemini must not invent these numbers."""

from app.models.project import ProjectRecord, RiskBreakdown


def _clamp(
    value: float,
    low: float = 0,
    high: float = 100,
) -> int:
    """Keep a risk value between 0 and 100."""

    return int(
        round(
            min(
                high,
                max(low, value),
            )
        )
    )


def _risk_level(score: int) -> str:
    """Convert the risk score into a risk level."""

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def calculate_risk(
    project: ProjectRecord,
) -> RiskBreakdown:
    """
    Calculate deterministic project risk.

    Gemini is NOT used to calculate these numbers.

    Components:
        progress_risk -> project progress compared with plan
        delay_risk    -> schedule delay
        budget_risk   -> budget utilization and spending ahead of work

    Overall score:
        35% progress risk
        40% delay risk
        25% budget risk
    """

    # =========================================================
    # 1. PROGRESS RISK
    # =========================================================

    # Positive value means actual progress is behind plan.
    progress_gap = round(
        project.planned_progress - project.progress,
        2,
    )

    # A 40 percentage-point gap produces maximum risk.
    # If the project is ahead of plan, risk is zero.
    progress_risk = _clamp(
        max(progress_gap, 0) * 2.5
    )

    # =========================================================
    # 2. DELAY RISK
    # =========================================================

    # 90 days of delay produces maximum risk.
    delay_risk = _clamp(
        (project.delay_days / 90) * 100
    )

    # =========================================================
    # 3. BUDGET RISK
    # =========================================================

    # Spending more than physical progress is a warning sign.
    spend_ahead_of_work = max(
        project.budget_used - project.progress,
        0,
    )

    # Combine total budget utilization and spending
    # ahead of physical progress.
    budget_risk = _clamp(
        (0.55 * project.budget_used)
        + (0.45 * spend_ahead_of_work)
    )

    # =========================================================
    # 4. OVERALL RISK
    # =========================================================

    overall_score = _clamp(
        (0.35 * progress_risk)
        + (0.40 * delay_risk)
        + (0.25 * budget_risk)
    )

    overall_level = _risk_level(
        overall_score
    )

    # =========================================================
    # 5. MAJOR RISK FACTORS
    # =========================================================

    factors: list[str] = []

    # Schedule
    if (
        delay_risk >= 70
        or project.delay_days >= 90
    ):
        factors.append(
            "Significant schedule delay"
        )

    elif delay_risk >= 40:
        factors.append(
            "Moderate schedule delay"
        )

    # Physical progress
    if (
        progress_risk >= 70
        or progress_gap >= 20
    ):
        factors.append(
            "Low physical progress"
        )

    elif progress_risk >= 40:
        factors.append(
            "Progress lagging behind plan"
        )

    # Budget
    if (
        budget_risk >= 70
        or project.budget_used >= 85
    ):
        factors.append(
            "High budget utilization"
        )

    elif spend_ahead_of_work >= 20:
        factors.append(
            "Budget spend is ahead of physical progress"
        )

    # If nothing significant was detected.
    if not factors:
        factors.append(
            "No major risk flags from current metrics"
        )

    # =========================================================
    # 6. RETURN STRUCTURED RISK RESULT
    # =========================================================

    return RiskBreakdown(
        progress_gap=progress_gap,
        progress_risk=progress_risk,
        delay_risk=delay_risk,
        budget_risk=budget_risk,
        overall_score=overall_score,
        overall_level=overall_level,
        major_factors=factors,
        metrics={
            "progress": project.progress,
            "planned_progress": project.planned_progress,
            "delay_days": project.delay_days,
            "budget_used": project.budget_used,
        },
    )

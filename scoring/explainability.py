from dataclasses import asdict
from typing import Dict

from models.schedule import WeekPlan
from models.task import TaskSegment
from models.user_preferences import UserPreferences

from scoring.objectives import ObjectiveScore, AUTONOMY_WEIGHTS
from scoring.score_function import score_schedule


def explain_schedule(
    week_plan: WeekPlan,
    segments: list[TaskSegment],
    user_preferences: UserPreferences
) -> Dict:
    """
    Returns a full explainability report for a weekly schedule.
    """

    # We recompute the objective breakdown explicitly
    from scoring.score_function import _compute_objectives  # internal helper

    objectives: ObjectiveScore = _compute_objectives(
        week_plan, segments, user_preferences
    )

    weights = AUTONOMY_WEIGHTS[user_preferences.autonomy_level]

    weighted_score = objectives.weighted_sum(weights)

    weighted_breakdown = {
        key: getattr(objectives, key) * weights[key]
        for key in weights
    }

    return {
        "autonomy_level": user_preferences.autonomy_level,
        "objectives_raw": asdict(objectives),
        "weights": weights,
        "objectives_weighted": weighted_breakdown,
        "final_score": weighted_score,
    }

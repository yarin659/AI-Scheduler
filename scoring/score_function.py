# scoring/score_function.py

from typing import List, Dict, Set
from collections import defaultdict

from models.schedule import WeekPlan, DayPlan
from models.task import TaskSegment
from models.user_preferences import UserPreferences
from scoring.objectives import ObjectiveScore, AUTONOMY_WEIGHTS
from constraints.hard_constraints import validate_week_hard_constraints
from constraints.soft_constraints import (
    completion_score,
    deadline_score,
    preferred_time_score,
    frequency_score,
    load_balance_score,
    night_work_penalty,
    daily_load_balance_score,
    rest_day_bonus,
    round_time_preference
)


def score_schedule(
    week_plan: WeekPlan,
    segments: List[TaskSegment],
    user_preferences: UserPreferences
) -> float:
    """
    Computes a WEEKLY schedule score using multi-objective scoring.
    Returns -inf if any hard constraint is violated.
    """

    # -------------------------------------------------
    # Preprocessing
    # -------------------------------------------------

    scheduled_segment_ids: Set[str] = set()

    for day in week_plan.days:
        for block in day.blocks:
            if not block.is_fixed:
                scheduled_segment_ids.add(block.item_id)

    segments_by_task: Dict[str, List[TaskSegment]] = defaultdict(list)
    for segment in segments:
        segments_by_task[segment.task_id].append(segment)

    # -------------------------------------------------
    # HARD CONSTRAINTS
    # -------------------------------------------------
    if not validate_week_hard_constraints(week_plan, segments):
        return float("-inf")

    # -------------------------------------------------
    # SOFT SCORING — COLLECT OBJECTIVES
    # -------------------------------------------------

    objective_score = _compute_objectives(
        week_plan=week_plan,
        segments=segments,
        user_preferences=user_preferences
    )

    # -------------------------------------------------
    # MULTI-OBJECTIVE AGGREGATION
    # -------------------------------------------------

    weights = AUTONOMY_WEIGHTS[user_preferences.autonomy_level]

    return objective_score.weighted_sum(weights)

def _compute_objectives(
    week_plan: WeekPlan,
    segments: List[TaskSegment],
    user_preferences: UserPreferences
) -> ObjectiveScore:

    """
    Internal helper: computes raw ObjectiveScore without weighting.
    """
    scheduled_segment_ids = set()
    for day in week_plan.days:
        for block in day.blocks:
            if not block.is_fixed:
                scheduled_segment_ids.add(block.item_id)

    segments_by_task = defaultdict(list)
    for s in segments:
        segments_by_task[s.task_id].append(s)

    productivity = 0
    balance = 0
    wellbeing = 0
    preferences = 0

    for task_segments in segments_by_task.values():
        productivity += completion_score(task_segments, scheduled_segment_ids)
        productivity += deadline_score(task_segments, week_plan)

        preferences += frequency_score(
            task_segments, week_plan, user_preferences
        )

        balance += load_balance_score(task_segments, week_plan)

    for day in week_plan.days:
        preferences += preferred_time_score(day, user_preferences)
        wellbeing += night_work_penalty(day)
        balance += daily_load_balance_score(day)
        wellbeing += round_time_preference(day)

    wellbeing += rest_day_bonus(week_plan)

    return ObjectiveScore(
        productivity=productivity,
        balance=balance,
        wellbeing=wellbeing,
        preferences=preferences
    )


# scoring/score_function.py

from typing import List, Dict, Set
from collections import defaultdict

from models.schedule import WeekPlan, DayPlan
from models.task import TaskSegment
from models.user_preferences import UserPreferences

from scoring.objectives import ObjectiveScore, AUTONOMY_WEIGHTS

from constraints.hard_constraints import (
    no_overlap_constraint,
    respects_fixed_events_constraint,
    deadline_hard_constraint,
    minimum_completion_constraint,
)

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

    # Day-level hard constraints
    for day in week_plan.days:
        if not no_overlap_constraint(day):
            return float("-inf")

        if not respects_fixed_events_constraint(day):
            return float("-inf")

    # Task-level hard constraints (checked per day)
    for task_segments in segments_by_task.values():
        for day in week_plan.days:
            if not deadline_hard_constraint(task_segments, day):
                return float("-inf")

        if not minimum_completion_constraint(
            task_segments,
            scheduled_segment_ids
        ):
            return float("-inf")

    # -------------------------------------------------
    # SOFT SCORING — COLLECT OBJECTIVES
    # -------------------------------------------------

    productivity = 0.0
    balance = 0.0
    wellbeing = 0.0
    preferences = 0.0

    # Task-level weekly objectives
    for task_segments in segments_by_task.values():
        productivity += completion_score(task_segments, scheduled_segment_ids)
        productivity += deadline_score(task_segments, week_plan)

        preferences += frequency_score(
            task_segments,
            week_plan,
            user_preferences
        )

        balance += load_balance_score(task_segments, week_plan)

    # Day / week level objectives
    for day in week_plan.days:
        preferences += preferred_time_score(day, user_preferences)
        wellbeing += night_work_penalty(day)
        balance += daily_load_balance_score(day)
        wellbeing += round_time_preference(day)

    wellbeing += rest_day_bonus(week_plan)

    # -------------------------------------------------
    # MULTI-OBJECTIVE AGGREGATION
    # -------------------------------------------------

    objective_score = ObjectiveScore(
        productivity=productivity,
        balance=balance,
        wellbeing=wellbeing,
        preferences=preferences
    )

    weights = AUTONOMY_WEIGHTS[user_preferences.autonomy_level]

    return objective_score.weighted_sum(weights)

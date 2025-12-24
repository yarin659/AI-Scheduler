# scoring/score_function.py

from typing import List, Dict
from collections import defaultdict

from models.schedule import DayPlan
from models.task import TaskSegment
from models.user_preferences import UserPreferences

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
    day_plan: DayPlan,
    segments: List[TaskSegment],
    user_preferences: UserPreferences
) -> int:
    """
    Computes a schedule score.
    Returns -inf if any hard constraint is violated.
    """

    # -----------------------
    # Preprocessing
    # -----------------------

    scheduled_segment_ids = {
        block.item_id
        for block in day_plan.blocks
        if not block.is_fixed
    }

    segments_by_task: Dict[str, List[TaskSegment]] = defaultdict(list)
    for segment in segments:
        segments_by_task[segment.task_id].append(segment)

    # -----------------------
    # HARD CONSTRAINTS
    # -----------------------

    # Global hard constraints
    if not no_overlap_constraint(day_plan):
        return float("-inf")

    if not respects_fixed_events_constraint(day_plan):
        return float("-inf")

    # Per-task hard constraints
    for task_segments in segments_by_task.values():
        if not deadline_hard_constraint(task_segments, day_plan):
            return float("-inf")

        if not minimum_completion_constraint(task_segments, scheduled_segment_ids):
            return float("-inf")

    # -----------------------
    # SOFT SCORING
    # -----------------------

    score = 0

    # Task-level soft constraints
    for task_segments in segments_by_task.values():
        score += completion_score(task_segments, scheduled_segment_ids)
        score += deadline_score(task_segments, day_plan)
        score += preferred_time_score(task_segments, day_plan, user_preferences)
        score += frequency_score(task_segments, day_plan, user_preferences)
        score += load_balance_score(task_segments, day_plan)

    # Global soft constraints (apply once per day)
    score += night_work_penalty(day_plan)
    score += daily_load_balance_score(day_plan)
    score += rest_day_bonus(day_plan)
    score += round_time_preference(day_plan)

    return score

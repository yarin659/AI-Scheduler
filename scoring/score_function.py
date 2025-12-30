# scoring/score_function.py

from typing import List, Dict, Set
from collections import defaultdict

from models.schedule import WeekPlan
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
    week_plan: WeekPlan,
    segments: List[TaskSegment],
    user_preferences: UserPreferences
) -> int:
    """
    Computes a WEEKLY schedule score.
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
    # HARD CONSTRAINTS (Day + Week)
    # -------------------------------------------------

    # Day-level hard constraints
    for day in week_plan.days:
        if not no_overlap_constraint(day):
            return float("-inf")

        if not respects_fixed_events_constraint(day):
            return float("-inf")

    # Task-level hard constraints (weekly)
    for task_segments in segments_by_task.values():
        if not deadline_hard_constraint(task_segments, week_plan):
            return float("-inf")

        if not minimum_completion_constraint(
            task_segments,
            scheduled_segment_ids
        ):
            return float("-inf")

    # -------------------------------------------------
    # SOFT SCORING
    # -------------------------------------------------

    score = 0

    # Task-level weekly soft constraints
    for task_segments in segments_by_task.values():
        score += completion_score(task_segments, scheduled_segment_ids)
        score += deadline_score(task_segments, week_plan)
        score += frequency_score(
            task_segments,
            week_plan,
            user_preferences
        )
        score += load_balance_score(task_segments, week_plan)

    # Week-level soft constraints
    score += preferred_time_score(week_plan, user_preferences)
    score += night_work_penalty(week_plan)
    score += daily_load_balance_score(week_plan)
    score += rest_day_bonus(week_plan)
    score += round_time_preference(week_plan)

    return score

# constraints/soft_constraints.py

from typing import List, Set
from collections import defaultdict

from models.task import TaskSegment
from models.user_preferences import UserPreferences
from models.schedule import WeekPlan


# -------------------------------------------------
# Task-level scores (weekly)
# -------------------------------------------------

def completion_score(
    task_segments: List[TaskSegment],
    scheduled_segment_ids: Set[str]
) -> int:
    priority = task_segments[0].priority
    total_segments = len(task_segments)

    completed = len(
        [s for s in task_segments if s.segment_id in scheduled_segment_ids]
    )

    if total_segments == 0:
        return 0

    ratio = completed / total_segments
    score = priority * 100 * ratio

    if ratio == 1.0:
        score += priority * 50
    else:
        score -= priority * 30 * (1.0 - ratio)

    return int(score)


def deadline_score(
    task_segments: List[TaskSegment],
    week_plan: WeekPlan
) -> int:
    priority = task_segments[0].priority
    deadline_day = task_segments[0].deadline_day

    if deadline_day is None:
        return 0

    scheduled_days = []

    for day in week_plan.days:
        for block in day.blocks:
            if (
                not block.is_fixed
                and block.item_id in {s.segment_id for s in task_segments}
            ):
                scheduled_days.append(block.day)

    if not scheduled_days:
        return 0

    latest_day = max(scheduled_days)
    diff = deadline_day - latest_day

    if diff < 0:
        return -priority * 80 * abs(diff)

    if diff <= 1:
        return priority * 20

    return 0


def frequency_score(
    task_segments: List[TaskSegment],
    week_plan: WeekPlan,
    user_preferences: UserPreferences
) -> int:
    task_id = task_segments[0].task_id
    priority = task_segments[0].priority

    desired = user_preferences.desired_frequencies.get(task_id)
    if desired is None:
        return 0

    scheduled_days = set()

    for day in week_plan.days:
        for block in day.blocks:
            if (
                not block.is_fixed
                and block.item_id in {s.segment_id for s in task_segments}
            ):
                scheduled_days.add(day.day_index)

    actual = len(scheduled_days)
    diff = abs(actual - desired)

    if diff == 0:
        return priority * 25

    return -priority * 10 * diff


def load_balance_score(
    task_segments: List[TaskSegment],
    week_plan: WeekPlan
) -> int:
    counts = defaultdict(int)
    priority = task_segments[0].priority

    for day in week_plan.days:
        for block in day.blocks:
            if (
                not block.is_fixed
                and block.item_id in {s.segment_id for s in task_segments}
            ):
                counts[day.day_index] += 1

    if not counts:
        return 0

    imbalance = max(counts.values()) - min(counts.values())
    return -priority * imbalance * 5


# -------------------------------------------------
# Week-level soft constraints
# -------------------------------------------------

def preferred_time_score(
    week_plan: WeekPlan,
    user_preferences: UserPreferences
) -> int:
    score = 0

    for day in week_plan.days:
        for block in day.blocks:
            if block.is_fixed:
                continue

            start_hour = block.start_min // 60

            if any(
                start <= start_hour < end
                for start, end in user_preferences.preferred_time_ranges
            ):
                score += 10

            if any(
                start <= start_hour < end
                for start, end in user_preferences.avoided_time_ranges
            ):
                score -= 15

    return score


def night_work_penalty(week_plan: WeekPlan) -> int:
    penalty = 0

    for day in week_plan.days:
        for block in day.blocks:
            if block.is_fixed:
                continue

            hour = block.start_min // 60
            if 0 <= hour < 6:
                penalty -= 20

    return penalty


def daily_load_balance_score(week_plan: WeekPlan) -> int:
    counts = defaultdict(int)

    for day in week_plan.days:
        for block in day.blocks:
            if not block.is_fixed:
                counts[day.day_index] += 1

    if not counts:
        return 0

    return -(max(counts.values()) - min(counts.values())) * 15


def rest_day_bonus(week_plan: WeekPlan) -> int:
    counts = defaultdict(int)

    for day in week_plan.days:
        for block in day.blocks:
            if not block.is_fixed:
                counts[day.day_index] += 1

    for day in range(7):
        if counts.get(day, 0) == 0:
            return 50
        if counts.get(day, 0) <= 1:
            return 25

    return 0


def round_time_preference(week_plan: WeekPlan) -> int:
    score = 0

    for day in week_plan.days:
        for block in day.blocks:
            if block.is_fixed:
                continue

            minute = block.start_min % 60
            if minute in (0, 30):
                score += 5
            else:
                score -= 5

    return score

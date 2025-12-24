# constraints/soft_constraints.py

from typing import List, Set
from collections import defaultdict

from models.task import TaskSegment
from models.user_preferences import UserPreferences


def completion_score(task_segments: List[TaskSegment], scheduled_segment_ids: Set[str]) -> int:
    """
    Scores task completion proportionally.
    Full completion yields a bonus, partial completion yields a soft penalty.
    """

    priority = task_segments[0].priority
    total_segments = len(task_segments)

    scheduled_segments = [
        s for s in task_segments
        if s.segment_id in scheduled_segment_ids
    ]

    completed_count = len(scheduled_segments)
    completion_ratio = completed_count / total_segments

    score = priority * 100 * completion_ratio

    if completion_ratio == 1.0:
        score += priority * 50
    else:
        score -= priority * 30 * (1.0 - completion_ratio)

    return int(score)


def deadline_score(task_segments, day_plan):
    """
    Applies soft penalties or bonuses based on task deadline proximity.
    """

    priority = task_segments[0].priority
    deadline_day = task_segments[0].deadline_day

    if deadline_day is None:
        return 0

    blocks_by_item = {
        block.item_id: block
        for block in day_plan.blocks
        if not block.is_fixed
    }

    scheduled_blocks = [
        blocks_by_item.get(segment.segment_id)
        for segment in task_segments
        if blocks_by_item.get(segment.segment_id) is not None
    ]

    if not scheduled_blocks:
        return 0

    latest_day = max(block.day for block in scheduled_blocks)
    days_diff = deadline_day - latest_day

    if days_diff < 0:
        return -priority * 80 * abs(days_diff)

    if days_diff <= 1:
        return priority * 20

    return 0


def preferred_time_score(task_segments, day_plan, user_preferences):
    """
    Rewards or penalizes scheduling based on preferred or avoided time ranges.
    """

    priority = task_segments[0].priority
    score = 0

    blocks_by_item = {
        block.item_id: block
        for block in day_plan.blocks
        if not block.is_fixed
    }

    for segment in task_segments:
        block = blocks_by_item.get(segment.segment_id)
        if block is None:
            continue

        start_hour = block.start_min // 60

        if any(start <= start_hour < end for start, end in user_preferences.preferred_time_ranges):
            score += priority * 10

        if any(start <= start_hour < end for start, end in user_preferences.avoided_time_ranges):
            score -= priority * 15

    return score

def frequency_score(task_segments, day_plan, user_preferences):
    """
    Scores how well the task scheduling matches the desired weekly frequency.
    """

    task_id = task_segments[0].task_id
    priority = task_segments[0].priority

    desired_frequency = user_preferences.desired_frequencies.get(task_id)
    if desired_frequency is None:
        return 0

    blocks_by_item = {
        block.item_id: block
        for block in day_plan.blocks
        if not block.is_fixed
    }

    scheduled_days = {
        blocks_by_item[segment.segment_id].day
        for segment in task_segments
        if segment.segment_id in blocks_by_item
    }

    actual_frequency = len(scheduled_days)
    diff = abs(actual_frequency - desired_frequency)

    if diff == 0:
        return priority * 25

    return -priority * 10 * diff


def load_balance_score(task_segments, day_plan):
    """
    Penalizes uneven distribution of task segments across days.
    """

    day_counts = {}

    blocks_by_item = {
        block.item_id: block
        for block in day_plan.blocks
        if not block.is_fixed
    }

    for segment in task_segments:
        block = blocks_by_item.get(segment.segment_id)
        if block is None:
            continue

        day = block.day
        day_counts[day] = day_counts.get(day, 0) + 1

    if not day_counts:
        return 0

    counts = list(day_counts.values())
    max_load = max(counts)
    min_load = min(counts)

    imbalance = max_load - min_load

    priority = task_segments[0].priority

    return -priority * imbalance * 5

def night_work_penalty(day_plan):
    """
    Penalizes scheduling work/study tasks during night hours (00:00–06:00).
    """

    penalty = 0

    for block in day_plan.blocks:
        if block.is_fixed:
            continue

        start_hour = block.start_min // 60
        if 0 <= start_hour < 6:
            penalty -= 20

    return penalty


def daily_load_balance_score(day_plan):
    """
    Penalizes uneven distribution of blocks across days.
    """

    day_counts = defaultdict(int)

    for block in day_plan.blocks:
        if block.is_fixed:
            continue
        day_counts[block.day] += 1

    if not day_counts:
        return 0

    max_load = max(day_counts.values())
    min_load = min(day_counts.values())

    return -(max_load - min_load) * 15


def rest_day_bonus(day_plan):
    """
    Rewards having at least one light or free day.
    """

    day_counts = defaultdict(int)

    for block in day_plan.blocks:
        if block.is_fixed:
            continue
        day_counts[block.day] += 1

    for day in range(7):
        if day_counts.get(day, 0) == 0:
            return 50   # full rest day bonus

        if day_counts.get(day, 0) <= 1:
            return 25   # light day bonus

    return 0


def round_time_preference(day_plan):
    """
    Prefers blocks that start at round times (00 or 30).
    """

    score = 0

    for block in day_plan.blocks:
        if block.is_fixed:
            continue

        minute = block.start_min % 60
        if minute in (0, 30):
            score += 5
        else:
            score -= 5

    return score
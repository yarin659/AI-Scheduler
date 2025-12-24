# constraints/hard_constraints.py

from typing import List, Set
from models.schedule import DayPlan
from models.task import TaskSegment
from models.schedule import ScheduleBlock



def no_overlap_constraint(day_plan: DayPlan) -> bool:
    """
    Ensures that no two non-fixed blocks overlap in time.
    """

    blocks = sorted(day_plan.blocks, key=lambda b: (b.day, b.start_min))

    for i in range(len(blocks) - 1):
        current = blocks[i]
        next_block = blocks[i + 1]

        if current.day != next_block.day:
            continue

        if current.end_min > next_block.start_min:
            return False

    return True


def respects_fixed_events_constraint(day_plan: DayPlan) -> bool:
    """
    Ensures that scheduled tasks do not overlap with fixed events.
    """

    fixed_blocks = [b for b in day_plan.blocks if b.is_fixed]
    task_blocks = [b for b in day_plan.blocks if not b.is_fixed]

    for task in task_blocks:
        for fixed in fixed_blocks:
            if task.day != fixed.day:
                continue

            if not (task.end_min <= fixed.start_min or task.start_min >= fixed.end_min):
                return False

    return True


def deadline_hard_constraint(
    task_segments,
    day_plan
) -> bool:
    """
    Ensures that no task segment is scheduled after its hard deadline.
    """

    blocks_by_item = {
        block.item_id: block
        for block in day_plan.blocks
        if not block.is_fixed
    }

    for segment in task_segments:
        block = blocks_by_item.get(segment.segment_id)
        if block is None:
            continue

        if segment.deadline_day is not None and block.day > segment.deadline_day:
            return False

    return True


def minimum_completion_constraint(
    task_segments: List[TaskSegment],
    scheduled_segment_ids: Set[str],
    min_ratio: float = 0.5
) -> bool:
    """
    Ensures that at least a minimum portion of a task is completed.
    """

    total = len(task_segments)
    completed = len([
        s for s in task_segments
        if s.segment_id in scheduled_segment_ids
    ])

    if total == 0:
        return True

    return (completed / total) >= min_ratio

def weekly_sleep_hard_constraint(week_plans, min_sleep_hours=6):
    """
    Enforces at least one continuous sleep window per 24h period.
    """

    # Collect all blocks with absolute time
    blocks = []
    for day_plan in week_plans:
        for block in day_plan.blocks:
            if block.is_fixed:
                continue

            absolute_start = day_plan.day * 1440 + block.start_min
            absolute_end = day_plan.day * 1440 + block.end_min
            blocks.append((absolute_start, absolute_end))

    blocks.sort()

    # Check each 24h window
    for day in range(len(week_plans)):
        window_start = day * 1440
        window_end = window_start + 1440

        current = window_start
        for start, end in blocks:
            if end <= window_start or start >= window_end:
                continue

            if start - current >= min_sleep_hours * 60:
                break

            current = max(current, end)

        if window_end - current < min_sleep_hours * 60:
            return False

    return True

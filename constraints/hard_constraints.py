# constraints/hard_constraints.py

from typing import List, Set

from models.schedule import DayPlan, WeekPlan, ScheduleBlock
from models.task import TaskSegment


# -------------------------------------------------
# Day-level hard constraints
# -------------------------------------------------

def no_overlap_constraint(day_plan: DayPlan) -> bool:
    """
    Ensures that no two blocks overlap in time within the same day.
    """

    blocks = sorted(day_plan.blocks, key=lambda b: b.start_min)

    for i in range(len(blocks) - 1):
        current = blocks[i]
        next_block = blocks[i + 1]

        if current.end_min > next_block.start_min:
            return False

    return True


def respects_fixed_events_constraint(day_plan: DayPlan) -> bool:
    """
    Ensures that non-fixed blocks do not overlap fixed blocks.
    """

    fixed_blocks = [b for b in day_plan.blocks if b.is_fixed]
    task_blocks = [b for b in day_plan.blocks if not b.is_fixed]

    for task in task_blocks:
        for fixed in fixed_blocks:
            if not (
                task.end_min <= fixed.start_min
                or task.start_min >= fixed.end_min
            ):
                return False

    return True


def deadline_hard_constraint(
    task_segments: List[TaskSegment],
    week_plan: WeekPlan
) -> bool:
    """
    Ensures that no task segment is scheduled after its hard deadline day.
    """

    blocks_by_segment = {}

    for day in week_plan.days:
        for block in day.blocks:
            if not block.is_fixed:
                blocks_by_segment[block.item_id] = block

    for segment in task_segments:
        block = blocks_by_segment.get(segment.segment_id)
        if block is None:
            continue

        if (
            segment.deadline_day is not None
            and block.day > segment.deadline_day
        ):
            return False

    return True


def minimum_completion_constraint(
    task_segments: List[TaskSegment],
    scheduled_segment_ids: Set[str],
    min_ratio: float = 0.5
) -> bool:
    """
    Ensures that at least a minimum portion of task segments are scheduled.
    """

    total = len(task_segments)
    if total == 0:
        return True

    completed = len(
        [s for s in task_segments if s.segment_id in scheduled_segment_ids]
    )

    return (completed / total) >= min_ratio


# -------------------------------------------------
# Week-level hard constraints
# -------------------------------------------------

def weekly_sleep_hard_constraint(week_plan: WeekPlan) -> bool:
    """
    Enforces that every day contains a fixed sleep block.
    Sleep is modeled as a hard fixed ScheduleBlock.
    """

    for day in week_plan.days:
        has_sleep = any(
            block.is_fixed and block.name.lower() == "sleep"
            for block in day.blocks
        )
        if not has_sleep:
            return False

    return True

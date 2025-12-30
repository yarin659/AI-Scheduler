# utils/locking.py

from typing import Optional
from models.schedule import WeekPlan, ScheduleBlock


class LockingError(Exception):
    """Raised when a locking operation is invalid."""
    pass


def lock_block(
    week_plan: WeekPlan,
    *,
    day: int,
    start_min: int,
    task_id: Optional[str] = None
) -> ScheduleBlock:
    """
    Locks a specific block in the weekly schedule.

    Parameters:
    - day: day index (0-6)
    - start_min: block start time (minutes)
    - task_id: optional, used for extra validation

    Returns:
    - The locked ScheduleBlock
    """

    day_plan = week_plan.get_day(day)

    for block in day_plan.blocks:
        if block.start_min != start_min:
            continue

        if task_id is not None and block.item_id != task_id:
            continue

        if block.is_fixed:
            raise LockingError("Cannot lock a fixed block.")

        block.is_locked = True
        return block

    raise LockingError("Block not found to lock.")


def unlock_block(
    week_plan: WeekPlan,
    *,
    day: int,
    start_min: int,
    task_id: Optional[str] = None
) -> ScheduleBlock:
    """
    Unlocks a previously locked block.
    """

    day_plan = week_plan.get_day(day)

    for block in day_plan.blocks:
        if block.start_min != start_min:
            continue

        if task_id is not None and block.item_id != task_id:
            continue

        if not block.is_locked:
            raise LockingError("Block is not locked.")

        block.is_locked = False
        return block

    raise LockingError("Block not found to unlock.")

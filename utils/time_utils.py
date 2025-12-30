# utilities/time_utils.py

from typing import List, Tuple
from models.schedule import DayPlan

DAY_START = 0
DAY_END = 24 * 60


def find_free_time_slots(day_plan: DayPlan) -> List[Tuple[int, int]]:
    """
    Identifies free time intervals between scheduled blocks.
    Assumes all hard constraints (including sleep) are already
    injected as fixed ScheduleBlocks into the DayPlan.
    """

    free_slots: List[Tuple[int, int]] = []
    current_time = DAY_START

    blocks = sorted(day_plan.blocks, key=lambda b: b.start_min)

    for block in blocks:
        if current_time < block.start_min:
            free_slots.append((current_time, block.start_min))

        current_time = max(current_time, block.end_min)

    if current_time < DAY_END:
        free_slots.append((current_time, DAY_END))

    return free_slots

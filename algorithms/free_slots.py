# algorithms/free_slots.py

from typing import List, Tuple
from models.schedule import DayPlan


def get_free_slots(
    day_plan: DayPlan,
    day_start: int = 0,
    day_end: int = 24 * 60
) -> List[Tuple[int, int]]:
    """
    Returns free time slots for a single-day plan.
    """

    blocks = sorted(day_plan.blocks, key=lambda b: b.start_min)

    free_slots = []
    cursor = day_start

    for block in blocks:
        if block.start_min > cursor:
            free_slots.append((cursor, block.start_min))
        cursor = max(cursor, block.end_min)

    if cursor < day_end:
        free_slots.append((cursor, day_end))

    return free_slots


def fit_start_times(
    free_slots: List[Tuple[int, int]],
    duration: int,
    step: int = 15
) -> List[int]:
    """
    Produces candidate start times that fit inside free slots.
    """

    starts = []

    for start, end in free_slots:
        t = start
        while t + duration <= end:
            starts.append(t)
            t += step

    return starts


from typing import List, Tuple
from models.schedule import DayPlan

DAY_START = 0
DAY_END = 24 * 60

SLEEP_START = 22 * 60   # 22:00
SLEEP_END = 7 * 60     # 07:00


def find_free_time_slots(day_plan: DayPlan) -> List[Tuple[int, int]]:
    """
    Identifies free time intervals between fixed scheduled blocks.
    The function scans the day timeline and returns gaps where tasks can be placed.
    """

    free_slots = []
    current_time = DAY_START

    for block in sorted(day_plan.blocks, key=lambda b: b.start_min):
        if current_time < block.start_min:
            free_slots.append((current_time, block.start_min))

        current_time = max(current_time, block.end_min)

    if current_time < DAY_END:
        free_slots.append((current_time, DAY_END))

    return free_slots


def filter_sleep_time_slots(
    free_slots: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    Removes or trims free time slots that overlap with sleep hours.
    Only time intervals outside the sleep window are returned.
    """

    valid_slots = []

    for start, end in free_slots:
        # Slot fully during allowed hours
        if end <= SLEEP_START and start >= SLEEP_END:
            valid_slots.append((start, end))
            continue

        # Slot overlaps sleep start (evening)
        if start < SLEEP_START < end:
            valid_slots.append((start, SLEEP_START))

        # Slot overlaps sleep end (morning)
        if start < SLEEP_END < end:
            valid_slots.append((SLEEP_END, end))

    return valid_slots

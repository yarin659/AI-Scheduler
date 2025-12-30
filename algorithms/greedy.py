# algorithms/greedy.py

from typing import List, Tuple
from models.task import TaskSegment
from models.schedule import DayPlan, ScheduleBlock


def greedy_schedule(
    day_plan: DayPlan,
    segments: List[TaskSegment],
    free_slots: List[Tuple[int, int]]
) -> DayPlan:
    """
    Builds a schedule for a single day using a greedy strategy.
    This function is WEEKLY-COMPATIBLE:
    - It schedules only segments assigned to this day
    - Day selection happens outside this function
    """

    # Create a copy of the day plan
    new_plan = DayPlan(day_plan.day_index)
    new_plan.blocks = list(day_plan.blocks)

    remaining_slots = list(free_slots)

    # Sort segments by priority (higher first)
    segments_sorted = sorted(
        segments,
        key=lambda s: s.priority,
        reverse=True
    )

    for segment in segments_sorted:
        for i, (slot_start, slot_end) in enumerate(remaining_slots):
            slot_duration = slot_end - slot_start

            if slot_duration >= segment.duration_min:
                block = ScheduleBlock(
                    item_id=segment.segment_id,   # IMPORTANT: segment-level ID
                    name=segment.task_id,
                    day=new_plan.day_index,
                    start_min=slot_start,
                    end_min=slot_start + segment.duration_min,
                    category=segment.category,
                    is_fixed=False
                )

                new_plan.add_block(block)

                # Update remaining free slot
                remaining_slots[i] = (
                    slot_start + segment.duration_min,
                    slot_end
                )

                break

    # Keep blocks ordered in time
    new_plan.blocks.sort(key=lambda b: b.start_min)

    return new_plan

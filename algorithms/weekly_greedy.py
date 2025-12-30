# algorithms/weekly_greedy.py

from typing import List

from models.schedule import WeekPlan, ScheduleBlock
from models.task import TaskSegment
from algorithms.free_slots import get_free_slots


def weekly_greedy_schedule(
    week_plan: WeekPlan,
    segments: List[TaskSegment]
) -> WeekPlan:
    """
    Greedy scheduler on a WEEK level with load balancing.
    Each TaskSegment is placed once somewhere in the week.
    Days are chosen by current load (least blocks first).
    """

    # Sort segments by priority (higher first)
    segments_sorted = sorted(
        segments,
        key=lambda s: s.priority,
        reverse=True
    )

    for segment in segments_sorted:
        placed = False

        # Sort days by current load (fewest non-fixed blocks first)
        days_by_load = sorted(
            week_plan.days,
            key=lambda d: len([b for b in d.blocks if not b.is_fixed])
        )

        for day in days_by_load:
            free_slots = get_free_slots(day)

            for start, end in free_slots:
                if end - start >= segment.duration_min:
                    block = ScheduleBlock(
                        item_id=segment.segment_id,
                        name=segment.task_id,
                        day=day.day_index,
                        start_min=start,
                        end_min=start + segment.duration_min,
                        category=segment.category,
                        is_fixed=False
                    )

                    day.add_block(block)
                    day.blocks.sort(key=lambda b: b.start_min)
                    placed = True
                    break

            if placed:
                break

        # If segment could not be placed anywhere, skip it
        # (local search may handle it later)

    return week_plan

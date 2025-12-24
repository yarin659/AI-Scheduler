from typing import List, Tuple
from models.task import TaskSegment
from models.schedule import DayPlan, ScheduleBlock


def greedy_schedule(
    day_plan: DayPlan,
    tasks: List[TaskSegment],
    free_slots: List[Tuple[int, int]]
) -> DayPlan:
    """
    Builds a schedule using a greedy strategy over task segments.
    Each segment is treated as an independent schedulable unit.
    """

    # Create a shallow copy of the day plan
    new_plan = DayPlan(
        day=day_plan.day,
        blocks=list(day_plan.blocks)
    )

    remaining_slots = list(free_slots)

    # Sort segments by priority (higher first)
    tasks_sorted = sorted(tasks, key=lambda t: t.priority, reverse=True)

    for task in tasks_sorted:
        for i, (slot_start, slot_end) in enumerate(remaining_slots):
            slot_duration = slot_end - slot_start

            if slot_duration >= task.duration_min:
                block = ScheduleBlock(
                    item_id=task.task_id,
                    name=task.task_id,
                    day=new_plan.day,
                    start_min=slot_start,
                    end_min=slot_start + task.duration_min,
                    category=task.category,
                    is_fixed=False
                )

                new_plan.blocks.append(block)

                # Update the remaining free slot
                remaining_slots[i] = (
                    slot_start + task.duration_min,
                    slot_end
                )

                break

    # Keep blocks ordered in time
    new_plan.blocks.sort(key=lambda b: b.start_min)

    return new_plan

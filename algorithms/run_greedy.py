from typing import List, Tuple
from uuid import uuid4

from models.task import Task, TaskSegment
from models.schedule import DayPlan
from algorithms.greedy import greedy_schedule
from algorithms.free_slots import get_free_slots


def run_greedy_from_tasks(
    tasks: List[Task],
    day: int = 0
) -> DayPlan:
    """
    Adapter function:
    Converts high-level Tasks into TaskSegments,
    builds an initial DayPlan,
    computes free slots,
    and runs the greedy scheduler.
    """

    # 1. Build initial empty day plan
    day_plan = DayPlan(
        day=day,
        blocks=[]
    )

    # 2. Convert Tasks -> TaskSegments (1 segment per task for now)
    segments: List[TaskSegment] = []

    for task in tasks:
        segment = TaskSegment(
            task_id=task.id,
            segment_id=str(uuid4()),
            duration_min=task.duration_min,
            category=task.category,
            priority=task.priority,
            deadline_day=None
        )
        segments.append(segment)

    # 3. Compute free slots from the empty plan
    free_slots: List[Tuple[int, int]] = get_free_slots(day_plan)

    # 4. Run greedy scheduler
    scheduled_plan = greedy_schedule(
        day_plan=day_plan,
        tasks=segments,
        free_slots=free_slots
    )

    return scheduled_plan

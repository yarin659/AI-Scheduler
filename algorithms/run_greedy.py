# algorithms/run_greedy.py

from typing import List
from uuid import uuid4

from models.task import Task, TaskSegment
from models.schedule import WeekPlan
from algorithms.weekly_greedy import weekly_greedy_schedule


def run_weekly_greedy_from_tasks(
    tasks: List[Task]
) -> WeekPlan:
    """
    Adapter function (WEEKLY):
    - Converts high-level Tasks into TaskSegments
    - Builds an empty WeekPlan
    - Runs the weekly greedy scheduler
    """

    # 1. Convert Tasks -> TaskSegments
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

    # 2. Build empty week
    week = WeekPlan()

    # 3. Run weekly greedy scheduler
    scheduled_week = weekly_greedy_schedule(
        week_plan=week,
        segments=segments
    )

    return scheduled_week

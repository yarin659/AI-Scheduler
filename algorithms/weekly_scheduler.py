# algorithms/weekly_scheduler.py

from typing import List, Dict

from models.schedule import DayPlan
from models.task import Task, TaskSegment
from models.user_preferences import UserPreferences

from algorithms.greedy import greedy_schedule
from algorithms.free_slots import get_free_slots
from algorithms.local_search import simulated_annealing

from constraints.hard_constraints import weekly_sleep_hard_constraint


def split_tasks_to_segments(tasks: List[Task]) -> List[TaskSegment]:
    """
    Splits tasks into schedulable task segments.
    Currently: one segment per task.
    """

    segments: List[TaskSegment] = []

    for task in tasks:
        segments.append(
            TaskSegment(
                task_id=task.id,
                segment_id=f"{task.id}_seg",
                duration_min=task.duration_min,
                category=task.category,
                priority=task.priority,
                deadline_day=None
            )
        )

    return segments


def build_weekly_schedule(
    fixed_events_by_day: Dict[int, list],
    tasks: List[Task],
    user_preferences: UserPreferences,
    max_retries: int = 10
):
    """
    Builds a weekly schedule using:
    - greedy scheduling per day
    - simulated annealing per day
    - global weekly hard constraints (sleep)
    """

    segments = split_tasks_to_segments(tasks)

    for _ in range(max_retries):
        week: List[DayPlan] = []

        for day in range(7):
            day_plan = DayPlan(day=day, blocks=[])

            # Insert fixed events
            for event in fixed_events_by_day.get(day, []):
                day_plan.blocks.append(event.to_block(day))

            # Compute free slots
            free_slots = get_free_slots(day_plan, day)

            # Greedy scheduling
            greedy_plan = greedy_schedule(
                day_plan=day_plan,
                tasks=segments,
                free_slots=free_slots
            )

            # Local search refinement (SA)
            optimized_plan = simulated_annealing(
                initial_plan=greedy_plan,
                segments=segments,
                user_preferences=user_preferences,
                max_iters=1500,
                start_temp=100.0,
                cooling_rate=0.997
            )

            week.append(optimized_plan)

        # -------- Weekly hard constraints --------
        if weekly_sleep_hard_constraint(week):
            return week

    # If we failed to find a valid weekly schedule
    return week

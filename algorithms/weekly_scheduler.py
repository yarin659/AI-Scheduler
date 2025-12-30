# algorithms/weekly_scheduler.py

from typing import List, Dict

from models.schedule import WeekPlan
from models.task import Task, TaskSegment
from models.user_preferences import UserPreferences
from utils.sleep import add_sleep_block

from algorithms.weekly_greedy import weekly_greedy_schedule
from algorithms.local_search import simulated_annealing
from constraints.hard_constraints import weekly_sleep_hard_constraint


def split_tasks_to_segments(
    tasks: List[Task],
    user_preferences: UserPreferences
) -> List[TaskSegment]:
    """
    Splits tasks into weekly task segments according to desired frequency.
    """

    segments: List[TaskSegment] = []

    for task in tasks:
        freq = user_preferences.desired_frequencies.get(task.id, 1)

        for i in range(freq):
            segments.append(
                TaskSegment(
                    task_id=task.id,
                    segment_id=f"{task.id}_seg_{i+1}",
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
) -> WeekPlan:
    """
    Builds a WEEKLY schedule using:
    - weekly greedy initialization
    - weekly simulated annealing
    - global weekly hard constraints
    """

    segments = split_tasks_to_segments(tasks, user_preferences)

    for _ in range(max_retries):
        # 1. Build empty week
        week = WeekPlan()


        # Inject sleep block into every day
        for day in week.days:
            add_sleep_block(day)

        # 2. Insert fixed events
        for day_index, events in fixed_events_by_day.items():
            day = week.get_day(day_index)
            for event in events:
                day.add_block(event.to_block(day_index))

        # 3. Weekly greedy scheduling
        week = weekly_greedy_schedule(
            week_plan=week,
            segments=segments
        )

        # 4. Weekly local search optimization
        week = simulated_annealing(
            initial_week=week,
            segments=segments,
            user_preferences=user_preferences,
            max_iters=1500,
            start_temp=100.0,
            cooling_rate=0.997
        )

        # 5. Weekly hard constraints
        if weekly_sleep_hard_constraint(week):
            return week

    return week

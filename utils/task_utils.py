
from typing import List
from models.task import Task, TaskSegment


def split_task(task: Task, chunk_size: int) -> List[TaskSegment]:
    """
    Splits a task into smaller segments of fixed size.
    Each segment can be scheduled independently.
    """

    segments = []
    remaining = task.duration_min
    index = 1

    while remaining > 0:
        segment_duration = min(chunk_size, remaining)

        segments.append(
            TaskSegment(
                task_id=task.id,
                segment_id=f"{task.id}_part{index}",
                duration_min=segment_duration,
                category=task.category,
                priority=task.priority
            )
        )

        remaining -= segment_duration
        index += 1

    return segments

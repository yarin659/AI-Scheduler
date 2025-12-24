
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Task:
    id: str
    name: str
    duration_min: int
    category: str
    priority: int
    flexible: bool = True
    earliest_start: Optional[int] = None
    latest_end: Optional[int] = None


@dataclass(frozen=True)
class TaskSegment:
    """
    Represents a split portion of a task.
    Multiple segments may belong to the same original task.
    """
    task_id: str
    segment_id: str
    duration_min: int
    category: str
    priority: int
    deadline_day: Optional[int] = None


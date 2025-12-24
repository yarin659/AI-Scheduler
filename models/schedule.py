# models/schedule.py

from dataclasses import dataclass
from typing import List


@dataclass
class ScheduleBlock:
    item_id: str
    name: str
    day: int
    start_min: int
    end_min: int
    category: str
    is_fixed: bool = False


@dataclass
class DayPlan:
    day: int
    blocks: List[ScheduleBlock]


@dataclass
class WeekPlan:
    days: List[DayPlan]

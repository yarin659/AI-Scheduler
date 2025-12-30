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
    is_locked: bool = False


class DayPlan:
    def __init__(self, day_index: int):
        self.day_index = day_index
        self.blocks: List[ScheduleBlock] = []

    def add_block(self, block: ScheduleBlock):
        self.blocks.append(block)

    def get_blocks(self) -> List[ScheduleBlock]:
        return self.blocks


class WeekPlan:
    def __init__(self):
        self.days: List[DayPlan] = [DayPlan(i) for i in range(7)]

    def get_day(self, day_index: int) -> DayPlan:
        return self.days[day_index]

    def __iter__(self):
        return iter(self.days)

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

    @property
    def duration_min(self) -> int:
        return self.end_min - self.start_min


class DayPlan:
    def __init__(self, day_index: int):
        self.day_index = day_index
        self.blocks: List[ScheduleBlock] = []

    def add_block(self, block: ScheduleBlock):
        self.blocks.append(block)
        self.blocks.sort(key=lambda b: b.start_min)

    def get_blocks(self) -> List[ScheduleBlock]:
        return self.blocks

    def total_load_minutes(self, include_fixed: bool = False) -> int:
        return sum(
            block.duration_min
            for block in self.blocks
            if include_fixed or not block.is_fixed
        )

    def movable_blocks(self) -> List[ScheduleBlock]:
        return [
            block for block in self.blocks
            if not block.is_fixed and not block.is_locked
        ]

    def overlaps_with_existing(self, new_block: ScheduleBlock) -> bool:
        for block in self.blocks:
            if not (
                new_block.end_min <= block.start_min
                or new_block.start_min >= block.end_min
            ):
                return True
        return False


class WeekPlan:
    def __init__(self):
        self.days: List[DayPlan] = [DayPlan(i) for i in range(7)]

    def get_day(self, day_index: int) -> DayPlan:
        return self.days[day_index]

    def __iter__(self):
        return iter(self.days)
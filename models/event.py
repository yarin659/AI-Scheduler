# models/event.py

from dataclasses import dataclass
from models.schedule import ScheduleBlock


@dataclass
class FixedEvent:
    id: str
    name: str
    start_min: int
    end_min: int
    category: str

    def to_block(self, day: int) -> ScheduleBlock:
        """
        Converts a fixed calendar event into a schedulable block.
        """

        return ScheduleBlock(
            item_id=self.id,
            name=self.name,
            day=day,
            start_min=self.start_min,
            end_min=self.end_min,
            category=self.category,
            is_fixed=True
        )

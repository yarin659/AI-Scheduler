# utils/sleep.py

from models.schedule import ScheduleBlock, DayPlan


def add_sleep_block(
    day_plan: DayPlan,
    sleep_start: int = 0,
    sleep_end: int = 7 * 60
):
    """
    Injects a fixed sleep block into a DayPlan.
    """

    sleep_block = ScheduleBlock(
        item_id="sleep",
        name="Sleep",
        day=day_plan.day_index,
        start_min=sleep_start,
        end_min=sleep_end,
        category="sleep",
        is_fixed=True
    )

    day_plan.add_block(sleep_block)

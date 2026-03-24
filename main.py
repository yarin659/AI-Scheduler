# main.py

from data.example_input import fixed_events, tasks
from models.user_preferences import UserPreferences
from algorithms.weekly_scheduler import build_weekly_schedule
from utils.locking import lock_block
from ml.decision_logging.decision_logger import DecisionLogger



DAY_NAMES = [
    "Day 0 (Sunday)",
    "Day 1 (Monday)",
    "Day 2 (Tuesday)",
    "Day 3 (Wednesday)",
    "Day 4 (Thursday)",
    "Day 5 (Friday)",
    "Day 6 (Saturday)"
]


def print_week(week):
    print("\n=== WEEKLY SCHEDULE ===\n")

    for day_plan in week.days:
        print(f"\n--- {DAY_NAMES[day_plan.day_index]} ---")

        if not day_plan.blocks:
            print("No scheduled blocks")
            continue

        for block in sorted(day_plan.blocks, key=lambda b: b.start_min):
            sh, sm = divmod(block.start_min, 60)
            eh, em = divmod(block.end_min, 60)

            lock_mark = " lock" if getattr(block, "is_locked", False) else ""

            print(
                f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d} | "
                f"{block.name} [{block.category}]{lock_mark}"
            )






def main():
    fixed_events_by_day = {
        0: fixed_events,
        2: fixed_events,
        4: fixed_events
    }

    user_preferences = UserPreferences(
        preferred_time_ranges=[(18, 22)],
        avoided_time_ranges=[(7, 9)],
        desired_frequencies={
            "project": 3,
            "study_material": 5,
            "assignments": 2
        },
        autonomy_level="aggressive",   # gentle / balanced / aggressive
        balanced_move_threshold=30
    )

    # -------------------------------------------------
    # Build weekly schedule
    # -------------------------------------------------
    week = build_weekly_schedule(
        fixed_events_by_day=fixed_events_by_day,
        tasks=tasks,
        user_preferences=user_preferences
    )

    # -------------------------------------------------
    # LOCKING TEST — robust & generic
    # Lock the FIRST non-fixed work block we find
    # -------------------------------------------------
    block_to_lock = None

    for day in week.days:
        for block in day.blocks:
            if (
                not block.is_fixed
                and block.category == "work"
            ):
                block_to_lock = block
                break
        if block_to_lock:
            break

    if block_to_lock:
        lock_block(
            week,
            day=block_to_lock.day,
            start_min=block_to_lock.start_min,
            task_id=block_to_lock.item_id
        )
        print(
            f"\n Locked block: {block_to_lock.name} "
            f"(Day {block_to_lock.day}, {block_to_lock.start_min} min)"
        )
    else:
        print("\n No suitable work block found to lock.")

    # -------------------------------------------------
    # Print result
    # -------------------------------------------------
    print_week(week)

    logger = DecisionLogger()

    # Simulated feedback: user liked study tasks
    for day in week.days:
        for block in day.blocks:
            if block.category == "study":
                logger.update_label(
                    user_id="debug_user",
                    task_id=block.name,
                    label=1
                )
            elif not block.is_fixed:
                logger.update_label(
                    user_id="debug_user",
                    task_id=block.name,
                    label=0
                )


if __name__ == "__main__":
    main()

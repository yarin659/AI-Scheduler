# main.py

from data.example_input import fixed_events, tasks
from models.user_preferences import UserPreferences
from algorithms.weekly_scheduler import build_weekly_schedule
from utils.locking import lock_block


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
        autonomy_level="aggressive",   # "gentle" / "balanced" / "aggressive"
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
    # LOCKING TEST (correct, deterministic)
    # -------------------------------------------------
    project_block = None

    for day in week.days:
        for block in day.blocks:
            if block.name == "Core Project Work" and not block.is_fixed:
                project_block = block
                break
        if project_block:
            break

    if project_block:
        lock_block(
            week,
            day=project_block.day,
            start_min=project_block.start_min,
            task_id=project_block.item_id
        )
        print(" Locked Core Project Work block for testing.")
    else:
        print(" No Core Project Work block found — skipping locking test.")

    # -------------------------------------------------
    # Print result
    # -------------------------------------------------
    print_week(week)


if __name__ == "__main__":
    main()

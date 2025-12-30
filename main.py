# main.py

from data.example_input import fixed_events, tasks
from models.user_preferences import UserPreferences
from algorithms.weekly_scheduler import build_weekly_schedule


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

            print(
                f"{sh:02d}:{sm:02d}-{eh:02d}:{em:02d} | "
                f"{block.name} [{block.category}]"
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
        autonomy_level = "balanced",  # "gentle" / "balanced" / "aggressive"
        balanced_move_threshold = 30
    )

    week = build_weekly_schedule(
        fixed_events_by_day=fixed_events_by_day,
        tasks=tasks,
        user_preferences=user_preferences
    )

    print_week(week)


if __name__ == "__main__":
    main()

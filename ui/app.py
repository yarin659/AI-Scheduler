# ui/app.py

import streamlit as st
from uuid import uuid4

from models.task import Task
from models.user_preferences import UserPreferences
from algorithms.weekly_scheduler import build_weekly_schedule


def minutes_to_time_str(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


PRIORITY_MAP = {
    "Low": 3,
    "Medium": 6,
    "High": 9
}

DAY_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
]


st.set_page_config(page_title="Smart Study Scheduler", layout="centered")

st.title("🧠 Smart Study Scheduler (Weekly)")

# -------------------------------------------------
# USER PREFERENCES
# -------------------------------------------------

st.header("User Preferences")

preferred_hours = st.multiselect(
    "Preferred start hours",
    options=list(range(6, 23)),
    default=[18, 19, 20]
)

avoided_hours = st.multiselect(
    "Avoided start hours",
    options=list(range(6, 23)),
    default=[7, 8]
)

st.subheader("AI Autonomy Level")

autonomy_level = st.selectbox(
    "How much control should the AI have?",
    options=["gentle", "balanced", "aggressive"],
    format_func=lambda x: {
        "gentle": "Gentle – Improve hours only",
        "balanced": "Balanced – Reorganize if clearly better",
        "aggressive": "Aggressive – Full weekly control"
    }[x]
)

balanced_threshold = 30
if autonomy_level == "balanced":
    balanced_threshold = st.slider(
        "Required improvement for moving tasks between days",
        min_value=10,
        max_value=100,
        value=30,
        step=5
    )

# -------------------------------------------------
# TASK INPUT
# -------------------------------------------------

st.header("Tasks")

tasks_input = st.text_area(
    "Enter tasks (format: name,duration,priority)",
    placeholder="Project,60,High\nStudy Material,45,Medium\nAssignments,120,High"
)

# -------------------------------------------------
# GENERATE SCHEDULE
# -------------------------------------------------

if st.button("Generate Weekly Schedule"):
    tasks = []

    for line in tasks_input.splitlines():
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            st.error(f"Invalid task format: {line}")
            continue

        name, duration_str, priority_str = parts

        if priority_str not in PRIORITY_MAP:
            st.error(f"Invalid priority: {priority_str}")
            continue

        try:
            duration_min = int(duration_str)
        except ValueError:
            st.error(f"Invalid duration: {duration_str}")
            continue

        tasks.append(
            Task(
                id=name.lower().replace(" ", "_"),
                name=name,
                duration_min=duration_min,
                category="general",
                priority=PRIORITY_MAP[priority_str],
                flexible=True
            )
        )

    if not tasks:
        st.warning("No valid tasks entered.")
        st.stop()

    user_preferences = UserPreferences(
        preferred_time_ranges=[(h, h + 1) for h in preferred_hours],
        avoided_time_ranges=[(h, h + 1) for h in avoided_hours],
        desired_frequencies={},  # frequencies come from backend example / future UI
        autonomy_level=autonomy_level,
        balanced_move_threshold=balanced_threshold
    )

    fixed_events_by_day = {}

    week = build_weekly_schedule(
        fixed_events_by_day=fixed_events_by_day,
        tasks=tasks,
        user_preferences=user_preferences
    )

    st.header("Generated Weekly Schedule")

    for day in week.days:
        st.subheader(DAY_NAMES[day.day_index])

        visible_blocks = [b for b in day.blocks if not b.is_fixed]

        if not visible_blocks:
            st.write("— Free day —")
            continue

        for block in sorted(visible_blocks, key=lambda b: b.start_min):
            start_time = minutes_to_time_str(block.start_min)
            end_time = minutes_to_time_str(block.end_min)

            st.write(
                f"{start_time} – {end_time} | {block.name}"
            )

import streamlit as st
from uuid import uuid4

# Import your existing logic
from algorithms.greedy import greedy_schedule
from models.task import Task
from models.user_preferences import UserPreferences
from algorithms.run_greedy import run_greedy_from_tasks

def minutes_to_time_str(minutes_from_day_start: int, day_start_min: int) -> str:
    total_minutes = day_start_min + minutes_from_day_start
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


PRIORITY_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}


st.set_page_config(page_title="Smart Study Scheduler", layout="centered")

st.title("🧠 Smart Study Scheduler")

st.header("User Preferences")

sleep_hours = st.slider("Sleep hours", min_value=4, max_value=10, value=7)
focus_level = st.selectbox("Focus preference", ["Morning", "Evening", "Flexible"])

st.header("Tasks")

tasks_input = st.text_area(
    "Enter tasks (format: name,duration,priority)",
    placeholder="Math,90,High\nWorkout,60,Medium"
)

if st.button("Generate Schedule"):
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
            st.error(f"Invalid priority (use Low/Medium/High): {priority_str}")
            continue

        try:
            duration_min = int(duration_str)
        except ValueError:
            st.error(f"Invalid duration: {duration_str}")
            continue

        task = Task(
            id=str(uuid4()),
            name=name,
            duration_min=duration_min,
            category="general",  # כרגע קבוע – בהמשך נעשה selectbox
            priority=PRIORITY_MAP[priority_str],
            flexible=True
        )
        task_name_by_id = {t.id: t.name for t in tasks}

        tasks.append(task)

    # Run greedy scheduler via adapter
    task_name_by_id = {t.id: t.name for t in tasks}

    schedule = run_greedy_from_tasks(tasks)

    st.header("Generated Schedule")

    for block in schedule.blocks:
        display_name = task_name_by_id.get(block.name, block.name)
        DAY_START_MIN = 8 * 60 + 30  # 08:30

        start_time = minutes_to_time_str(block.start_min, DAY_START_MIN)
        end_time = minutes_to_time_str(block.end_min, DAY_START_MIN)

        st.write(
            f"{start_time} – {end_time} | {display_name}"
        )





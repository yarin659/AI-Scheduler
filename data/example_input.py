from models.event import FixedEvent
from models.task import Task


def hhmm_to_min(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


# ---------------------------
# Fixed weekly events
# ---------------------------

fixed_events = [
    FixedEvent(
        id="study_block",
        name="Studies",
        start_min=hhmm_to_min("09:00"),
        end_min=hhmm_to_min("14:00"),
        category="study"
    ),
    FixedEvent(
        id="project_time",
        name="Project Time",
        start_min=hhmm_to_min("10:30"),
        end_min=hhmm_to_min("12:30"),
        category="personal"
    ),
    FixedEvent(
        id="partner_time",
        name="Partner Time",
        start_min=hhmm_to_min("16:30"),
        end_min=hhmm_to_min("18:30"),
        category="personal"
    ),
    FixedEvent(
        id="workout",
        name="Workout",
        start_min=hhmm_to_min("20:30"),
        end_min=hhmm_to_min("21:00"),
        category="sport"
    )
]


# ---------------------------
# Stress-test tasks (price exists)
# ---------------------------

tasks = [
    Task(
        id="project_core",
        name="Core Project Work",
        duration_min=180,
        category="work",
        priority=10,
        latest_end=hhmm_to_min("21:00")
    ),
    Task(
        id="cpp_project",
        name="CPP Project",
        duration_min=180,
        category="study",
        priority=10,
        latest_end=hhmm_to_min("21:00")
    ),
    Task(
        id="assignments_math",
        name="Math Assignments",
        duration_min=120,
        category="study",
        priority=9,
        latest_end=hhmm_to_min("21:00")
    ),
    Task(
        id="assignments_physics",
        name="Physics Assignments",
        duration_min=120,
        category="study",
        priority=9,
        latest_end=hhmm_to_min("21:00")
    ),
    Task(
        id="reading",
        name="Reading & Review",
        duration_min=90,
        category="study",
        priority=6,
        latest_end=hhmm_to_min("21:00")
    ),
    Task(
        id="optional_learning",
        name="Optional Learning",
        duration_min=90,
        category="study",
        priority=4,
        latest_end=hhmm_to_min("21:00")
    ),
]

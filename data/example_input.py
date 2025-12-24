from models.event import FixedEvent
from models.task import Task

def hhmm_to_min(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m

fixed_events = [
    FixedEvent(
        id="study_block",
        name="Studies",
        start_min=hhmm_to_min("09:00"),
        end_min=hhmm_to_min("14:00"),
        category="study"
    ),
    FixedEvent(
        id="partner_time",
        name="Partner Time",
        start_min=hhmm_to_min("16:30"),
        end_min=hhmm_to_min("18:30"),
        category="personal"
    ),
FixedEvent(
        id="project_time",
        name="project_Time",
        start_min=hhmm_to_min("10:30"),
        end_min=hhmm_to_min("12:30"),
        category="personal"
    ),
    FixedEvent(
        id="evening_workout",
        name="Workout",
        start_min=hhmm_to_min("20:30"),
        end_min=hhmm_to_min("21:00"),
        category="sport"
    )
]

tasks = [
    Task(
        id="project",
        name="Work on Project",
        duration_min=60,
        category="work",
        priority=9
    ),
    Task(
        id="study_material",
        name="Study Material",
        duration_min=45,
        category="study",
        priority=7,
        latest_end=hhmm_to_min("21:00")
    ),
    Task(
        id="assignments",
        name="Assignments",
        duration_min=120,
        category="study",
        priority=9,
        latest_end=hhmm_to_min("21:00")
    )
]

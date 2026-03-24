from dataclasses import dataclass
from typing import List


@dataclass
class UserProfile:
    chronotype: str              # "morning" / "evening" / "neutral"
    duration_sensitivity: str    # "low" / "medium" / "high"
    day_flexibility: str         # "low" / "high"
    preferred_categories: List[str]

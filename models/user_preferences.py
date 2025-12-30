# models/user_preferences.py

from dataclasses import dataclass
from typing import List, Tuple, Dict, Literal


AutonomyLevel = Literal["gentle", "balanced", "aggressive"]


@dataclass
class UserPreferences:
    """
    Represents soft preferences that describe how a specific user
    prefers their schedule to be organized.
    """

    def __init__(
        self,
        preferred_time_ranges: List[Tuple[int, int]],
        avoided_time_ranges: List[Tuple[int, int]],
        desired_frequencies: Dict[str, int],
        autonomy_level: AutonomyLevel = "gentle",
        balanced_move_threshold: int = 30
    ):
        self.preferred_time_ranges = preferred_time_ranges
        self.avoided_time_ranges = avoided_time_ranges
        self.desired_frequencies = desired_frequencies

        # Control how much the optimizer is allowed to change the week structure
        self.autonomy_level = autonomy_level

        # For "balanced": allow moving between days only if improvement >= threshold
        self.balanced_move_threshold = balanced_move_threshold

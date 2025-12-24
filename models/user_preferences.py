# models/user_preferences.py

from typing import List, Tuple, Dict


class UserPreferences:
    """
    Represents soft preferences that describe how a specific user
    prefers their schedule to be organized.
    """

    def __init__(
        self,
        preferred_time_ranges: List[Tuple[int, int]],
        avoided_time_ranges: List[Tuple[int, int]],
        desired_frequencies: Dict[str, int]
    ):
        self.preferred_time_ranges = preferred_time_ranges
        self.avoided_time_ranges = avoided_time_ranges
        self.desired_frequencies = desired_frequencies

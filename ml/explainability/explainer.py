from typing import List

class SimpleExplainer:
    @staticmethod
    def explain(features: dict) -> List[str]:
        reasons = []

        if features["task_category"] == "study":
            reasons.append("You usually prefer study tasks")

        if features["hour"] <= 9:
            reasons.append("You tend to prefer morning hours")

        if features["hour"] >= 21:
            reasons.append("This task was scheduled late based on past preferences")

        if features["task_duration"] >= 150:
            reasons.append("You handle longer sessions well for this task type")

        return reasons


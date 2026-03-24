from ml.models.user_profile import UserProfile


class ProfileBias:
    @staticmethod
    def get_bias_bonus(features: dict, profile: UserProfile) -> float:
        """
        Returns a small additive bonus/penalty based on learned user profile.
        This is not a full score. It is only a personalization adjustment.
        """
        bonus = 0.0

        # Chronotype bias
        hour = features.get("hour", 12)
        if profile.chronotype == "morning" and hour >= 18:
            bonus -= 0.10
        if profile.chronotype == "evening" and hour <= 9:
            bonus -= 0.10

        # Duration sensitivity
        duration = features.get("task_duration", 0)
        if profile.duration_sensitivity == "high" and duration > 120:
            bonus -= 0.10

        # Preferred categories
        category = features.get("task_category")
        if category and category in profile.preferred_categories:
            bonus += 0.05

        return bonus
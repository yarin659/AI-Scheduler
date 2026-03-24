from ml.models.user_profile import UserProfile


class UserProfileBuilder:
    @staticmethod
    def from_feature_weights(weights: dict) -> UserProfile:
        # Chronotype
        hour_w = weights.get("hour", 0)
        if hour_w < -0.3:
            chronotype = "morning"
        elif hour_w > 0.3:
            chronotype = "evening"
        else:
            chronotype = "neutral"

        # Duration sensitivity
        duration_w = abs(weights.get("task_duration", 0))
        if duration_w > 0.3:
            duration_sensitivity = "high"
        elif duration_w > 0.1:
            duration_sensitivity = "medium"
        else:
            duration_sensitivity = "low"

        # Day flexibility
        day_w = abs(weights.get("day_of_week", 0))
        day_flexibility = "high" if day_w < 0.1 else "low"

        # Preferred categories
        preferred_categories = []
        for k, v in weights.items():
            if k.startswith("task_category_") and v > 0:
                preferred_categories.append(k.replace("task_category_", ""))

        return UserProfile(
            chronotype=chronotype,
            duration_sensitivity=duration_sensitivity,
            day_flexibility=day_flexibility,
            preferred_categories=preferred_categories
        )

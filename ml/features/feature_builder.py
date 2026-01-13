# Builds ML features from scheduling context

class FeatureBuilder:
    @staticmethod
    def build(segment, block):
        return {
            "hour": block.start_min // 60,
            "day_of_week": block.day,
            "task_category": segment.category,
            "task_duration": segment.duration_min
        }

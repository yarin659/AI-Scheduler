from typing import List, Dict, Any

from models.schedule import WeekPlan, ScheduleBlock
from models.task import TaskSegment
from models.user_preferences import UserPreferences
from algorithms.free_slots import get_free_slots

from ml.decision_logging.decision_logger import DecisionLogger
from ml.features.feature_builder import FeatureBuilder
from ml.interfaces.ml_scorer import MLScorer
from ml.explainability.comparative_explainer import ComparativeExplainer
from ml.user_modeling.profile_bias import ProfileBias
from ml.user_modeling.weights_extractor import extract_feature_weights
from ml.user_modeling.profile_builder import UserProfileBuilder


def _is_in_time_range(hour: int, time_ranges: List[tuple]) -> bool:
    for start_hour, end_hour in time_ranges:
        if start_hour <= hour < end_hour:
            return True
    return False


def _round_time_bonus(start_min: int) -> float:
    if start_min % 60 == 0:
        return 2.0
    if start_min % 30 == 0:
        return 1.0
    return 0.0


def _heuristic_candidate_score(
    segment: TaskSegment,
    block: ScheduleBlock,
    day,
    user_preferences: UserPreferences
) -> float:
    score = 0.0

    hour = block.start_min // 60
    day_load_minutes = day.total_load_minutes()

    # Strong priority signal for greedy placement
    score += float(segment.priority) * 10.0

    # Preferred / avoided user time ranges
    if _is_in_time_range(hour, user_preferences.preferred_time_ranges):
        score += 8.0

    if _is_in_time_range(hour, user_preferences.avoided_time_ranges):
        score -= 10.0

    # Prefer lighter days
    score -= day_load_minutes / 60.0

    # Prefer cleaner starting times
    score += _round_time_bonus(block.start_min)

    # Small preference for earlier hours
    score -= hour * 0.15

    return score


def weekly_greedy_schedule(
    week_plan: WeekPlan,
    segments: List[TaskSegment],
    user_preferences: UserPreferences
) -> WeekPlan:
    """
    Greedy scheduler on a WEEK level.
    Core decision logic is heuristic-based (AI-first).
    ML is used only as a supporting bonus layer.
    """
    weights = extract_feature_weights()
    user_profile = UserProfileBuilder.from_feature_weights(weights)

    ml_scorer = MLScorer()
    decision_logger = DecisionLogger()

    segments_sorted = sorted(
        segments,
        key=lambda s: s.priority,
        reverse=True
    )

    for segment in segments_sorted:
        placed = False

        days_by_load = sorted(
            week_plan.days,
            key=lambda d: len([b for b in d.blocks if not b.is_fixed])
        )

        for day in days_by_load:
            free_slots = get_free_slots(day)
            candidates: List[Dict[str, Any]] = []

            for start, end in free_slots:
                if end - start < segment.duration_min:
                    continue

                block = ScheduleBlock(
                    item_id=segment.segment_id,
                    name=segment.task_id,
                    day=day.day_index,
                    start_min=start,
                    end_min=start + segment.duration_min,
                    category=segment.category,
                    is_fixed=False
                )

                heuristic_score = _heuristic_candidate_score(
                    segment=segment,
                    block=block,
                    day=day,
                    user_preferences=user_preferences
                )

                features = FeatureBuilder.build(segment, block)

                ml_raw_score = ml_scorer.score(features)
                ml_bonus = (ml_raw_score - 0.5) * 2.0 if ml_scorer.available() else 0.0

                profile_bonus = ProfileBias.get_bias_bonus(
                    features=features,
                    profile=user_profile
                )

                final_score = heuristic_score + ml_bonus + profile_bonus

                decision_logger.log_decision(
                    user_id="debug_user",
                    task_id=segment.task_id,
                    features=features
                )

                candidates.append({
                    "block": block,
                    "features": features,
                    "heuristic_score": heuristic_score,
                    "ml_raw_score": ml_raw_score,
                    "ml_bonus": ml_bonus,
                    "profile_bonus": profile_bonus,
                    "final_score": final_score
                })

            if not candidates:
                continue

            candidates.sort(key=lambda c: c["final_score"], reverse=True)

            best = candidates[0]
            alternatives = candidates[1:3]

            explanation = ComparativeExplainer.explain(best, alternatives)

            day.add_block(best["block"])
            placed = True

            print(
                f"Scheduled {segment.task_id} on day {best['block'].day} "
                f"at {best['features']['hour']}:00\n"
                f"Heuristic score: {best['heuristic_score']:.2f}\n"
                f"ML bonus: {best['ml_bonus']:.2f}\n"
                f"Profile bonus: {best['profile_bonus']:.2f}\n"
                f"Final score: {best['final_score']:.2f}\n"
                f"Reasons:\n- " + "\n- ".join(explanation)
            )

            break

        if not placed:
            print(f"Could not place segment {segment.segment_id} ({segment.task_id})")

    return week_plan
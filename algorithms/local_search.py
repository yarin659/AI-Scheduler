# algorithms/local_search.py

import random
import math
from typing import List, Optional, Tuple, Callable

from models.schedule import WeekPlan, ScheduleBlock
from models.user_preferences import UserPreferences
from scoring.score_function import score_schedule
from algorithms.free_slots import get_free_slots, fit_start_times


NeighborOp = Callable[[WeekPlan], Optional[WeekPlan]]


def simulated_annealing(
    initial_week: WeekPlan,
    segments: List,
    user_preferences: UserPreferences,
    max_iters: int = 2000,
    start_temp: float = 100.0,
    cooling_rate: float = 0.995,
    seed: Optional[int] = None
) -> WeekPlan:
    """
    Performs Simulated Annealing optimization on a WEEKLY schedule.
    The autonomy_level controls which neighbor operators are allowed.

    - gentle: only move within the same day (time shifts)
    - balanced: may move between days ONLY if improvement >= balanced_move_threshold
    - aggressive: may move freely between days
    """

    if seed is not None:
        random.seed(seed)

    current = clone_week(initial_week)
    current_score = score_schedule(current, segments, user_preferences)

    best = clone_week(current)
    best_score = current_score

    temperature = start_temp

    for _ in range(max_iters):
        neighbor, op_kind = generate_neighbor(current, user_preferences)
        if neighbor is None:
            temperature *= cooling_rate
            continue

        neighbor_score = score_schedule(neighbor, segments, user_preferences)
        delta = neighbor_score - current_score

        # Balanced policy: allow "between-days" moves only if improvement is significant
        if (
            user_preferences.autonomy_level == "balanced"
            and op_kind == "between_days"
            and delta < user_preferences.balanced_move_threshold
        ):
            temperature *= cooling_rate
            continue

        # SA acceptance
        if delta > 0 or random.random() < math.exp(delta / max(temperature, 1e-9)):
            current = neighbor
            current_score = neighbor_score

            if current_score > best_score:
                best = clone_week(current)
                best_score = current_score

        temperature *= cooling_rate
        if temperature < 1e-3:
            break

    return best


# ------------------------------------------------------------------
# Neighbor selection (Autonomy)
# ------------------------------------------------------------------

def generate_neighbor(
    week: WeekPlan,
    user_preferences: UserPreferences
) -> Tuple[Optional[WeekPlan], str]:
    """
    Returns (neighbor_week, op_kind) where op_kind is:
    - "within_day"
    - "between_days"
    """

    level = user_preferences.autonomy_level

    if level == "gentle":
        ops: List[Tuple[NeighborOp, str]] = [
            (_op_move_within_day, "within_day"),
        ]
    elif level == "balanced":
        ops = [
            (_op_move_within_day, "within_day"),
            (_op_move_between_days_adjacent_only, "between_days"),
        ]
    else:  # aggressive
        ops = [
            (_op_move_within_day, "within_day"),
            (_op_move_between_days_any, "between_days"),
        ]

    op, kind = random.choice(ops)
    return op(week), kind


# ------------------------------------------------------------------
# Operators
# ------------------------------------------------------------------

def _op_move_within_day(week: WeekPlan) -> Optional[WeekPlan]:
    """
    Moves a non-fixed block to a different time on the SAME day.
    """

    week = clone_week(week)
    day = random.choice(week.days)

    movable = [b for b in day.blocks if not b.is_fixed]
    if not movable:
        return None

    block = random.choice(movable)
    duration = block.end_min - block.start_min

    day.blocks.remove(block)

    free_slots = get_free_slots(day)
    candidates = fit_start_times(free_slots, duration)
    if not candidates:
        day.blocks.append(block)
        return None

    new_start = random.choice(candidates)
    block.start_min = new_start
    block.end_min = new_start + duration

    day.blocks.append(block)
    day.blocks.sort(key=lambda b: b.start_min)

    return week


def _op_move_between_days_adjacent_only(week: WeekPlan) -> Optional[WeekPlan]:
    """
    Moves a non-fixed block from one day to an ADJACENT day only (±1).
    """

    week = clone_week(week)

    source_day = random.choice(week.days)
    movable = [b for b in source_day.blocks if not b.is_fixed]
    if not movable:
        return None

    block = random.choice(movable)
    duration = block.end_min - block.start_min

    src_idx = source_day.day_index
    candidates_days = []
    if src_idx - 1 >= 0:
        candidates_days.append(week.get_day(src_idx - 1))
    if src_idx + 1 <= 6:
        candidates_days.append(week.get_day(src_idx + 1))

    if not candidates_days:
        return None

    target_day = random.choice(candidates_days)

    source_day.blocks.remove(block)

    free_slots = get_free_slots(target_day)
    candidates = fit_start_times(free_slots, duration)
    if not candidates:
        source_day.blocks.append(block)
        return None

    new_start = random.choice(candidates)
    block.day = target_day.day_index
    block.start_min = new_start
    block.end_min = new_start + duration

    target_day.blocks.append(block)
    target_day.blocks.sort(key=lambda b: b.start_min)

    return week


def _op_move_between_days_any(week: WeekPlan) -> Optional[WeekPlan]:
    """
    Moves a non-fixed block from one day to ANY other day.
    """

    week = clone_week(week)

    source_day = random.choice(week.days)
    movable = [b for b in source_day.blocks if not b.is_fixed]
    if not movable:
        return None

    block = random.choice(movable)
    duration = block.end_min - block.start_min

    target_day = random.choice(week.days)
    if target_day.day_index == source_day.day_index:
        return None

    source_day.blocks.remove(block)

    free_slots = get_free_slots(target_day)
    candidates = fit_start_times(free_slots, duration)
    if not candidates:
        source_day.blocks.append(block)
        return None

    new_start = random.choice(candidates)
    block.day = target_day.day_index
    block.start_min = new_start
    block.end_min = new_start + duration

    target_day.blocks.append(block)
    target_day.blocks.sort(key=lambda b: b.start_min)

    return week


# ------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------

def clone_week(week: WeekPlan) -> WeekPlan:
    """
    Deep copy of WeekPlan (manual, controlled).
    """

    new_week = WeekPlan()

    for day in week.days:
        new_day = new_week.get_day(day.day_index)
        for block in day.blocks:
            new_day.blocks.append(
                ScheduleBlock(
                    item_id=block.item_id,
                    name=block.name,
                    day=block.day,
                    start_min=block.start_min,
                    end_min=block.end_min,
                    category=block.category,
                    is_fixed=block.is_fixed
                )
            )

    return new_week

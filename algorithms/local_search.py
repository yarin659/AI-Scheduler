# algorithms/local_search.py

import random
import math
from dataclasses import replace
from typing import List, Optional, Tuple

from models.schedule import DayPlan
from models.user_preferences import UserPreferences
from scoring.score_function import score_schedule
from algorithms.free_slots import get_free_slots, fit_start_times


def simulated_annealing(
    initial_plan: DayPlan,
    segments: List,
    user_preferences: UserPreferences,
    max_iters: int = 2000,
    start_temp: float = 100.0,
    cooling_rate: float = 0.995,
    neighbor_samples: int = 1,
    seed: Optional[int] = None
) -> DayPlan:
    """
    Performs Simulated Annealing optimization on a schedule.
    """

    if seed is not None:
        random.seed(seed)

    current = initial_plan
    current_score = score_schedule(current, segments, user_preferences)

    best = current
    best_score = current_score

    temperature = start_temp

    for _ in range(max_iters):
        neighbor = generate_neighbor(current)
        if neighbor is None:
            temperature *= cooling_rate
            continue

        neighbor_score = score_schedule(neighbor, segments, user_preferences)
        delta = neighbor_score - current_score

        # Always accept better solutions
        if delta > 0:
            current = neighbor
            current_score = neighbor_score

        # Probabilistically accept worse solutions
        else:
            acceptance_prob = math.exp(delta / temperature)
            if random.random() < acceptance_prob:
                current = neighbor
                current_score = neighbor_score

        # Track best solution seen
        if current_score > best_score:
            best = current
            best_score = current_score

        temperature *= cooling_rate
        if temperature < 1e-3:
            break

    return best


def generate_neighbor(plan: DayPlan) -> Optional[DayPlan]:
    """
    Generates a neighboring schedule using one of several operators.
    """

    operators = [
        _op_move_to_free_slot,
        _op_swap,
        _op_reinsert_to_free_slot
    ]
    return random.choice(operators)(plan)


def _op_move_to_free_slot(plan: DayPlan) -> Optional[DayPlan]:
    """
    Moves one non-fixed block into a valid free slot on the same day.
    """

    movable = [i for i, b in enumerate(plan.blocks) if not b.is_fixed]
    if not movable:
        return None

    idx = random.choice(movable)
    block = plan.blocks[idx]
    duration = block.end_min - block.start_min

    temp_blocks = list(plan.blocks)
    temp_blocks.pop(idx)
    temp_plan = replace(plan, blocks=temp_blocks)

    free_slots = get_free_slots(temp_plan, block.day)
    candidates = fit_start_times(free_slots, duration)
    if not candidates:
        return None

    new_start = random.choice(candidates)
    new_block = replace(block, start_min=new_start, end_min=new_start + duration)

    new_blocks = list(plan.blocks)
    new_blocks[idx] = new_block

    return replace(plan, blocks=new_blocks)


def _op_swap(plan: DayPlan) -> Optional[DayPlan]:
    """
    Swaps two non-fixed blocks on the same day.
    """

    movable = [i for i, b in enumerate(plan.blocks) if not b.is_fixed]
    if len(movable) < 2:
        return None

    i1, i2 = random.sample(movable, 2)
    b1, b2 = plan.blocks[i1], plan.blocks[i2]

    if b1.day != b2.day:
        return None

    new_blocks = list(plan.blocks)
    new_blocks[i1] = replace(b1, start_min=b2.start_min, end_min=b2.end_min)
    new_blocks[i2] = replace(b2, start_min=b1.start_min, end_min=b1.end_min)

    return replace(plan, blocks=new_blocks)


def _op_reinsert_to_free_slot(plan: DayPlan) -> Optional[DayPlan]:
    """
    Reinserts a block into a random valid free slot.
    """

    movable = [i for i, b in enumerate(plan.blocks) if not b.is_fixed]
    if not movable:
        return None

    idx = random.choice(movable)
    block = plan.blocks[idx]
    duration = block.end_min - block.start_min

    temp_blocks = list(plan.blocks)
    temp_blocks.pop(idx)
    temp_plan = replace(plan, blocks=temp_blocks)

    free_slots = get_free_slots(temp_plan, block.day)
    candidates = fit_start_times(free_slots, duration)
    if not candidates:
        return None

    new_start = random.choice(candidates)
    new_block = replace(block, start_min=new_start, end_min=new_start + duration)

    new_blocks = list(plan.blocks)
    new_blocks[idx] = new_block

    return replace(plan, blocks=new_blocks)

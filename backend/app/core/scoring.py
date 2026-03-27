from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PenaltyWeights:
    unbalanced_shifts: int = 10
    consecutive_nights: int = 5
    fairness_deviation: int = 3
    norm_overrun: int = 20
    low_hours: int = 3
    uncovered_shift: int = 200
    missing_first_shift: int = 120
    pre_start_assignment: int = 120
    rest_gap: int = 90
    five_day_streak: int = 90
    post_streak_rest: int = 90


DEFAULT_WEIGHTS = PenaltyWeights()

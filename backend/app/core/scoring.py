# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PenaltyWeights:
    unbalanced_shifts: int = 10
    consecutive_nights: int = 5
    fairness_deviation: int = 3
    norm_overrun: int = 20
    low_hours: int = 3

    # Dominating best-effort objective weights.
    uncovered_shift: int = 10000000000
    missing_first_shift: int = 100000000
    hard_violation: int = 1000000


@dataclass(frozen=True)
class ScoreConfig:
    base_score: int = 100
    uncovered_shift_penalty: int = 40
    missing_first_shift_penalty: int = 15
    other_hard_penalty: int = 8
    unbalanced_penalty: int = 6
    consecutive_nights_penalty: int = 4
    fairness_penalty: int = 3
    norm_overrun_penalty: int = 10
    soft_penalty_cap: int = 30
    hard_penalty_cap: int = 80


DEFAULT_WEIGHTS = PenaltyWeights()
DEFAULT_SCORE_CONFIG = ScoreConfig()

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Sequence

from app.models.schemas import ViolationEntry


def build_explanation(
    used_best_effort: bool,
    strict_found: bool,
    used_cover_employee: bool,
    input_warnings: Sequence[ViolationEntry],
    hard_violations: Sequence[ViolationEntry],
    soft_violations: Sequence[ViolationEntry],
) -> str:
    uncovered_count = sum(1 for violation in hard_violations if violation.code == "uncovered_shift")
    missing_first_count = sum(1 for violation in hard_violations if violation.code == "missing_first_shift")
    norm_overrun_count = sum(1 for violation in soft_violations if violation.code == "norm_overrun")

    strict_failed = not strict_found

    return (
        f"strict_mode_failed={'yes' if strict_failed else 'no'}; "
        f"best_effort_used={'yes' if used_best_effort else 'no'}; "
        f"cover_employee_used={'yes' if used_cover_employee else 'no'}; "
        f"input_warnings_count={len(input_warnings)}; "
        f"uncovered_shifts_count={uncovered_count}; "
        f"missing_first_shifts_count={missing_first_count}; "
        f"norm_overruns_count={norm_overrun_count}; "
        f"hard_violations_count={len(hard_violations)}; "
        f"soft_violations_count={len(soft_violations)}"
    )

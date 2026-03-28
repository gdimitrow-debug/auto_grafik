# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Sequence

from app.models.schemas import EmployeeStats, ViolationEntry


def build_explanation(
    used_best_effort: bool,
    strict_found: bool,
    used_cover_employee: bool,
    input_warnings: Sequence[ViolationEntry],
    hard_violations: Sequence[ViolationEntry],
    soft_violations: Sequence[ViolationEntry],
    employee_stats: Sequence[EmployeeStats],
    norm_hours: int,
) -> str:
    uncovered_count = sum(1 for violation in hard_violations if violation.code == "uncovered_shift")
    missing_first_count = sum(1 for violation in hard_violations if violation.code == "missing_first_shift")
    cover_shift_count = sum(stat.total_shifts for stat in employee_stats if stat.is_cover)
    norm_limited_employee_count = sum(1 for stat in employee_stats if stat.total_hours >= norm_hours)
    all_employees_at_norm_limit = bool(employee_stats) and all(stat.total_hours >= norm_hours for stat in employee_stats)
    uncovered_due_to_norm_limits = uncovered_count > 0 and all_employees_at_norm_limit

    strict_failed = not strict_found

    return (
        f"strict_mode_failed={'yes' if strict_failed else 'no'}; "
        f"best_effort_used={'yes' if used_best_effort else 'no'}; "
        f"cover_employee_used={'yes' if used_cover_employee else 'no'}; "
        f"cover_shifts_count={cover_shift_count}; "
        f"input_warnings_count={len(input_warnings)}; "
        f"uncovered_shifts_count={uncovered_count}; "
        f"missing_first_shifts_count={missing_first_count}; "
        f"norm_limited_employees_count={norm_limited_employee_count}; "
        f"uncovered_due_to_all_norm_limits={'yes' if uncovered_due_to_norm_limits else 'no'}; "
        f"hard_violations_count={len(hard_violations)}; "
        f"soft_violations_count={len(soft_violations)}"
    )

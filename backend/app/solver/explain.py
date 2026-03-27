from __future__ import annotations

from typing import Sequence

from app.models.schemas import ViolationEntry


def build_explanation(
    used_best_effort: bool,
    strict_found: bool,
    used_cover_employee: bool,
    hard_violations: Sequence[ViolationEntry],
    soft_violations: Sequence[ViolationEntry],
) -> str:
    parts = []
    if strict_found:
        parts.append("Strict mode found a fully valid schedule with no hard-constraint violations.")
    elif used_best_effort:
        parts.append("Strict mode did not find a solution, so the solver switched to best effort mode.")

    if used_cover_employee:
        parts.append("A cover employee was used in the returned schedule.")

    if hard_violations:
        parts.append(f"The final result contains {len(hard_violations)} hard-constraint violation(s), listed in the response.")
    else:
        parts.append("The final result contains no hard-constraint violations.")

    if soft_violations:
        parts.append(f"The final result contains {len(soft_violations)} soft-constraint warning(s).")
    else:
        parts.append("No soft-constraint penalties were triggered.")

    return " ".join(parts)

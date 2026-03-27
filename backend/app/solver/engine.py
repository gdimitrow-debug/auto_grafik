# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ortools.sat.python import cp_model

from app.core.config import DEFAULT_RANDOM_SEED, DEFAULT_SOLVER_TIME_LIMIT_SECONDS
from app.core.scoring import DEFAULT_SCORE_CONFIG, DEFAULT_WEIGHTS, PenaltyWeights, ScoreConfig
from app.models.schemas import EmployeeStats, ScheduleAssignment, ScheduleRequest, ScheduleResponse, ViolationEntry
from app.solver.explain import build_explanation
from app.solver.validators import detect_input_conflicts, employee_start_day, get_days_in_month, validate_request_window


@dataclass(frozen=True)
class ShiftMeta:
    shift_id: str
    shift_type: str
    start_hour_absolute: int
    end_hour_absolute: int
    duration_hours: int


@dataclass(frozen=True)
class SolveOptions:
    allow_cover: bool
    allow_norm_overrun: bool
    allow_hard_relaxation: bool


def _parse_hour(text: str) -> int:
    return datetime.strptime(text, "%H:%M").hour


def _build_shift_meta(payload: ScheduleRequest) -> Dict[str, ShiftMeta]:
    meta: Dict[str, ShiftMeta] = {}
    for shift in payload.shifts:
        start_hour = _parse_hour(shift.start_time)
        end_hour = _parse_hour(shift.end_time)
        end_absolute = end_hour if end_hour > start_hour else end_hour + 24
        meta[shift.id] = ShiftMeta(
            shift_id=shift.id,
            shift_type=shift.type,
            start_hour_absolute=start_hour,
            end_hour_absolute=end_absolute,
            duration_hours=shift.duration_hours,
        )
    return meta


def _rest_gap_hours(meta: Dict[str, ShiftMeta], previous_shift_id: str, next_shift_id: str) -> int:
    previous = meta[previous_shift_id]
    next_shift = meta[next_shift_id]
    return (24 + next_shift.start_hour_absolute) - previous.end_hour_absolute


def _post_streak_gap_hours(meta: Dict[str, ShiftMeta], last_shift_id: str, future_shift_id: str) -> int:
    last_shift = meta[last_shift_id]
    future = meta[future_shift_id]
    return (48 + future.start_hour_absolute) - last_shift.end_hour_absolute


def _stable_employee_order(payload: ScheduleRequest, allow_cover: bool) -> List[int]:
    ordered = sorted(
        [
            (index, employee)
            for index, employee in enumerate(payload.employees)
            if allow_cover or not employee.is_cover
        ],
        key=lambda item: (item[1].is_cover, employee_start_day(item[1]), item[1].name, item[1].id),
    )
    return [index for index, _ in ordered]


def solve_schedule(
    payload: ScheduleRequest,
    weights: PenaltyWeights = DEFAULT_WEIGHTS,
    score_config: ScoreConfig = DEFAULT_SCORE_CONFIG,
) -> ScheduleResponse:
    input_warnings = detect_input_conflicts(payload)
    is_window_valid, message = validate_request_window(payload)
    if not is_window_valid:
        violation = ViolationEntry(code="invalid_start_day", message=message, severity="hard")
        explanation = build_explanation(False, False, False, input_warnings, [violation], [])
        return ScheduleResponse(
            schedule=[],
            input_warnings=input_warnings,
            hard_violations=[violation],
            soft_violations=[],
            employee_stats=[],
            score=_compute_score(score_config, [violation], []),
            is_valid=False,
            used_cover_employee=False,
            used_best_effort=False,
            explanation=explanation,
        )

    strict_result = _run_solver(payload, SolveOptions(False, False, False), weights, score_config)
    if strict_result is not None:
        strict_result.input_warnings = input_warnings
        strict_result.score = _compute_score(score_config, strict_result.hard_violations, strict_result.soft_violations)
        strict_result.explanation = build_explanation(
            strict_result.used_best_effort,
            not strict_result.used_best_effort,
            strict_result.used_cover_employee,
            strict_result.input_warnings,
            strict_result.hard_violations,
            strict_result.soft_violations,
        )
        return strict_result

    best_effort_valid = _run_solver(payload, SolveOptions(True, True, False), weights, score_config)
    if best_effort_valid is not None:
        best_effort_valid.input_warnings = input_warnings
        best_effort_valid.score = _compute_score(score_config, best_effort_valid.hard_violations, best_effort_valid.soft_violations)
        best_effort_valid.explanation = build_explanation(
            best_effort_valid.used_best_effort,
            False,
            best_effort_valid.used_cover_employee,
            best_effort_valid.input_warnings,
            best_effort_valid.hard_violations,
            best_effort_valid.soft_violations,
        )
        return best_effort_valid

    fallback = _run_solver(payload, SolveOptions(True, True, True), weights, score_config)
    if fallback is not None:
        fallback.input_warnings = input_warnings
        fallback.score = _compute_score(score_config, fallback.hard_violations, fallback.soft_violations)
        fallback.explanation = build_explanation(
            fallback.used_best_effort,
            False,
            fallback.used_cover_employee,
            fallback.input_warnings,
            fallback.hard_violations,
            fallback.soft_violations,
        )
        return fallback

    violation = ViolationEntry(
        code="solver_failed",
        message="No solution could be produced, even in best effort fallback mode.",
        severity="hard",
    )
    explanation = build_explanation(True, False, False, input_warnings, [violation], [])
    return ScheduleResponse(
        schedule=[],
        input_warnings=input_warnings,
        hard_violations=[violation],
        soft_violations=[],
        employee_stats=[],
        score=_compute_score(score_config, [violation], []),
        is_valid=False,
        used_cover_employee=False,
        used_best_effort=True,
        explanation=explanation,
    )


def _run_solver(
    payload: ScheduleRequest,
    options: SolveOptions,
    weights: PenaltyWeights,
    score_config: ScoreConfig,
) -> Optional[ScheduleResponse]:
    model = cp_model.CpModel()
    days = get_days_in_month(payload.year, payload.month)
    day_range = range(1, days + 1)
    shift_ids = [shift.id for shift in payload.shifts]
    shift_meta = _build_shift_meta(payload)
    employee_indexes = _stable_employee_order(payload, options.allow_cover)
    if not employee_indexes:
        return None

    assign: Dict[Tuple[int, int, str], cp_model.IntVar] = {}
    work: Dict[Tuple[int, int], cp_model.IntVar] = {}

    uncovered_terms: List[cp_model.IntVar] = []
    missing_first_terms: List[cp_model.IntVar] = []
    other_hard_violation_terms: List[cp_model.IntVar] = []
    soft_penalties: List[cp_model.LinearExpr] = []
    violation_vars: List[Tuple[cp_model.IntVar, str, Dict[str, object], str]] = []

    for employee_idx in employee_indexes:
        employee = payload.employees[employee_idx]
        start_day = employee_start_day(employee)
        for day in day_range:
            work[(employee_idx, day)] = model.NewBoolVar(f"work_e{employee_idx}_d{day}")
            vars_for_day = []
            for shift_id in shift_ids:
                var = model.NewBoolVar(f"x_e{employee_idx}_d{day}_{shift_id}")
                assign[(employee_idx, day, shift_id)] = var
                vars_for_day.append(var)

            model.Add(sum(vars_for_day) == work[(employee_idx, day)])
            model.Add(sum(vars_for_day) <= 1)

            if day < start_day:
                for shift_id in shift_ids:
                    model.Add(assign[(employee_idx, day, shift_id)] == 0)

    for day in day_range:
        for shift_id in shift_ids:
            vars_for_slot = [assign[(employee_idx, day, shift_id)] for employee_idx in employee_indexes]
            if options.allow_hard_relaxation:
                shortage = model.NewBoolVar(f"shortage_d{day}_{shift_id}")
                model.Add(sum(vars_for_slot) + shortage == 1)
                uncovered_terms.append(shortage)
                violation_vars.append((shortage, "uncovered_shift", {"day": day, "shift_id": shift_id}, "hard"))
            else:
                model.Add(sum(vars_for_slot) == 1)

    for employee_idx in employee_indexes:
        employee = payload.employees[employee_idx]
        start_day = employee_start_day(employee)
        if employee.first_shift is not None:
            required_first = assign[(employee_idx, start_day, employee.first_shift)]
            if options.allow_hard_relaxation:
                missing_first = model.NewBoolVar(f"missing_first_e{employee_idx}")
                model.Add(required_first + missing_first == 1)
                missing_first_terms.append(missing_first)
                violation_vars.append(
                    (
                        missing_first,
                        "missing_first_shift",
                        {"employee_id": employee.id, "day": start_day, "shift_id": employee.first_shift},
                        "hard",
                    )
                )
            else:
                model.Add(required_first == 1)

        total_hours = sum(
            assign[(employee_idx, day, shift_id)] * shift_meta[shift_id].duration_hours
            for day in day_range
            for shift_id in shift_ids
        )
        max_norm = int(payload.norm_hours * 1.08) if options.allow_norm_overrun else payload.norm_hours
        model.Add(total_hours <= max_norm)

        if not employee.is_cover:
            preferred_floor = int(payload.norm_hours * 0.85)
            low_hours = model.NewIntVar(0, payload.norm_hours, f"low_hours_e{employee_idx}")
            model.Add(low_hours >= preferred_floor - total_hours)
            model.Add(low_hours >= 0)
            soft_penalties.append(low_hours * weights.low_hours)

        if options.allow_norm_overrun:
            overrun = model.NewIntVar(0, max_norm, f"overrun_e{employee_idx}")
            model.Add(overrun >= total_hours - payload.norm_hours)
            model.Add(overrun >= 0)
            soft_penalties.append(overrun * weights.norm_overrun)

        for day in range(1, days):
            for previous_shift in shift_ids:
                for next_shift in shift_ids:
                    if _rest_gap_hours(shift_meta, previous_shift, next_shift) < 12:
                        lhs = assign[(employee_idx, day, previous_shift)] + assign[(employee_idx, day + 1, next_shift)]
                        if options.allow_hard_relaxation:
                            violation = model.NewBoolVar(f"rest_e{employee_idx}_d{day}_{previous_shift}_{next_shift}")
                            model.Add(lhs <= 1 + violation)
                            other_hard_violation_terms.append(violation)
                            violation_vars.append(
                                (
                                    violation,
                                    "minimum_rest_violation",
                                    {"employee_id": employee.id, "day": day + 1, "shift_id": next_shift},
                                    "hard",
                                )
                            )
                        else:
                            model.Add(lhs <= 1)

        for day in range(5, days + 1):
            lhs = sum(work[(employee_idx, ref_day)] for ref_day in range(day - 4, day + 1))
            if options.allow_hard_relaxation:
                violation = model.NewBoolVar(f"five_day_e{employee_idx}_d{day}")
                model.Add(lhs <= 4 + violation)
                other_hard_violation_terms.append(violation)
                violation_vars.append(
                    (
                        violation,
                        "max_consecutive_days_violation",
                        {"employee_id": employee.id, "day": day},
                        "hard",
                    )
                )
            else:
                model.Add(lhs <= 4)

        for day in range(4, days):
            lhs_next_day = sum(work[(employee_idx, ref_day)] for ref_day in range(day - 3, day + 1)) + work[(employee_idx, day + 1)]
            if options.allow_hard_relaxation:
                violation = model.NewBoolVar(f"rest_after_streak_e{employee_idx}_d{day}")
                model.Add(lhs_next_day <= 4 + violation)
                other_hard_violation_terms.append(violation)
                violation_vars.append(
                    (
                        violation,
                        "post_streak_rest_violation",
                        {"employee_id": employee.id, "day": day + 1},
                        "hard",
                    )
                )
            else:
                model.Add(lhs_next_day <= 4)

            if day + 2 <= days:
                for last_shift in shift_ids:
                    for future_shift in shift_ids:
                        if _post_streak_gap_hours(shift_meta, last_shift, future_shift) < 36:
                            lhs = (
                                sum(work[(employee_idx, ref_day)] for ref_day in range(day - 3, day))
                                + assign[(employee_idx, day, last_shift)]
                                + assign[(employee_idx, day + 2, future_shift)]
                            )
                            if options.allow_hard_relaxation:
                                violation = model.NewBoolVar(f"rest36_e{employee_idx}_d{day}_{last_shift}_{future_shift}")
                                model.Add(lhs <= 4 + violation)
                                other_hard_violation_terms.append(violation)
                                violation_vars.append(
                                    (
                                        violation,
                                        "missing_36h_rest_after_streak",
                                        {"employee_id": employee.id, "day": day + 2, "shift_id": future_shift},
                                        "hard",
                                    )
                                )
                            else:
                                model.Add(lhs <= 4)

        night_shift_ids = [shift_id for shift_id in shift_ids if shift_meta[shift_id].shift_type == "night"]
        for day in range(1, days):
            for night_shift in night_shift_ids:
                pair = model.NewBoolVar(f"night_pair_e{employee_idx}_d{day}_{night_shift}")
                model.Add(pair <= assign[(employee_idx, day, night_shift)])
                model.Add(pair <= assign[(employee_idx, day + 1, night_shift)])
                model.Add(pair >= assign[(employee_idx, day, night_shift)] + assign[(employee_idx, day + 1, night_shift)] - 1)
                soft_penalties.append(pair * weights.consecutive_nights)

    non_cover_indexes = [idx for idx in employee_indexes if not payload.employees[idx].is_cover]
    if non_cover_indexes:
        expected_total_shifts = days * len(shift_ids)
        avg_total_scaled = expected_total_shifts * 100 // len(non_cover_indexes)
        expected_per_shift_scaled = days * 100 // len(non_cover_indexes)
        tolerance_scaled = max(1, expected_per_shift_scaled // 4)

        for employee_idx in non_cover_indexes:
            total_shifts = sum(work[(employee_idx, day)] for day in day_range)
            total_scaled = model.NewIntVar(0, expected_total_shifts * 100, f"fair_total_scaled_e{employee_idx}")
            model.Add(total_scaled == total_shifts * 100)
            fairness_diff = model.NewIntVar(0, expected_total_shifts * 100, f"fair_diff_e{employee_idx}")
            model.AddAbsEquality(fairness_diff, total_scaled - avg_total_scaled)
            soft_penalties.append(fairness_diff * weights.fairness_deviation)

            for shift_id in shift_ids:
                shift_count = sum(assign[(employee_idx, day, shift_id)] for day in day_range)
                shift_scaled = model.NewIntVar(0, days * 100, f"shift_scaled_e{employee_idx}_{shift_id}")
                model.Add(shift_scaled == shift_count * 100)
                shift_diff = model.NewIntVar(0, days * 100, f"shift_diff_e{employee_idx}_{shift_id}")
                model.AddAbsEquality(shift_diff, shift_scaled - expected_per_shift_scaled)
                excess = model.NewIntVar(0, days * 100, f"shift_excess_e{employee_idx}_{shift_id}")
                model.Add(excess >= shift_diff - tolerance_scaled)
                model.Add(excess >= 0)
                soft_penalties.append(excess * weights.unbalanced_shifts)

    tie_break = []
    shift_order = {shift_id: index for index, shift_id in enumerate(shift_ids)}
    for employee_position, employee_idx in enumerate(employee_indexes):
        for day in day_range:
            for shift_id in shift_ids:
                tie_break.append(assign[(employee_idx, day, shift_id)] * ((employee_position + 1) * 1000 + day * 10 + shift_order[shift_id]))

    if options.allow_hard_relaxation:
        model.Minimize(
            sum(uncovered_terms) * weights.uncovered_shift
            + sum(missing_first_terms) * weights.missing_first_shift
            + sum(other_hard_violation_terms) * weights.hard_violation
            + sum(soft_penalties)
            + sum(tie_break)
        )
    else:
        model.Minimize(sum(soft_penalties) + sum(tie_break))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = DEFAULT_RANDOM_SEED
    solver.parameters.max_time_in_seconds = DEFAULT_SOLVER_TIME_LIMIT_SECONDS
    solver.parameters.log_search_progress = False

    status = solver.Solve(model)
    if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
        return None

    assignments_by_employee: Dict[int, Dict[int, str]] = {employee_idx: {} for employee_idx in employee_indexes}
    schedule: List[ScheduleAssignment] = []
    for employee_idx in employee_indexes:
        employee = payload.employees[employee_idx]
        for day in day_range:
            for shift_id in shift_ids:
                if solver.Value(assign[(employee_idx, day, shift_id)]) == 1:
                    assignments_by_employee[employee_idx][day] = shift_id
                    schedule.append(
                        ScheduleAssignment(
                            employee_id=employee.id,
                            employee_name=employee.name,
                            day=day,
                            shift_id=shift_id,
                        )
                    )

    hard_violations: List[ViolationEntry] = []
    if options.allow_hard_relaxation:
        for variable, code, meta, severity in violation_vars:
            if severity == "hard" and solver.Value(variable) == 1:
                hard_violations.append(
                    ViolationEntry(
                        code=code,
                        message=_hard_violation_message(code, meta),
                        employee_id=meta.get("employee_id"),
                        day=meta.get("day"),
                        shift_id=meta.get("shift_id"),
                        severity="hard",
                    )
                )

    employee_stats = _build_employee_stats(payload, employee_indexes, assignments_by_employee, shift_meta)
    soft_violations = _build_soft_violations(payload, employee_stats)
    if options.allow_norm_overrun:
        for stat in employee_stats:
            if stat.total_hours > payload.norm_hours:
                soft_violations.append(
                    ViolationEntry(
                        code="norm_overrun",
                        message=f"Employee {stat.employee_name} exceeds norm hours with {stat.total_hours}h.",
                        employee_id=stat.employee_id,
                        severity="soft",
                    )
                )

    used_cover_employee = any(stat.is_cover and stat.total_shifts > 0 for stat in employee_stats)
    used_best_effort = options.allow_cover or options.allow_norm_overrun or options.allow_hard_relaxation
    score = _compute_score(score_config, hard_violations, soft_violations)
    explanation = build_explanation(used_best_effort, not used_best_effort, used_cover_employee, [], hard_violations, soft_violations)

    return ScheduleResponse(
        schedule=sorted(schedule, key=lambda item: (item.day, item.shift_id, item.employee_name)),
        input_warnings=[],
        hard_violations=hard_violations,
        soft_violations=soft_violations,
        employee_stats=employee_stats,
        score=score,
        is_valid=len(hard_violations) == 0,
        used_cover_employee=used_cover_employee,
        used_best_effort=used_best_effort,
        explanation=explanation,
    )


def _compute_score(score_config: ScoreConfig, hard_violations: Sequence[ViolationEntry], soft_violations: Sequence[ViolationEntry]) -> int:
    hard_penalty = 0
    soft_penalty = 0

    for violation in hard_violations:
        if violation.code == "uncovered_shift":
            hard_penalty += score_config.uncovered_shift_penalty
        elif violation.code == "missing_first_shift":
            hard_penalty += score_config.missing_first_shift_penalty
        else:
            hard_penalty += score_config.other_hard_penalty

    for violation in soft_violations:
        if violation.code == "unbalanced_shift_distribution":
            soft_penalty += score_config.unbalanced_penalty
        elif violation.code == "consecutive_night_shift_pair":
            soft_penalty += score_config.consecutive_nights_penalty
        elif violation.code in {"fairness_deviation", "below_preferred_hours"}:
            soft_penalty += score_config.fairness_penalty
        elif violation.code == "norm_overrun":
            soft_penalty += score_config.norm_overrun_penalty

    hard_penalty = min(hard_penalty, score_config.hard_penalty_cap)
    soft_penalty = min(soft_penalty, score_config.soft_penalty_cap)
    return max(score_config.base_score - hard_penalty - soft_penalty, 0)


def _hard_violation_message(code: str, meta: Dict[str, object]) -> str:
    if code == "uncovered_shift":
        return f"Shift {meta['shift_id']} on day {meta['day']} could not be covered."
    if code == "missing_first_shift":
        return f"Employee {meta['employee_id']} could not receive required first shift {meta['shift_id']} on day {meta['day']}."
    if code == "minimum_rest_violation":
        return f"Employee {meta['employee_id']} violates the 12-hour minimum rest before day {meta['day']}."
    if code == "max_consecutive_days_violation":
        return f"Employee {meta['employee_id']} exceeds the 4-day consecutive work limit by day {meta['day']}."
    if code == "post_streak_rest_violation":
        return f"Employee {meta['employee_id']} works again too soon after a 4-day streak on day {meta['day']}."
    if code == "missing_36h_rest_after_streak":
        return f"Employee {meta['employee_id']} misses the required 36-hour recovery after a 4-day streak by day {meta['day']}."
    return f"Constraint violation: {code}."


def _build_employee_stats(
    payload: ScheduleRequest,
    employee_indexes: Iterable[int],
    assignments_by_employee: Dict[int, Dict[int, str]],
    shift_meta: Dict[str, ShiftMeta],
) -> List[EmployeeStats]:
    stats: List[EmployeeStats] = []
    for employee_idx in employee_indexes:
        employee = payload.employees[employee_idx]
        assignments = assignments_by_employee[employee_idx]
        total_hours = sum(shift_meta[shift_id].duration_hours for shift_id in assignments.values())
        day_shifts = sum(1 for shift_id in assignments.values() if shift_meta[shift_id].shift_type == "day")
        night_shifts = sum(1 for shift_id in assignments.values() if shift_meta[shift_id].shift_type == "night")
        consecutive_night_pairs = 0
        for day in assignments:
            if day + 1 in assignments:
                if shift_meta[assignments[day]].shift_type == "night" and shift_meta[assignments[day + 1]].shift_type == "night":
                    consecutive_night_pairs += 1
        stats.append(
            EmployeeStats(
                employee_id=employee.id,
                employee_name=employee.name,
                role=employee.role,
                total_hours=total_hours,
                total_shifts=len(assignments),
                day_shifts=day_shifts,
                night_shifts=night_shifts,
                consecutive_night_pairs=consecutive_night_pairs,
                assignments_by_day=assignments,
                is_cover=employee.is_cover,
            )
        )
    return sorted(stats, key=lambda item: (item.is_cover, item.employee_name, item.employee_id))


def _build_soft_violations(payload: ScheduleRequest, employee_stats: Sequence[EmployeeStats]) -> List[ViolationEntry]:
    violations: List[ViolationEntry] = []
    non_cover = [stat for stat in employee_stats if not stat.is_cover]
    if not non_cover:
        return violations

    avg_total = sum(stat.total_shifts for stat in non_cover) / len(non_cover)
    avg_day = sum(stat.day_shifts for stat in non_cover) / len(non_cover)
    avg_night = sum(stat.night_shifts for stat in non_cover) / len(non_cover)
    tolerance_day = avg_day * 0.25
    tolerance_night = avg_night * 0.25

    for stat in non_cover:
        if abs(stat.total_shifts - avg_total) > 1:
            violations.append(
                ViolationEntry(
                    code="fairness_deviation",
                    message=f"Employee {stat.employee_name} deviates from the average total number of shifts.",
                    employee_id=stat.employee_id,
                    severity="soft",
                )
            )
        if abs(stat.day_shifts - avg_day) > tolerance_day or abs(stat.night_shifts - avg_night) > tolerance_night:
            violations.append(
                ViolationEntry(
                    code="unbalanced_shift_distribution",
                    message=f"Employee {stat.employee_name} has an imbalanced day/night distribution.",
                    employee_id=stat.employee_id,
                    severity="soft",
                )
            )
        if stat.total_hours < int(payload.norm_hours * 0.85):
            violations.append(
                ViolationEntry(
                    code="below_preferred_hours",
                    message=f"Employee {stat.employee_name} is below the preferred 85% hours threshold.",
                    employee_id=stat.employee_id,
                    severity="soft",
                )
            )
        if stat.consecutive_night_pairs:
            violations.append(
                ViolationEntry(
                    code="consecutive_night_shift_pair",
                    message=f"Employee {stat.employee_name} has consecutive night shifts.",
                    employee_id=stat.employee_id,
                    severity="soft",
                )
            )
    return violations

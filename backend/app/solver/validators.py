# -*- coding: utf-8 -*-
from __future__ import annotations

import calendar
from collections import defaultdict
from typing import List, Tuple

from app.models.schemas import ScheduleRequest, ViolationEntry


def get_days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def employee_start_day(employee) -> int:
    return employee.start_day if employee.start_day is not None else 1


def validate_request_window(payload: ScheduleRequest) -> Tuple[bool, str]:
    days = get_days_in_month(payload.year, payload.month)
    for employee in payload.employees:
        start_day = employee_start_day(employee)
        if start_day > days:
            return False, f"Employee {employee.id} has start_day {start_day}, but month has only {days} days."
    return True, ""


def detect_input_conflicts(payload: ScheduleRequest) -> List[ViolationEntry]:
    conflicts: List[ViolationEntry] = []
    grouped = defaultdict(list)
    for employee in payload.employees:
        if employee.first_shift is None:
            continue
        grouped[(employee_start_day(employee), employee.first_shift)].append(employee)

    for (day, shift_id), employees in grouped.items():
        if len(employees) > 1:
            employee_names = ", ".join(employee.name for employee in employees)
            conflicts.append(
                ViolationEntry(
                    code="input_first_shift_conflict",
                    message=(
                        f"Multiple employees require first_shift {shift_id} on day {day}: {employee_names}. "
                        "Only one employee can take that shift slot."
                    ),
                    day=day,
                    shift_id=shift_id,
                    severity="soft",
                )
            )
    return conflicts

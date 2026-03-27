from __future__ import annotations

import calendar
from typing import Tuple

from app.models.schemas import ScheduleRequest


def get_days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def validate_request_window(payload: ScheduleRequest) -> Tuple[bool, str]:
    days = get_days_in_month(payload.year, payload.month)
    for employee in payload.employees:
        if employee.start_day > days:
            return False, f"Employee {employee.id} has start_day {employee.start_day}, but month has only {days} days."
    return True, ""

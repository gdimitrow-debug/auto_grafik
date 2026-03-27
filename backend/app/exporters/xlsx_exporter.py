from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from app.models.schemas import ScheduleRequest, ScheduleResponse
from app.solver.validators import get_days_in_month


def export_xlsx(payload: ScheduleRequest, response: ScheduleResponse, target_path: Path) -> Path:
    days = get_days_in_month(payload.year, payload.month)
    workbook = Workbook()
    schedule_sheet = workbook.active
    schedule_sheet.title = "Schedule"
    schedule_sheet.append(["Име", "Длъжност", *[str(day) for day in range(1, days + 1)], "Общо часове"])

    for stat in response.employee_stats:
        row = [stat.employee_name, stat.role]
        for day in range(1, days + 1):
            row.append(stat.assignments_by_day.get(day, ""))
        row.append(stat.total_hours)
        schedule_sheet.append(row)

    summary_sheet = workbook.create_sheet("Summary")
    summary_sheet.append(["Employee", "Role", "Hours", "Total shifts", "Day shifts", "Night shifts", "Cover"])
    for stat in response.employee_stats:
        summary_sheet.append([
            stat.employee_name,
            stat.role,
            stat.total_hours,
            stat.total_shifts,
            stat.day_shifts,
            stat.night_shifts,
            "Yes" if stat.is_cover else "No",
        ])

    summary_sheet.append([])
    summary_sheet.append(["Hard violations"])
    summary_sheet.append(["Code", "Message", "Employee", "Day", "Shift"])
    for violation in response.hard_violations:
        summary_sheet.append([violation.code, violation.message, violation.employee_id or "", violation.day or "", violation.shift_id or ""])

    summary_sheet.append([])
    summary_sheet.append(["Soft violations"])
    summary_sheet.append(["Code", "Message", "Employee", "Day", "Shift"])
    for violation in response.soft_violations:
        summary_sheet.append([violation.code, violation.message, violation.employee_id or "", violation.day or "", violation.shift_id or ""])

    target_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(target_path)
    return target_path

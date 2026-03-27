# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from app.models.schemas import ScheduleRequest, ScheduleResponse
from app.solver.validators import get_days_in_month


def export_csv(payload: ScheduleRequest, response: ScheduleResponse, target_path: Path) -> Path:
    import csv

    days = get_days_in_month(payload.year, payload.month)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Име", "Длъжност", *[str(day) for day in range(1, days + 1)], "Общо часове"])
        for stat in response.employee_stats:
            row = [stat.employee_name, stat.role]
            for day in range(1, days + 1):
                row.append(stat.assignments_by_day.get(day, ""))
            row.append(stat.total_hours)
            writer.writerow(row)
    return target_path
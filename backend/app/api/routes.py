# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import EXPORT_DIR
from app.exporters.csv_exporter import export_csv
from app.exporters.xlsx_exporter import export_xlsx
from app.models.schemas import ScheduleRequest, ScheduleResponse
from app.solver.engine import solve_schedule

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@router.post("/schedule", response_model=ScheduleResponse)
def generate_schedule(payload: ScheduleRequest) -> ScheduleResponse:
    return solve_schedule(payload)


@router.post("/schedule/export/csv")
def generate_schedule_csv(payload: ScheduleRequest) -> FileResponse:
    response = solve_schedule(payload)
    export_path = Path(EXPORT_DIR) / f"schedule_{payload.year}_{payload.month}.csv"
    export_csv(payload, response, export_path)
    if not export_path.exists():
        raise HTTPException(status_code=500, detail="CSV export failed.")
    return FileResponse(export_path, media_type="text/csv", filename=export_path.name)


@router.post("/schedule/export/xlsx")
def generate_schedule_xlsx(payload: ScheduleRequest) -> FileResponse:
    response = solve_schedule(payload)
    export_path = Path(EXPORT_DIR) / f"schedule_{payload.year}_{payload.month}.xlsx"
    export_xlsx(payload, response, export_path)
    if not export_path.exists():
        raise HTTPException(status_code=500, detail="XLSX export failed.")
    return FileResponse(
        export_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=export_path.name,
    )

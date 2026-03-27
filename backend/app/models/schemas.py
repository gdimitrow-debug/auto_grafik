# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ShiftDefinition(BaseModel):
    id: str
    type: Literal["day", "night"]
    start_time: str
    end_time: str
    duration_hours: int = Field(gt=0)


class EmployeeInput(BaseModel):
    id: str
    name: str
    role: str = ""
    start_day: Optional[int] = Field(default=None, ge=1, le=31)
    first_shift: Optional[str] = None
    is_cover: bool = False

    @model_validator(mode="after")
    def validate_required_fields(self) -> "EmployeeInput":
        if not self.is_cover:
            if self.start_day is None:
                raise ValueError(f"Employee {self.id} must define start_day.")
            if self.first_shift is None:
                raise ValueError(f"Employee {self.id} must define first_shift.")
        return self


class ScheduleRequest(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    norm_hours: int = Field(gt=0)
    employees: List[EmployeeInput] = Field(min_length=1)
    shifts: List[ShiftDefinition] = Field(min_length=2)

    @field_validator("shifts")
    @classmethod
    def ensure_required_shifts_exist(cls, shifts: List[ShiftDefinition]) -> List[ShiftDefinition]:
        ids = {shift.id for shift in shifts}
        if "A2" not in ids or "A3" not in ids:
            raise ValueError("Current version requires A2 and A3 shift definitions.")
        return shifts

    @model_validator(mode="after")
    def validate_references(self) -> "ScheduleRequest":
        shift_ids = {shift.id for shift in self.shifts}
        for employee in self.employees:
            if employee.first_shift is not None and employee.first_shift not in shift_ids:
                raise ValueError(f"Employee {employee.id} references unknown first_shift '{employee.first_shift}'.")
        return self


class ScheduleAssignment(BaseModel):
    employee_id: str
    employee_name: str
    day: int
    shift_id: str


class ViolationEntry(BaseModel):
    code: str
    message: str
    employee_id: Optional[str] = None
    day: Optional[int] = None
    shift_id: Optional[str] = None
    severity: Literal["hard", "soft"] = "soft"


class EmployeeStats(BaseModel):
    employee_id: str
    employee_name: str
    role: str
    total_hours: int
    total_shifts: int
    day_shifts: int
    night_shifts: int
    consecutive_night_pairs: int
    assignments_by_day: Dict[int, str]
    is_cover: bool


class ScheduleResponse(BaseModel):
    schedule: List[ScheduleAssignment]
    input_warnings: List[ViolationEntry]
    hard_violations: List[ViolationEntry]
    soft_violations: List[ViolationEntry]
    employee_stats: List[EmployeeStats]
    score: int
    is_valid: bool
    used_cover_employee: bool
    used_best_effort: bool
    explanation: str

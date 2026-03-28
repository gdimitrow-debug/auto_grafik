export const monthOptions = [
  { value: 1, label: "January" },
  { value: 2, label: "February" },
  { value: 3, label: "March" },
  { value: 4, label: "April" },
  { value: 5, label: "May" },
  { value: 6, label: "June" },
  { value: 7, label: "July" },
  { value: 8, label: "August" },
  { value: 9, label: "September" },
  { value: 10, label: "October" },
  { value: 11, label: "November" },
  { value: 12, label: "December" },
];

export function createDefaultFormState() {
  return {
    settings: {
      month: 4,
      year: 2026,
      norm_hours: 168,
    },
    shifts: [
      { localId: crypto.randomUUID(), id: "A2", type: "day", start_time: "07:00", end_time: "19:00", duration_hours: 12 },
      { localId: crypto.randomUUID(), id: "A3", type: "night", start_time: "19:00", end_time: "07:00", duration_hours: 12 },
    ],
    employees: [
      { localId: crypto.randomUUID(), id: "e1", name: "Ivan", role: "Operator", start_day: 1, first_shift: "A2", is_cover: false },
      { localId: crypto.randomUUID(), id: "e2", name: "Maria", role: "Operator", start_day: 1, first_shift: "A3", is_cover: false },
      { localId: crypto.randomUUID(), id: "e3", name: "Peter", role: "Operator", start_day: 2, first_shift: "A2", is_cover: false },
      { localId: crypto.randomUUID(), id: "e4", name: "Galia", role: "Operator", start_day: 3, first_shift: "A3", is_cover: false },
      { localId: crypto.randomUUID(), id: "cover1", name: "Reserve", role: "Cover", start_day: "", first_shift: "", is_cover: true },
    ],
    showAdvanced: false,
  };
}

export function createEmptyShift() {
  return {
    localId: crypto.randomUUID(),
    id: "",
    type: "day",
    start_time: "07:00",
    end_time: "19:00",
    duration_hours: 12,
  };
}

export function createEmptyEmployee() {
  return {
    localId: crypto.randomUUID(),
    id: "",
    name: "",
    role: "",
    start_day: "",
    first_shift: "",
    is_cover: false,
  };
}

export function buildPayload(formState) {
  return {
    month: Number(formState.settings.month),
    year: Number(formState.settings.year),
    norm_hours: Number(formState.settings.norm_hours),
    shifts: formState.shifts.map((shift) => ({
      id: shift.id.trim(),
      type: shift.type,
      start_time: shift.start_time,
      end_time: shift.end_time,
      duration_hours: Number(shift.duration_hours),
    })),
    employees: formState.employees.map((employee) => {
      const base = {
        id: employee.id.trim(),
        name: employee.name.trim(),
        role: employee.role.trim(),
        is_cover: Boolean(employee.is_cover),
      };

      if (!employee.is_cover || employee.start_day !== "") {
        base.start_day = Number(employee.start_day);
      }
      if (!employee.is_cover || employee.first_shift) {
        base.first_shift = employee.first_shift;
      }
      return base;
    }),
  };
}
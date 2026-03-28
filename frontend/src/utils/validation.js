function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

export function validateForm(formState) {
  const fieldErrors = {};
  const summary = [];
  const shiftIds = new Map();
  const employeeIds = new Map();

  const addError = (path, message) => {
    fieldErrors[path] = message;
    summary.push(message);
  };

  if (!formState.settings.month) addError("settings.month", "Please choose a month.");
  if (!formState.settings.year) addError("settings.year", "Please enter a year.");
  if (!formState.settings.norm_hours) addError("settings.norm_hours", "Please enter monthly norm hours.");

  formState.shifts.forEach((shift, index) => {
    const prefix = `shifts.${shift.localId}`;
    if (!shift.id.trim()) addError(`${prefix}.id`, `Shift #${index + 1}: code is required.`);
    if (shiftIds.has(shift.id.trim()) && shift.id.trim()) {
      addError(`${prefix}.id`, `Shift #${index + 1}: duplicate shift code.`);
    }
    shiftIds.set(shift.id.trim(), true);
    if (!shift.start_time) addError(`${prefix}.start_time`, `Shift #${index + 1}: start time is required.`);
    if (!shift.end_time) addError(`${prefix}.end_time`, `Shift #${index + 1}: end time is required.`);
    if (!shift.duration_hours || Number(shift.duration_hours) <= 0) {
      addError(`${prefix}.duration_hours`, `Shift #${index + 1}: duration must be a positive number.`);
    }
  });

  const validShiftIds = new Set(formState.shifts.map((shift) => shift.id.trim()).filter(Boolean));
  const monthDays = daysInMonth(Number(formState.settings.year), Number(formState.settings.month));

  formState.employees.forEach((employee, index) => {
    const prefix = `employees.${employee.localId}`;
    if (!employee.id.trim()) addError(`${prefix}.id`, `Employee #${index + 1}: ID is required.`);
    if (employeeIds.has(employee.id.trim()) && employee.id.trim()) {
      addError(`${prefix}.id`, `Employee #${index + 1}: duplicate employee ID.`);
    }
    employeeIds.set(employee.id.trim(), true);
    if (!employee.name.trim()) addError(`${prefix}.name`, `Employee #${index + 1}: name is required.`);
    if (!employee.is_cover) {
      if (employee.start_day === "" || Number(employee.start_day) < 1 || Number(employee.start_day) > monthDays) {
        addError(`${prefix}.start_day`, `Employee #${index + 1}: start day must be a valid day in the selected month.`);
      }
      if (!employee.first_shift) {
        addError(`${prefix}.first_shift`, `Employee #${index + 1}: first shift is required.`);
      } else if (!validShiftIds.has(employee.first_shift)) {
        addError(`${prefix}.first_shift`, `Employee #${index + 1}: first shift must exist in the shifts list.`);
      }
    } else {
      if (employee.start_day !== "" && (Number(employee.start_day) < 1 || Number(employee.start_day) > monthDays)) {
        addError(`${prefix}.start_day`, `Employee #${index + 1}: start day must be valid.`);
      }
      if (employee.first_shift && !validShiftIds.has(employee.first_shift)) {
        addError(`${prefix}.first_shift`, `Employee #${index + 1}: selected first shift does not exist.`);
      }
    }
  });

  return { fieldErrors, summary };
}
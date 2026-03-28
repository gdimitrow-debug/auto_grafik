import React from "react";
import { createSchedule, exportSchedule } from "./api/client";
import { EmployeeListEditor } from "./components/EmployeeListEditor";
import { ExportActions } from "./components/ExportActions";
import { JsonAdvancedEditor } from "./components/JsonAdvancedEditor";
import { ScheduleActions } from "./components/ScheduleActions";
import { ScheduleGrid } from "./components/ScheduleGrid";
import { ScheduleSettingsForm } from "./components/ScheduleSettingsForm";
import { ShiftListEditor } from "./components/ShiftListEditor";
import { SummaryPanel } from "./components/SummaryPanel";
import { ValidationSummary } from "./components/ValidationSummary";
import { ViolationsPanel } from "./components/ViolationsPanel";
import { buildPayload, createDefaultFormState } from "./utils/formState";
import { validateForm } from "./utils/validation";
import "./styles.css";

export default function App() {
  const [formState, setFormState] = React.useState(createDefaultFormState);
  const [validationErrors, setValidationErrors] = React.useState({ fieldErrors: {}, summary: [] });
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [exporting, setExporting] = React.useState(false);

  const payload = React.useMemo(() => buildPayload(formState), [formState]);

  const updateSettings = (key, value) => {
    setFormState((current) => ({ ...current, settings: { ...current.settings, [key]: value } }));
  };

  const updateShift = (localId, key, value) => {
    setFormState((current) => ({
      ...current,
      shifts: current.shifts.map((shift) => (shift.localId === localId ? { ...shift, [key]: value } : shift)),
    }));
  };

  const updateEmployee = (localId, key, value) => {
    setFormState((current) => ({
      ...current,
      employees: current.employees.map((employee) => {
        if (employee.localId !== localId) return employee;
        const next = { ...employee, [key]: value };
        if (key === "is_cover" && value) {
          next.start_day = "";
          next.first_shift = "";
        }
        return next;
      }),
    }));
  };

  const runValidation = () => {
    const nextErrors = validateForm(formState);
    setValidationErrors(nextErrors);
    return nextErrors;
  };

  const handleGenerate = async () => {
    const nextErrors = runValidation();
    if (nextErrors.summary.length) {
      setError("The form contains errors. Please fix them before generating the schedule.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const data = await createSchedule(payload);
      setResult(data);
    } catch {
      setError("We could not generate the schedule. Please review the data and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (kind) => {
    const nextErrors = runValidation();
    if (nextErrors.summary.length) {
      setError("Export is blocked because the form still contains validation errors.");
      return;
    }

    setExporting(true);
    setError("");
    try {
      await exportSchedule(kind, payload);
    } catch {
      setError("We could not create the export file.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Auto Grafik</p>
        <h1>Employee Schedule Generator</h1>
        <p>Use the form to enter data, generate the schedule, and review the result in a table.</p>
      </header>

      {error ? <section className="panel error-banner">{error}</section> : null}
      <ValidationSummary errors={validationErrors.summary} />

      <div className="stack page-stack">
        <ScheduleSettingsForm settings={formState.settings} errors={validationErrors.fieldErrors} onChange={updateSettings} />
        <ShiftListEditor
          shifts={formState.shifts}
          errors={validationErrors.fieldErrors}
          onChange={updateShift}
          onAdd={(shift) => setFormState((current) => ({ ...current, shifts: [...current.shifts, shift] }))}
          onRemove={(localId) => setFormState((current) => ({ ...current, shifts: current.shifts.filter((shift) => shift.localId !== localId) }))}
        />
        <EmployeeListEditor
          employees={formState.employees}
          shifts={formState.shifts}
          errors={validationErrors.fieldErrors}
          onChange={updateEmployee}
          onAdd={(employee) => setFormState((current) => ({ ...current, employees: [...current.employees, employee] }))}
          onRemove={(localId) => setFormState((current) => ({ ...current, employees: current.employees.filter((employee) => employee.localId !== localId) }))}
        />
        <ScheduleActions
          loading={loading}
          onGenerate={handleGenerate}
          onToggleAdvanced={() => setFormState((current) => ({ ...current, showAdvanced: !current.showAdvanced }))}
          showAdvanced={formState.showAdvanced}
        />
        {formState.showAdvanced ? <JsonAdvancedEditor payload={payload} /> : null}
        <SummaryPanel result={result} />
        <ScheduleGrid result={result} />
        <ViolationsPanel result={result} />
        {result ? (
          <ExportActions
            disabled={exporting}
            onExportCsv={() => handleExport("csv")}
            onExportXlsx={() => handleExport("xlsx")}
          />
        ) : null}
      </div>
    </main>
  );
}
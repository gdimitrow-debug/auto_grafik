import { monthOptions } from "../utils/formState";
import { FieldError } from "./FieldError";
import { FieldHint } from "./FieldHint";

export function ScheduleSettingsForm({ settings, errors, onChange }) {
  return (
    <section className="panel">
      <h2>Basic settings</h2>
      <div className="form-grid">
        <label className="field">
          <span>Month</span>
          <select value={settings.month} onChange={(event) => onChange("month", Number(event.target.value))}>
            {monthOptions.map((month) => (
              <option key={month.value} value={month.value}>{month.label}</option>
            ))}
          </select>
          <FieldHint>Select the month for which the schedule should be generated.</FieldHint>
          <FieldError error={errors["settings.month"]} />
        </label>

        <label className="field">
          <span>Year</span>
          <input type="number" value={settings.year} onChange={(event) => onChange("year", event.target.value)} />
          <FieldHint>Enter the calendar year.</FieldHint>
          <FieldError error={errors["settings.year"]} />
        </label>

        <label className="field">
          <span>Monthly norm hours</span>
          <input type="number" value={settings.norm_hours} onChange={(event) => onChange("norm_hours", event.target.value)} />
          <FieldHint>This limit is used by the solver when distributing shifts.</FieldHint>
          <FieldError error={errors["settings.norm_hours"]} />
        </label>
      </div>
    </section>
  );
}
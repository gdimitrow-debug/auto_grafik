import { createEmptyShift } from "../utils/formState";
import { FieldError } from "./FieldError";
import { FieldHint } from "./FieldHint";

export function ShiftListEditor({ shifts, errors, onChange, onAdd, onRemove }) {
  return (
    <section className="panel">
      <div className="section-header">
        <div>
          <h2>Shifts</h2>
          <p className="section-copy">Add all shift definitions that can be used in the schedule.</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => onAdd(createEmptyShift())}>Add shift</button>
      </div>

      <div className="stack">
        {shifts.map((shift, index) => {
          const prefix = `shifts.${shift.localId}`;
          return (
            <div className="editor-card" key={shift.localId}>
              <div className="card-header">
                <h3>Shift #{index + 1}</h3>
                <button type="button" className="text-button" onClick={() => onRemove(shift.localId)}>Delete</button>
              </div>
              <div className="form-grid compact-grid">
                <label className="field">
                  <span>Code</span>
                  <input value={shift.id} onChange={(event) => onChange(shift.localId, "id", event.target.value)} />
                  <FieldError error={errors[`${prefix}.id`]} />
                </label>
                <label className="field">
                  <span>Type</span>
                  <select value={shift.type} onChange={(event) => onChange(shift.localId, "type", event.target.value)}>
                    <option value="day">day</option>
                    <option value="night">night</option>
                  </select>
                </label>
                <label className="field">
                  <span>Start time</span>
                  <input type="time" value={shift.start_time} onChange={(event) => onChange(shift.localId, "start_time", event.target.value)} />
                  <FieldError error={errors[`${prefix}.start_time`]} />
                </label>
                <label className="field">
                  <span>End time</span>
                  <input type="time" value={shift.end_time} onChange={(event) => onChange(shift.localId, "end_time", event.target.value)} />
                  <FieldError error={errors[`${prefix}.end_time`]} />
                </label>
                <label className="field">
                  <span>Duration hours</span>
                  <input type="number" value={shift.duration_hours} onChange={(event) => onChange(shift.localId, "duration_hours", event.target.value)} />
                  <FieldHint>Use a positive number.</FieldHint>
                  <FieldError error={errors[`${prefix}.duration_hours`]} />
                </label>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
import { createEmptyEmployee } from "../utils/formState";
import { FieldError } from "./FieldError";
import { FieldHint } from "./FieldHint";

export function EmployeeListEditor({ employees, shifts, errors, onChange, onAdd, onRemove }) {
  return (
    <section className="panel">
      <div className="section-header">
        <div>
          <h2>Employees</h2>
          <p className="section-copy">Enter the employees and their start constraints.</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => onAdd(createEmptyEmployee())}>Add employee</button>
      </div>

      <div className="stack">
        {employees.map((employee, index) => {
          const prefix = `employees.${employee.localId}`;
          return (
            <div className="editor-card" key={employee.localId}>
              <div className="card-header">
                <h3>Employee #{index + 1}</h3>
                <button type="button" className="text-button" onClick={() => onRemove(employee.localId)}>Delete</button>
              </div>
              <div className="form-grid compact-grid">
                <label className="field">
                  <span>ID</span>
                  <input value={employee.id} onChange={(event) => onChange(employee.localId, "id", event.target.value)} />
                  <FieldError error={errors[`${prefix}.id`]} />
                </label>
                <label className="field">
                  <span>Name</span>
                  <input value={employee.name} onChange={(event) => onChange(employee.localId, "name", event.target.value)} />
                  <FieldError error={errors[`${prefix}.name`]} />
                </label>
                <label className="field">
                  <span>Role</span>
                  <input value={employee.role} onChange={(event) => onChange(employee.localId, "role", event.target.value)} />
                </label>
                <label className="field checkbox-field">
                  <span>Cover employee</span>
                  <input type="checkbox" checked={employee.is_cover} onChange={(event) => onChange(employee.localId, "is_cover", event.target.checked)} />
                  <FieldHint>The cover employee is used only when needed.</FieldHint>
                </label>
                <label className="field">
                  <span>Start day</span>
                  <input type="number" value={employee.start_day} onChange={(event) => onChange(employee.localId, "start_day", event.target.value)} placeholder={employee.is_cover ? "optional" : "required"} />
                  <FieldError error={errors[`${prefix}.start_day`]} />
                </label>
                <label className="field">
                  <span>First shift</span>
                  <select value={employee.first_shift} onChange={(event) => onChange(employee.localId, "first_shift", event.target.value)}>
                    <option value="">{employee.is_cover ? "optional" : "select shift"}</option>
                    {shifts.map((shift) => (
                      <option key={shift.localId} value={shift.id}>{shift.id || "(missing code)"}</option>
                    ))}
                  </select>
                  <FieldError error={errors[`${prefix}.first_shift`]} />
                </label>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
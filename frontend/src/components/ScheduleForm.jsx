import React from "react";

const samplePayload = {
  month: 4,
  year: 2026,
  norm_hours: 168,
  shifts: [
    { id: "A2", type: "day", start_time: "07:00", end_time: "19:00", duration_hours: 12 },
    { id: "A3", type: "night", start_time: "19:00", end_time: "07:00", duration_hours: 12 },
  ],
  employees: [
    { id: "e1", name: "Иван", role: "Оператор", start_day: 1, first_shift: "A2", is_cover: false },
    { id: "e2", name: "Мария", role: "Оператор", start_day: 1, first_shift: "A3", is_cover: false },
    { id: "e3", name: "Петър", role: "Оператор", start_day: 2, first_shift: "A2", is_cover: false },
    { id: "e4", name: "Галя", role: "Оператор", start_day: 3, first_shift: "A3", is_cover: false },
    { id: "e5", name: "Нели", role: "Оператор", start_day: 4, first_shift: "A2", is_cover: false },
    { id: "e6", name: "Резерв", role: "Покриващ", start_day: 1, first_shift: "A3", is_cover: true },
  ],
};

export function ScheduleForm({ onSubmit, loading }) {
  const [value, setValue] = React.useState(JSON.stringify(samplePayload, null, 2));

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(JSON.parse(value));
  };

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className="panel-header">
        <h2>Input JSON</h2>
        <button type="submit" disabled={loading}>{loading ? "Generating..." : "Generate schedule"}</button>
      </div>
      <textarea value={value} onChange={(event) => setValue(event.target.value)} rows={24} />
    </form>
  );
}

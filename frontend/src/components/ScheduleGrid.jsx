import React from "react";

export function ScheduleGrid({ result }) {
  if (!result || !result.employee_stats?.length) {
    return (
      <section className="panel">
        <h2>Schedule</h2>
        <p>No result yet.</p>
      </section>
    );
  }

  const days = Object.keys(result.employee_stats[0].assignments_by_day)
    .map(Number)
    .sort((a, b) => a - b);
  const maxDay = Math.max(days.at(-1) || 0, ...result.schedule.map((item) => item.day));
  const dayList = Array.from({ length: maxDay }, (_, index) => index + 1);

  return (
    <section className="panel">
      <h2>Schedule</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              {dayList.map((day) => <th key={day}>{day}</th>)}
              <th>Hours</th>
            </tr>
          </thead>
          <tbody>
            {result.employee_stats.map((stat) => (
              <tr key={stat.employee_id}>
                <td>{stat.employee_name}</td>
                <td>{stat.role}</td>
                {dayList.map((day) => <td key={day}>{stat.assignments_by_day[day] || ""}</td>)}
                <td>{stat.total_hours}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
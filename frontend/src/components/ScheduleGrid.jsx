export function ScheduleGrid({ result }) {
  if (!result || !result.employee_stats?.length) {
    return null;
  }

  const days = Array.from(
    { length: Math.max(...result.schedule.map((item) => item.day), 1) },
    (_, index) => index + 1
  );

  return (
    <section className="panel">
      <h2>Schedule</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              {days.map((day) => <th key={day}>{day}</th>)}
              <th>Day shifts</th>
              <th>Night shifts</th>
              <th>Hours</th>
            </tr>
          </thead>
          <tbody>
            {result.employee_stats.map((stat) => (
              <tr key={stat.employee_id}>
                <td>{stat.employee_name}</td>
                <td>{stat.role}</td>
                {days.map((day) => <td key={day}>{stat.assignments_by_day[day] || ""}</td>)}
                <td>{stat.day_shifts}</td>
                <td>{stat.night_shifts}</td>
                <td>{stat.total_hours}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

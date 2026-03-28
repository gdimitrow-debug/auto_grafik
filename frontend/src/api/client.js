const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export async function createSchedule(payload) {
  const response = await fetch(`${API_BASE}/schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Възникна грешка при заявката.");
  }

  return response.json();
}

export async function exportSchedule(kind, payload) {
  const response = await fetch(`${API_BASE}/schedule/export/${kind}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Експортът не беше успешен.");
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = kind === "csv" ? "schedule.csv" : "schedule.xlsx";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}
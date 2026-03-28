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
    throw new Error(text || "Request failed");
  }

  return response.json();
}

export function buildExportUrl(kind) {
  return `${API_BASE}/schedule/export/${kind}`;
}
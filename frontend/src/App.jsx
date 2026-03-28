import React from "react";
import { createSchedule } from "./api/client";
import { ScheduleForm } from "./components/ScheduleForm";
import { ScheduleGrid } from "./components/ScheduleGrid";
import { SummaryPanel } from "./components/SummaryPanel";

export default function App() {
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (payload) => {
    setLoading(true);
    setError("");
    try {
      const data = await createSchedule(payload);
      setResult(data);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Auto Grafik</p>
        <h1>Employee Schedule Generator</h1>
        <p>FastAPI + OR-Tools backend with a simple React interface.</p>
      </header>
      <div className="layout">
        <ScheduleForm onSubmit={handleSubmit} loading={loading} />
        <SummaryPanel result={result} error={error} />
      </div>
      <ScheduleGrid result={result} />
    </main>
  );
}
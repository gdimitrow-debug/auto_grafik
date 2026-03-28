export function ScheduleActions({ loading, onGenerate, onToggleAdvanced, showAdvanced }) {
  return (
    <section className="panel actions-panel">
      <div>
        <h2>Generate</h2>
        <p className="section-copy">Review the data and generate the schedule.</p>
      </div>
      <div className="actions-row">
        <button type="button" className="primary-button" onClick={onGenerate} disabled={loading}>
          {loading ? "Generating..." : "Generate Schedule"}
        </button>
        <button type="button" className="secondary-button" onClick={onToggleAdvanced}>
          {showAdvanced ? "Hide Advanced JSON mode" : "Advanced JSON mode"}
        </button>
      </div>
    </section>
  );
}
export function SummaryPanel({ result }) {
  if (!result) return null;

  return (
    <section className="panel">
      <h2>Result summary</h2>
      <div className="summary-grid summary-grid-3">
        <div><strong>Score:</strong> {result.score}</div>
        <div><strong>Valid schedule:</strong> {String(result.is_valid)}</div>
        <div><strong>Cover used:</strong> {String(result.used_cover_employee)}</div>
        <div><strong>Best effort:</strong> {String(result.used_best_effort)}</div>
        <div><strong>Input warnings:</strong> {result.input_warnings?.length || 0}</div>
        <div><strong>Hard violations:</strong> {result.hard_violations?.length || 0}</div>
        <div><strong>Soft violations:</strong> {result.soft_violations?.length || 0}</div>
      </div>
    </section>
  );
}
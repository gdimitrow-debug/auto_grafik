import React from "react";

function ViolationList({ title, items }) {
  return (
    <div>
      <h3>{title}</h3>
      {items.length === 0 ? <p>None</p> : (
        <ul>
          {items.map((item, index) => (
            <li key={`${item.code}-${index}`}>{item.message}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function SummaryPanel({ result, error }) {
  return (
    <section className="panel">
      <h2>Summary</h2>
      {error && <p className="error">{error}</p>}
      {!result ? <p>No result yet.</p> : (
        <>
          <div className="summary-grid">
            <div><strong>Score:</strong> {result.score}</div>
            <div><strong>Valid:</strong> {String(result.is_valid)}</div>
            <div><strong>Best effort:</strong> {String(result.used_best_effort)}</div>
            <div><strong>Cover used:</strong> {String(result.used_cover_employee)}</div>
          </div>
          <p>{result.explanation}</p>
          <ViolationList title="Hard violations" items={result.hard_violations || []} />
          <ViolationList title="Soft violations" items={result.soft_violations || []} />
        </>
      )}
    </section>
  );
}

function ItemList({ title, items, emptyText }) {
  return (
    <div className="violation-group">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p>{emptyText}</p>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={`${item.code}-${index}`}>
              <strong>{item.code}</strong>: {item.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function ViolationsPanel({ result }) {
  if (!result) return null;

  return (
    <section className="panel">
      <h2>Warnings and violations</h2>
      <div className="violations-layout">
        <ItemList title="Input warnings" items={result.input_warnings || []} emptyText="No input warnings." />
        <ItemList title="Hard violations" items={result.hard_violations || []} emptyText="No hard violations." />
        <ItemList title="Soft violations" items={result.soft_violations || []} emptyText="No soft violations." />
      </div>
    </section>
  );
}
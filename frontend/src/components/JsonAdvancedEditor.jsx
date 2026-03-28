export function JsonAdvancedEditor({ payload }) {
  return (
    <section className="panel">
      <h2>Advanced JSON mode</h2>
      <p className="section-copy">This is the payload generated from the form.</p>
      <textarea readOnly rows={20} value={JSON.stringify(payload, null, 2)} />
    </section>
  );
}
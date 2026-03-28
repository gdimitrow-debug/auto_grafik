export function ExportActions({ disabled, onExportCsv, onExportXlsx }) {
  return (
    <section className="panel actions-panel">
      <div>
        <h2>Export</h2>
        <p className="section-copy">Download the generated schedule in a file format.</p>
      </div>
      <div className="actions-row">
        <button type="button" className="secondary-button" onClick={onExportCsv} disabled={disabled}>Export CSV</button>
        <button type="button" className="secondary-button" onClick={onExportXlsx} disabled={disabled}>Export XLSX</button>
      </div>
    </section>
  );
}
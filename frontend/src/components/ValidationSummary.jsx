export function ValidationSummary({ errors }) {
  if (!errors.length) return null;

  return (
    <section className="panel validation-panel">
      <h2>Please fix the following fields</h2>
      <ul>
        {errors.map((error, index) => (
          <li key={`${error}-${index}`}>{error}</li>
        ))}
      </ul>
    </section>
  );
}
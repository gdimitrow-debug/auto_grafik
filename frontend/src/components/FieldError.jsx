export function FieldError({ error }) {
  if (!error) return null;
  return <p className="field-error">{error}</p>;
}
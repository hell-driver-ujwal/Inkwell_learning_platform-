/** Consistent accessible loading and form feedback. */
export function ErrorMessage({ children }) {
  return children ? (
    <div className="notice error" role="alert">
      {children}
    </div>
  ) : null;
}
export function Notice({ children }) {
  return children ? (
    <div className="notice" role="status">
      {children}
    </div>
  ) : null;
}
export function Loading() {
  return (
    <p role="status" className="muted">
      Loading…
    </p>
  );
}
export function ResourceState({ resource, children }) {
  if (resource.loading) return <Loading />;
  if (resource.error) return <ErrorMessage>{resource.error}</ErrorMessage>;
  return children(resource.data);
}

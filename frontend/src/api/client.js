/** One HTTP boundary for session cookies, CSRF and readable API errors. */
let csrfToken = "";
export function setCsrfToken(token) {
  csrfToken = token;
}
function describeErrors(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(describeErrors).join(" ");
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([field, errors]) => `${field}: ${describeErrors(errors)}`)
      .join(" • ");
  }
  return "The request could not be completed.";
}
export async function api(path, options = {}) {
  const headers = { ...options.headers };
  const isForm = options.body instanceof FormData;
  if (options.body && !isForm) headers["Content-Type"] = "application/json";
  if (csrfToken) headers["X-CSRFToken"] = csrfToken;
  const response = await fetch(`/api/${path}`, {
    ...options,
    credentials: "same-origin",
    headers,
    body: options.body && !isForm ? JSON.stringify(options.body) : options.body,
  });
  if (response.status === 204) return null;
  const payload = await response
    .json()
    .catch(() => ({ errors: "The server returned an unreadable response." }));
  if (!response.ok) throw new Error(describeErrors(payload.errors || payload));
  if (payload.csrf_token) setCsrfToken(payload.csrf_token);
  return payload;
}
export async function allPages(path) {
  const first = await api(path);
  if (!first.results) return first;
  let records = first.results;
  let next = first.next;
  while (next) {
    const url = new URL(next, window.location.origin);
    const page = await api(url.pathname.replace("/api/", "") + url.search);
    records = [...records, ...page.results];
    next = page.next;
  }
  return records;
}

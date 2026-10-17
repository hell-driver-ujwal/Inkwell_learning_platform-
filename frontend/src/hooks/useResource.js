/** Fetch a page resource and ignore stale responses after navigation. */
import { useCallback, useEffect, useState } from "react";
import { api, allPages } from "../api/client";
export function useResource(path, { all = false } = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [version, setVersion] = useState(0);
  const reload = useCallback(() => setVersion((current) => current + 1), []);
  useEffect(() => {
    let current = true;
    setLoading(true);
    setError("");
    const request = all
      ? allPages(path).then((results) => ({ results, count: results.length }))
      : api(path);
    request
      .then((result) => {
        if (current) setData(result);
      })
      .catch((failure) => {
        if (current) setError(failure.message);
      })
      .finally(() => {
        if (current) setLoading(false);
      });
    return () => {
      current = false;
    };
  }, [path, version, all]);
  return { data, error, loading, reload };
}

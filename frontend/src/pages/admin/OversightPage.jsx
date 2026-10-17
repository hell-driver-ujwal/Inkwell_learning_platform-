/** Read-only oversight plus the specific unpublish action allowed to administrators. */
import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
export default function OversightPage({ kind }) {
  const [params, setParams] = useSearchParams();
  const resource = useResource(`admin/${kind}/?${params}`);
  const [error, setError] = useState("");
  async function perform(id, action) {
    try {
      await api(`admin/${kind}/${id}/${action}/`, { method: "POST" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function remove(id) {
    if (
      !window.confirm(
        "Delete this unused content? Attempts and payment history will block deletion.",
      )
    )
      return;
    try {
      await api(`admin/${kind}/${id}/`, { method: "DELETE" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <h1>{kind[0].toUpperCase() + kind.slice(1)}</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <ResourceState resource={resource}>
        {(data) => (
          <>
            <div className="record-list">
              {data.results.map((entry) => (
                <article className="panel" key={entry.id}>
                  {kind === "messages" ? (
                    <>
                      <h2>{entry.subject}</h2>
                      <p>
                        {entry.sender_name} · {entry.sender_email}
                      </p>
                      <p>{entry.message}</p>
                      <div className="actions">
                        <button onClick={() => perform(entry.id, "read")}>
                          {entry.is_read ? "Read" : "Mark as read"}
                        </button>
                        <a
                          href={`mailto:${entry.sender_email}?subject=${encodeURIComponent(`Re: ${entry.subject}`)}`}
                        >
                          Reply by email →
                        </a>
                      </div>
                    </>
                  ) : kind === "payments" ? (
                    <>
                      <h2>{entry.course_title}</h2>
                      <p>
                        NPR {entry.amount_npr} · {entry.status}
                      </p>
                      <p>
                        {entry.provider_reference || entry.transaction_uuid}
                      </p>
                    </>
                  ) : (
                    <>
                      <h2>
                        <Link
                          to={
                            kind === "courses"
                              ? `/courses/${entry.id}`
                              : `/activities/${entry.id}?preview=1`
                          }
                        >
                          {entry.title}
                        </Link>
                      </h2>
                      <p>
                        {entry.teacher_name || entry.kind} · {entry.status}
                      </p>
                      <button
                        className="text-button"
                        onClick={() => remove(entry.id)}
                      >
                        Delete unused content
                      </button>
                      {entry.status === "Published" && (
                        <button
                          className="secondary"
                          onClick={() => perform(entry.id, "unpublish")}
                        >
                          Unpublish
                        </button>
                      )}
                    </>
                  )}
                </article>
              ))}
            </div>
            <div className="actions">
              {data.previous && (
                <button
                  onClick={() =>
                    setParams({ page: Number(params.get("page")) - 1 })
                  }
                >
                  Previous
                </button>
              )}
              {data.next && (
                <button
                  onClick={() =>
                    setParams({ page: Number(params.get("page") || 1) + 1 })
                  }
                >
                  Next
                </button>
              )}
            </div>
          </>
        )}
      </ResourceState>
    </>
  );
}

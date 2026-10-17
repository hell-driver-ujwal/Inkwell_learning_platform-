/** Conventional forms for two small administrative reference-data resources. */
import { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
export default function ContentAdminPage() {
  const { resource: name } = useParams();
  const endpoint = name === "subjects" ? "subjects" : "faqs";
  const resource = useResource(`admin/${endpoint}/`, { all: true });
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");
  async function save(event) {
    event.preventDefault();
    try {
      await api(`admin/${endpoint}/${editing ? `${editing.id}/` : ""}`, {
        method: editing ? "PATCH" : "POST",
        body: Object.fromEntries(new FormData(event.currentTarget)),
      });
      resource.reload();
      setEditing(null);
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function remove(id) {
    if (!window.confirm("Delete this record?")) return;
    try {
      await api(`admin/${endpoint}/${id}/`, { method: "DELETE" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <h1>{endpoint === "subjects" ? "Subjects" : "Help & FAQs"}</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <ResourceState resource={resource}>
        {(data) => (
          <ul className="record-list">
            {data.results.map((entry) => (
              <li key={entry.id}>
                <span>{entry.name || entry.question}</span>
                <button
                  className="text-button"
                  onClick={() => setEditing(entry)}
                >
                  Edit
                </button>
                <button
                  className="text-button"
                  onClick={() => remove(entry.id)}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </ResourceState>
      <form
        className="panel"
        onSubmit={save}
        key={`${endpoint}-${editing?.id || "new"}`}
      >
        <h2>{editing ? "Edit record" : "Add record"}</h2>
        {endpoint === "subjects" ? (
          <>
            <Field
              label="Name"
              name="name"
              defaultValue={editing?.name}
              required
            />
            <Field
              label="Description"
              name="description"
              as="textarea"
              defaultValue={editing?.description}
            />
          </>
        ) : (
          <>
            <Field
              label="Question"
              name="question"
              defaultValue={editing?.question}
              minLength={5}
              required
            />
            <Field
              label="Answer"
              name="answer"
              as="textarea"
              defaultValue={editing?.answer}
              minLength={10}
              required
            />
            <Field
              label="Audience"
              name="audience"
              as="select"
              defaultValue={editing?.audience || "All"}
            >
              <option>All</option>
              <option>Learner</option>
              <option>Teacher</option>
            </Field>
            <Field
              label="Order"
              name="sort_order"
              type="number"
              defaultValue={editing?.sort_order || 1}
              min="1"
            />
          </>
        )}
        <div className="actions">
          <button>Save</button>
          {editing && (
            <button
              type="button"
              className="secondary"
              onClick={() => setEditing(null)}
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </>
  );
}

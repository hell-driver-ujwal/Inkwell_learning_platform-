/** Activity settings and content remain separate, focused forms. */
import { useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, Notice, ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
import ActivityContentEditor from "../../features/authoring/ActivityContentEditor";
function ActivityForm({ activity, topic, reload }) {
  const [kind, setKind] = useState(activity?.kind || "Quiz");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  async function save(event) {
    event.preventDefault();
    const body = {
      ...Object.fromEntries(new FormData(event.currentTarget)),
      kind,
      topic: Number(topic),
    };
    body.is_closed = body.is_closed === "on";
    try {
      const saved = await api(
        activity ? `author/activities/${activity.id}/` : "author/activities/",
        { method: activity ? "PATCH" : "POST", body },
      );
      setMessage("Settings saved.");
      if (!activity) navigate(`/author/activities/${saved.id}?topic=${topic}`);
      else reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <ErrorMessage>{error}</ErrorMessage>
      <Notice>{message}</Notice>
      <form onSubmit={save}>
        <Field
          label="Activity type"
          as="select"
          value={kind}
          disabled={Boolean(activity)}
          onChange={(event) => setKind(event.target.value)}
        >
          {["Quiz", "SelfAssessment", "Game", "Scenario", "Discussion"].map(
            (type) => (
              <option key={type}>{type}</option>
            ),
          )}
        </Field>
        <Field
          label="Title"
          name="title"
          defaultValue={activity?.title}
          minLength={3}
          required
        />
        <Field
          label="Description / prompt"
          name="description"
          as="textarea"
          defaultValue={activity?.description}
        />
        <Field
          label="Order"
          name="sort_order"
          type="number"
          min="1"
          defaultValue={activity?.sort_order || 1}
        />
        {kind === "Quiz" && (
          <>
            <Field
              label="Time limit in minutes (0 = untimed)"
              name="time_limit_minutes"
              type="number"
              min="0"
              max="180"
              defaultValue={activity?.time_limit_minutes || 0}
            />
            <Field
              label="Maximum attempts (0 = unlimited)"
              name="max_attempts"
              type="number"
              min="0"
              max="10"
              defaultValue={activity?.max_attempts || 0}
            />
          </>
        )}
        {kind === "Game" && (
          <Field
            label="Game template"
            name="game_template"
            as="select"
            defaultValue={activity?.game_template || "Matching"}
          >
            {[
              "Matching",
              "Memory",
              "Flashcards",
              "Scramble",
              "Sort",
              "FillBlank",
              "TrueFalse",
              "Sequence",
            ].map((template) => (
              <option key={template}>{template}</option>
            ))}
          </Field>
        )}
        {kind === "Discussion" && (
          <label className="choice">
            <input
              type="checkbox"
              name="is_closed"
              defaultChecked={activity?.is_closed}
            />
            Close discussion
          </label>
        )}
        <Field
          label="Status"
          name="status"
          as="select"
          defaultValue={activity?.status || "Draft"}
        >
          <option>Draft</option>
          {activity && <option>Published</option>}
        </Field>
        <button>Save settings</button>
      </form>
    </>
  );
}
function ExistingEditor({ id, topic }) {
  const resource = useResource(`author/activities/${id}/`);
  return (
    <ResourceState resource={resource}>
      {(activity) => (
        <>
          <Link to={`/activities/${id}?preview=1`}>Preview activity →</Link>
          <ActivityForm
            activity={activity}
            topic={topic}
            reload={resource.reload}
          />
          {activity.kind !== "Discussion" && (
            <ActivityContentEditor activity={activity} />
          )}
        </>
      )}
    </ResourceState>
  );
}
export default function ActivityEditorPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  return (
    <section className="editor">
      <h1>{id === "new" ? "Create an activity" : "Activity editor"}</h1>
      {id === "new" ? (
        <ActivityForm topic={params.get("topic")} />
      ) : (
        <ExistingEditor id={id} topic={params.get("topic")} />
      )}
    </section>
  );
}

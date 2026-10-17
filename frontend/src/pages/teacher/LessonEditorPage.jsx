/** Lesson editing supports all seven original material formats and multipart uploads. */
import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
function LessonForm({ lesson, topic }) {
  const [kind, setKind] = useState(lesson?.kind || "Text");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  async function save(event) {
    event.preventDefault();
    const body = new FormData(event.currentTarget);
    body.set("topic", topic);
    body.set("kind", kind);
    body.set("is_preview", String(body.get("is_preview") === "on"));
    if (!body.get("file")?.size) body.delete("file");
    try {
      await api(
        lesson ? `author/materials/${lesson.id}/` : "author/materials/",
        { method: lesson ? "PATCH" : "POST", body },
      );
      const parent = await api(`author/topics/${topic}/`);
      navigate(`/author/courses/${parent.course}`);
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <form onSubmit={save}>
      <ErrorMessage>{error}</ErrorMessage>
      <Field
        label="Title"
        name="title"
        defaultValue={lesson?.title}
        minLength={3}
        required
      />
      <Field
        label="Format"
        as="select"
        value={kind}
        onChange={(event) => setKind(event.target.value)}
      >
        {["Text", "Image", "PDF", "Video", "Audio", "YouTube", "Code"].map(
          (format) => (
            <option key={format}>{format}</option>
          ),
        )}
      </Field>
      <Field
        label={
          kind === "Code"
            ? "Starter HTML, CSS and JavaScript"
            : "Lesson text / transcript"
        }
        name="text_content"
        as="textarea"
        rows="12"
        defaultValue={lesson?.text_content}
      />
      {["Image", "PDF", "Video", "Audio"].includes(kind) && (
        <Field label="Media file" name="file" type="file" />
      )}
      <Field
        label="Image alternative text"
        name="alt_text"
        defaultValue={lesson?.alt_text}
      />
      <Field
        label="YouTube URL"
        name="youtube_url"
        type="url"
        defaultValue={lesson?.youtube_url}
      />
      <Field
        label="Order"
        name="sort_order"
        type="number"
        min="1"
        defaultValue={lesson?.sort_order || 1}
      />
      <Field
        label="Status"
        name="status"
        as="select"
        defaultValue={lesson?.status || "Draft"}
      >
        <option>Draft</option>
        <option>Published</option>
      </Field>
      <label className="choice">
        <input
          name="is_preview"
          type="checkbox"
          defaultChecked={lesson?.is_preview}
        />
        Free public preview
      </label>
      <button>Save lesson</button>
    </form>
  );
}
function ExistingLesson({ id, topic }) {
  const resource = useResource(`author/materials/${id}/`);
  return (
    <ResourceState resource={resource}>
      {(lesson) => <LessonForm lesson={lesson} topic={topic} />}
    </ResourceState>
  );
}
export default function LessonEditorPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  return (
    <section className="editor">
      <h1>{id === "new" ? "Create a lesson" : "Edit lesson"}</h1>
      {id === "new" ? (
        <LessonForm topic={params.get("topic")} />
      ) : (
        <ExistingLesson id={id} topic={params.get("topic")} />
      )}
    </section>
  );
}

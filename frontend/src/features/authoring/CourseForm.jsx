/** Course metadata is independent of curriculum and activity editing. */
import { useState } from "react";
import { useResource } from "../../hooks/useResource";
import Field from "../../components/Field";
export default function CourseForm({ course, save }) {
  const subjects = useResource("subjects/", { all: true });
  const [paid, setPaid] = useState(course?.is_paid || false);
  function submit(event) {
    event.preventDefault();
    const body = new FormData(event.currentTarget);
    body.set("is_paid", String(paid));
    if (!paid) body.set("price_npr", "0");
    if (!body.get("cover")?.size) body.delete("cover");
    save(body);
  }
  return (
    <form onSubmit={submit}>
      <Field
        label="Course title"
        name="title"
        defaultValue={course?.title}
        minLength={5}
        maxLength={100}
        required
      />
      <Field
        label="Description"
        name="description"
        as="textarea"
        defaultValue={course?.description}
        minLength={20}
        maxLength={1000}
        required
      />
      <Field
        label="Subject"
        name="subject"
        as="select"
        defaultValue={course?.subject || ""}
        required
      >
        <option value="">Select a subject</option>
        {subjects.data?.results.map((subject) => (
          <option key={subject.id} value={subject.id}>
            {subject.name}
          </option>
        ))}
      </Field>
      <Field
        label="Publication"
        name="status"
        as="select"
        defaultValue={course?.status || "Draft"}
      >
        <option>Draft</option>
        <option>Published</option>
      </Field>
      <label className="choice">
        <input
          type="checkbox"
          checked={paid}
          onChange={(event) => setPaid(event.target.checked)}
        />
        Paid course
      </label>
      <Field
        label="Price in NPR"
        name="price_npr"
        type="number"
        min={paid ? "0.01" : "0"}
        step="0.01"
        defaultValue={course?.price_npr || "0"}
        disabled={!paid}
      />
      <Field
        label="Cover image (JPG/PNG, up to 2 MB)"
        name="cover"
        type="file"
        accept=".jpg,.jpeg,.png"
      />
      <button>Save course</button>
    </form>
  );
}

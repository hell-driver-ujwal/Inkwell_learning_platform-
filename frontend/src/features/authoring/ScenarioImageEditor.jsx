/** Images are uploaded separately after a scenario's steps have been saved. */
import { useState } from "react";
import { api } from "../../api/client";
import Field from "../../components/Field";
import { ErrorMessage, Notice } from "../../components/Feedback";
export default function ScenarioImageEditor({ activity, steps, reload }) {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function save(event) {
    event.preventDefault();
    const body = new FormData(event.currentTarget);
    if (!body.get("image")?.size) body.delete("image");
    try {
      await api(`author/activities/${activity.id}/step-image/`, {
        method: "POST",
        body,
      });
      setMessage("Step image updated.");
      reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <details>
      <summary>Scenario step images</summary>
      <p>
        Save your steps first, then attach an image. Images are locked after
        attempts.
      </p>
      <ErrorMessage>{error}</ErrorMessage>
      <Notice>{message}</Notice>
      <form onSubmit={save}>
        <Field label="Saved step" name="step_id" as="select" required>
          <option value="">Choose step</option>
          {steps
            .filter((step) => /^\d+$/.test(step.key))
            .map((step, index) => (
              <option key={step.key} value={step.key}>
                Step {index + 1}: {step.text.slice(0, 50)}
              </option>
            ))}
        </Field>
        <Field
          label="Image"
          type="file"
          name="image"
          accept=".jpg,.jpeg,.png,.gif"
        />
        <Field
          label="Alternative text"
          name="image_alt"
          minLength={5}
          maxLength={150}
        />
        <label className="choice">
          <input name="remove" type="checkbox" value="true" />
          Remove the current image
        </label>
        <button>Save image</button>
      </form>
      {steps
        .filter((step) => step.image_url)
        .map((step) => (
          <figure key={step.key}>
            <img
              className="lesson-image"
              src={step.image_url}
              alt={step.image_alt}
            />
            <figcaption>{step.text}</figcaption>
          </figure>
        ))}
    </details>
  );
}

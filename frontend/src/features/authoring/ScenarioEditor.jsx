/** A readable step-and-choice editor with named destinations. */
import Field from "../../components/Field";
export default function ScenarioEditor({ value, onChange }) {
  function updateStep(index, changes) {
    onChange({
      ...value,
      steps: value.steps.map((step, position) =>
        position === index ? { ...step, ...changes } : step,
      ),
    });
  }
  function updateChoice(index, changes) {
    onChange({
      ...value,
      choices: value.choices.map((choice, position) =>
        position === index ? { ...choice, ...changes } : choice,
      ),
    });
  }
  const options = value.steps.map((step, index) => (
    <option key={step.key} value={step.key}>
      Step {index + 1}: {step.text.slice(0, 50)}
    </option>
  ));
  return (
    <>
      <Field
        label="Start step"
        as="select"
        value={value.start_key}
        onChange={(event) =>
          onChange({ ...value, start_key: event.target.value })
        }
      >
        <option value="">Choose a step</option>
        {options}
      </Field>
      {value.steps.map((step, index) => (
        <section className="panel" key={step.key}>
          <Field
            label={`Step ${index + 1}`}
            as="textarea"
            value={step.text}
            onChange={(event) =>
              updateStep(index, { text: event.target.value })
            }
          />
          <label className="choice">
            <input
              type="checkbox"
              checked={step.is_ending}
              onChange={(event) =>
                updateStep(index, { is_ending: event.target.checked })
              }
            />
            Ending step
          </label>
          {step.is_ending && (
            <>
              <Field
                label="Outcome"
                as="select"
                value={step.outcome}
                onChange={(event) =>
                  updateStep(index, { outcome: event.target.value })
                }
              >
                <option value="">Choose outcome</option>
                <option>Best</option>
                <option>Acceptable</option>
                <option>Poor</option>
              </Field>
              <Field
                label="Feedback"
                as="textarea"
                value={step.feedback}
                onChange={(event) =>
                  updateStep(index, { feedback: event.target.value })
                }
              />
            </>
          )}
          <button
            type="button"
            className="text-button"
            onClick={() =>
              onChange({
                ...value,
                steps: value.steps.filter((_, position) => position !== index),
              })
            }
          >
            Remove step
          </button>
        </section>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange({
            ...value,
            steps: [
              ...value.steps,
              {
                key: crypto.randomUUID(),
                text: "",
                is_ending: false,
                outcome: "",
                feedback: "",
              },
            ],
          })
        }
      >
        Add step
      </button>
      <h3>Choices</h3>
      {value.choices.map((choice, index) => (
        <section className="panel" key={index}>
          <Field
            label="From step"
            as="select"
            value={choice.from_key}
            onChange={(event) =>
              updateChoice(index, { from_key: event.target.value })
            }
          >
            <option value="">Choose source</option>
            {options}
          </Field>
          <Field
            label="Choice text"
            value={choice.text}
            onChange={(event) =>
              updateChoice(index, { text: event.target.value })
            }
          />
          <Field
            label="Go to step"
            as="select"
            value={choice.next_key}
            onChange={(event) =>
              updateChoice(index, { next_key: event.target.value })
            }
          >
            <option value="">Choose destination</option>
            {options}
          </Field>
          <button
            type="button"
            className="text-button"
            onClick={() =>
              onChange({
                ...value,
                choices: value.choices.filter(
                  (_, position) => position !== index,
                ),
              })
            }
          >
            Remove choice
          </button>
        </section>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange({
            ...value,
            choices: [
              ...value.choices,
              { from_key: "", next_key: "", text: "" },
            ],
          })
        }
      >
        Add choice
      </button>
    </>
  );
}

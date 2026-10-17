/** Ordered confidence statements for self-assessment authoring. */
import Field from "../../components/Field";
export default function AssessmentEditor({ value, onChange }) {
  return (
    <>
      {value.map((statement, index) => (
        <div className="option-editor" key={index}>
          <Field
            label={`Statement ${index + 1}`}
            value={statement.text}
            onChange={(event) =>
              onChange(
                value.map((entry, position) =>
                  position === index
                    ? { ...entry, text: event.target.value }
                    : entry,
                ),
              )
            }
          />
          <button
            type="button"
            className="text-button"
            onClick={() =>
              onChange(value.filter((_, position) => position !== index))
            }
          >
            Remove
          </button>
        </div>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange([...value, { text: "", sort_order: value.length + 1 }])
        }
      >
        Add statement
      </button>
    </>
  );
}

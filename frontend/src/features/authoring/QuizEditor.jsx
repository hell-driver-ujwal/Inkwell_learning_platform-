/** Questions and options use ordinary form fields, not raw JSON editing. */
import Field from "../../components/Field";
export default function QuizEditor({ value, onChange }) {
  function updateQuestion(index, changes) {
    onChange(
      value.map((question, position) =>
        position === index ? { ...question, ...changes } : question,
      ),
    );
  }
  function updateOption(questionIndex, optionIndex, changes) {
    const options = value[questionIndex].options.map((option, position) =>
      position === optionIndex ? { ...option, ...changes } : option,
    );
    updateQuestion(questionIndex, { options });
  }
  return (
    <>
      {value.map((question, index) => (
        <section className="panel" key={index}>
          <Field
            label={`Question ${index + 1}`}
            value={question.text}
            onChange={(event) =>
              updateQuestion(index, { text: event.target.value })
            }
          />
          <Field
            label="Marks"
            type="number"
            min="1"
            max="10"
            value={question.marks}
            onChange={(event) =>
              updateQuestion(index, { marks: Number(event.target.value) })
            }
          />
          {question.options.map((option, optionIndex) => (
            <div className="option-editor" key={optionIndex}>
              <Field
                label={`Option ${optionIndex + 1}`}
                value={option.text}
                onChange={(event) =>
                  updateOption(index, optionIndex, { text: event.target.value })
                }
              />
              <label className="choice">
                <input
                  type="checkbox"
                  checked={option.is_correct}
                  onChange={(event) =>
                    updateOption(index, optionIndex, {
                      is_correct: event.target.checked,
                    })
                  }
                />
                Correct
              </label>
              <button
                type="button"
                className="text-button"
                onClick={() =>
                  updateQuestion(index, {
                    options: question.options.filter(
                      (_, position) => position !== optionIndex,
                    ),
                  })
                }
              >
                Remove option
              </button>
            </div>
          ))}
          <div className="actions">
            <button
              type="button"
              className="secondary"
              onClick={() =>
                updateQuestion(index, {
                  options: [
                    ...question.options,
                    { text: "", is_correct: false },
                  ],
                })
              }
            >
              Add option
            </button>
            <button
              type="button"
              className="danger"
              onClick={() =>
                onChange(value.filter((_, position) => position !== index))
              }
            >
              Remove question
            </button>
          </div>
        </section>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() =>
          onChange([
            ...value,
            {
              text: "",
              marks: 1,
              sort_order: value.length + 1,
              options: [
                { text: "", is_correct: true },
                { text: "", is_correct: false },
              ],
            },
          ])
        }
      >
        Add question
      </button>
    </>
  );
}

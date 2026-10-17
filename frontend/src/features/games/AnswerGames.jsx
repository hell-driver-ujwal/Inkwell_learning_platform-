/** Sort uses group choices; scramble and fill-blank use typed answers. */
import { useState } from "react";
import Field from "../../components/Field";
export default function AnswerGames({ activity, submit, busy }) {
  const [answers, setAnswers] = useState({});
  const template = activity.game_template;
  function send(event) {
    event.preventDefault();
    submit({
      game_answers: activity.items.map((item) => ({
        item_id: item.id,
        value: answers[item.id] || "",
      })),
    });
  }
  const options =
    template === "Sort"
      ? activity.groups.map((group) => ({
          value: String(group.id),
          label: group.name,
        }))
      : null;
  return (
    <form onSubmit={send}>
      {activity.items.map((item) => (
        <div className="game-item" key={item.id}>
          <h3>{template === "FillBlank" ? item.match_text : item.text}</h3>
          {template === "Scramble" && <p>Hint: {item.match_text}</p>}
          <Field
            label={
              template === "Scramble"
                ? "Unscramble the word"
                : template === "FillBlank"
                  ? "Missing word"
                  : "Your answer"
            }
            as={options ? "select" : "input"}
            required
            value={answers[item.id] || ""}
            onChange={(event) =>
              setAnswers({ ...answers, [item.id]: event.target.value })
            }
          >
            {options && (
              <>
                <option value="">Choose…</option>
                {options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </>
            )}
          </Field>
        </div>
      ))}
      <button disabled={busy}>Check my answers</button>
    </form>
  );
}

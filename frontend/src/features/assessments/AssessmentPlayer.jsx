/** Self-assessment is explicitly confidence-based, with no hidden correct answer. */
import { useState } from "react";
import Field from "../../components/Field";
export default function AssessmentPlayer({ activity, submit, busy }) {
  const [ratings, setRatings] = useState({});
  function send(event) {
    event.preventDefault();
    submit({
      ratings: activity.statements.map((statement) => ({
        statement_id: statement.id,
        rating: Number(ratings[statement.id]),
      })),
    });
  }
  return (
    <form onSubmit={send}>
      <p>Rate your confidence from 1 (not confident) to 5 (very confident).</p>
      {activity.statements.map((statement) => (
        <Field
          key={statement.id}
          label={statement.text}
          as="select"
          value={ratings[statement.id] || ""}
          required
          onChange={(event) =>
            setRatings({ ...ratings, [statement.id]: event.target.value })
          }
        >
          <option value="">Choose a rating</option>
          {[1, 2, 3, 4, 5].map((rating) => (
            <option key={rating}>{rating}</option>
          ))}
        </Field>
      ))}
      <button disabled={busy}>Save reflection</button>
    </form>
  );
}

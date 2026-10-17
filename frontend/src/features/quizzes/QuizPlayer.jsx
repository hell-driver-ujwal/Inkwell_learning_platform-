/** Quiz timing follows the server start time; answer keys arrive only after submission. */
import { useEffect, useState } from "react";
export default function QuizPlayer({ activity, run, submit, busy }) {
  const [answers, setAnswers] = useState({});
  const [remaining, setRemaining] = useState(null);
  useEffect(() => {
    if (!activity.time_limit_minutes) return;
    function tick() {
      setRemaining(
        Math.max(
          0,
          Math.ceil(
            (new Date(run.started_at).getTime() +
              activity.time_limit_minutes * 60000 -
              Date.now()) /
              1000,
          ),
        ),
      );
    }
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [activity.time_limit_minutes, run.started_at]);
  function send(event) {
    event.preventDefault();
    submit({
      answers: activity.questions.map((question) => ({
        question_id: question.id,
        option_id: answers[question.id] || null,
      })),
    });
  }
  return (
    <form onSubmit={send}>
      {remaining !== null && (
        <p className="timer" role="timer">
          Time remaining: {Math.floor(remaining / 60)}:
          {String(remaining % 60).padStart(2, "0")}{" "}
          {remaining === 0 &&
            "— submit now; a short server grace period applies."}
        </p>
      )}
      {activity.questions.map((question, index) => (
        <fieldset className="question" key={question.id}>
          <legend>
            {index + 1}. {question.text} <small>({question.marks} marks)</small>
          </legend>
          {question.options.map((option) => (
            <label className="choice" key={option.id}>
              <input
                type="radio"
                name={`question-${question.id}`}
                checked={answers[question.id] === option.id}
                onChange={() =>
                  setAnswers({ ...answers, [question.id]: option.id })
                }
              />
              {option.text}
            </label>
          ))}
        </fieldset>
      ))}
      <button disabled={busy}>Submit answers</button>
    </form>
  );
}

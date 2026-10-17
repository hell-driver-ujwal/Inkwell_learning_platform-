/** Submitted feedback is separate from the question-playing component. */
import { Link } from "react-router-dom";
export default function ActivityResult({ run }) {
  const result = run.result;
  return (
    <section className="result-panel">
      <span className="eyebrow">
        {run.preview ? "PREVIEW RESULT · NOT SAVED" : "YOUR RESULT"}
      </span>
      {result.score_percent !== undefined && <h2>{result.score_percent}%</h2>}
      {result.level && (
        <>
          <h2>{result.level}</h2>
          <p>Average confidence: {result.average} / 5</p>
        </>
      )}
      {result.outcome && <h2>{result.outcome} outcome</h2>}
      <p>{result.feedback}</p>
      {result.review?.map((question) => (
        <article className="question" key={question.question_id}>
          <h3>{question.text}</h3>
          <p>
            {question.selected_option === question.correct_option
              ? "Correct"
              : "Review this question"}
          </p>
          <ul>
            {question.options.map((option) => (
              <li key={option.id}>
                {option.text}{" "}
                {option.id === question.correct_option && "✓ Correct answer"}{" "}
                {option.id === question.selected_option && "(Your answer)"}
              </li>
            ))}
          </ul>
        </article>
      ))}
      {result.attempt_id && (
        <Link to={`/results/${result.attempt_id}`}>View saved result →</Link>
      )}
    </section>
  );
}

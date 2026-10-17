/** Aggregate quiz/game scores, confidence and outcomes without mixing their meanings. */
import { useResource } from "../../hooks/useResource";
import { ResourceState } from "../../components/Feedback";
export default function ResultsSummary({ query }) {
  const resource = useResource(`attempts/summary/?${query}`);
  return (
    <details>
      <summary>Scores, confidence and outcome summaries</summary>
      <ResourceState resource={resource}>
        {(data) => (
          <>
            <h2>Quiz & game scores</h2>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Activity / learner</th>
                    <th>Attempts</th>
                    <th>Best</th>
                    <th>Average</th>
                    <th>Latest</th>
                  </tr>
                </thead>
                <tbody>
                  {data.scores.map((row) => (
                    <tr key={`${row.activity_id}-${row.learner_id}`}>
                      <td>
                        {row.activity__title}
                        <small>{row.learner__full_name}</small>
                      </td>
                      <td>{row.attempt_count}</td>
                      <td>{row.best_score}%</td>
                      <td>{Number(row.average_score).toFixed(2)}%</td>
                      <td>{row.latest_score}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h2>Confidence by statement</h2>
            {data.confidence.map((row, index) => (
              <p key={index}>
                {row.statement__text}:{" "}
                <b>{Number(row.average_rating).toFixed(2)} / 5</b> (
                {row.response_count} responses)
              </p>
            ))}
            <h2>Scenario outcomes</h2>
            {data.endings.map((row, index) => (
              <p key={index}>
                {row.activity__title} · {row.ending_step__outcome}:{" "}
                {row.attempt_count} · {row.ending_step__text}
              </p>
            ))}
          </>
        )}
      </ResourceState>
    </details>
  );
}

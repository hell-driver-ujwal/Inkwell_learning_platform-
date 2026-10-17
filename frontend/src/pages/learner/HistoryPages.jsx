/** Course, bookmark and attempt history with explicit navigation. */
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import ResultsSummary from "../../features/activities/ResultsSummary";
import ResultsFilters from "../../features/activities/ResultsFilters";
import CourseCard from "../../components/CourseCard";
export function MyCoursesPage() {
  const resource = useResource("my-courses/", { all: true });
  return (
    <>
      <h1>My courses</h1>
      <ResourceState resource={resource}>
        {(data) => (
          <div className="course-grid">
            {data.results.map((course) => (
              <CourseCard course={course} key={course.id} />
            ))}
            {!data.count && (
              <p>
                Your first course is waiting.{" "}
                <Link to="/courses">Explore the library.</Link>
              </p>
            )}
          </div>
        )}
      </ResourceState>
    </>
  );
}
export function BookmarksPage() {
  const resource = useResource("bookmarks/", { all: true });
  const [error, setError] = useState("");
  async function remove(materialId) {
    try {
      await api(`materials/${materialId}/bookmark/`, { method: "DELETE" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <h1>Saved for later</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <ResourceState resource={resource}>
        {(data) => (
          <ul className="record-list">
            {data.results.map((bookmark) => (
              <li key={bookmark.id}>
                <Link to={`/lessons/${bookmark.material}`}>
                  {bookmark.title}
                </Link>
                <small>{bookmark.course_title}</small>
                <button
                  className="text-button"
                  onClick={() => remove(bookmark.material)}
                >
                  Remove bookmark
                </button>
              </li>
            ))}
            {!data.count && <li>No bookmarks yet.</li>}
          </ul>
        )}
      </ResourceState>
    </>
  );
}
export function ResultsPage() {
  const [params, setParams] = useSearchParams();
  const resource = useResource(`attempts/?${params}`);
  return (
    <>
      <h1>Learning history</h1>
      <p>Every practice session is a step forward.</p>
      <ResultsFilters params={params} setParams={setParams} />
      <ResultsSummary query={params.toString()} />
      <ResourceState resource={resource}>
        {(data) => (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Activity</th>
                    <th>Learner</th>
                    <th>Result</th>
                    <th>Submitted</th>
                  </tr>
                </thead>
                <tbody>
                  {data.results.map((attempt) => (
                    <tr key={attempt.id}>
                      <td>
                        <Link to={`/results/${attempt.id}`}>
                          {attempt.activity_title}
                        </Link>
                        <small>{attempt.kind}</small>
                      </td>
                      <td>{attempt.learner_name}</td>
                      <td>
                        {attempt.score_percent !== null
                          ? `${attempt.score_percent}%`
                          : attempt.outcome || "Reflection"}
                      </td>
                      <td>{new Date(attempt.submitted_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="actions">
              {data.previous && (
                <button
                  onClick={() =>
                    setParams({
                      ...Object.fromEntries(params),
                      page: Number(params.get("page")) - 1,
                    })
                  }
                >
                  Previous
                </button>
              )}
              {data.next && (
                <button
                  onClick={() =>
                    setParams({
                      ...Object.fromEntries(params),
                      page: Number(params.get("page") || 1) + 1,
                    })
                  }
                >
                  Next
                </button>
              )}
            </div>
          </>
        )}
      </ResourceState>
    </>
  );
}
export function ResultDetailPage() {
  const { id } = useParams();
  const resource = useResource(`attempts/${id}/`);
  return (
    <ResourceState resource={resource}>
      {(attempt) => (
        <>
          <Link to="/results">← Learning history</Link>
          <h1>{attempt.activity_title}</h1>
          <p>
            {attempt.learner_name} ·{" "}
            {new Date(attempt.submitted_at).toLocaleString()}
          </p>
          <h2>
            {attempt.score_percent !== null
              ? `${attempt.score_percent}%`
              : attempt.outcome || "Self reflection"}
          </h2>
          {attempt.review.map((question, index) => (
            <section className="question" key={index}>
              <h3>{question.text}</h3>
              <ul>
                {question.options.map((option) => (
                  <li key={option.id}>
                    {option.text} {option.is_correct && "✓ Correct answer"}{" "}
                    {question.selected_option === option.id && "(Your answer)"}
                  </li>
                ))}
              </ul>
            </section>
          ))}
          <p>{attempt.ending_feedback}</p>
          {attempt.confidence_comparison?.map((row, index) => (
            <p key={`comparison-${index}`}>
              {row.statement}: {row.rating}/5 · Previous:{" "}
              {row.previous_rating ?? "First reflection"}
            </p>
          ))}
          {attempt.ratings.map((rating, index) => (
            <p key={index}>
              {rating.statement__text}: <strong>{rating.rating}/5</strong>
            </p>
          ))}
        </>
      )}
    </ResourceState>
  );
}
export function CertificatePage() {
  const { id } = useParams();
  const resource = useResource(`courses/${id}/certificate/`);
  return (
    <ResourceState resource={resource}>
      {(certificate) => (
        <>
          <article className="certificate">
            <span className="brand">inkwell</span>
            <p className="eyebrow">CERTIFICATE OF COMPLETION</p>
            <h1>{certificate.learner}</h1>
            <p>has completed all published lessons and activities in</p>
            <h2>{certificate.course}</h2>
            <p>Course author: {certificate.teacher}</p>
            <small>{certificate.certificate_id}</small>
          </article>
          <button className="no-print" onClick={() => window.print()}>
            Print certificate
          </button>
        </>
      )}
    </ResourceState>
  );
}

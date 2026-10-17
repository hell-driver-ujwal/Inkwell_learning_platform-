/** Dashboard content is scoped by the backend to the authenticated role. */
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useResource } from "../../hooks/useResource";
import { ResourceState } from "../../components/Feedback";
export default function DashboardPage() {
  const { user } = useAuth();
  const resource = useResource("dashboard/");
  return (
    <>
      <span className="eyebrow">YOUR LEARNING WORKSPACE</span>
      <h1>Hello, {user.full_name.split(" ")[0]}.</h1>
      <p className="lead">A little progress, every day.</p>
      <ResourceState resource={resource}>
        {(data) => (
          <>
            <div className="stats">
              <div>
                <strong>{data.course_count}</strong>
                <span>Courses</span>
              </div>
              <div>
                <strong>{data.attempt_count}</strong>
                <span>Learning attempts</span>
              </div>
              <div>
                <strong>{data.streak ?? data.learner_count}</strong>
                <span>
                  {data.streak !== undefined ? "Day streak" : "Learners"}
                </span>
              </div>
              <div>
                <strong>{data.attempts_this_week}</strong>
                <span>Attempts this week</span>
              </div>
            </div>
            {data.courses && (
              <section>
                <h2>Keep your momentum</h2>
                {data.courses.map((course) => (
                  <article className="progress-row" key={course.id}>
                    <div>
                      <Link to={`/courses/${course.id}`}>
                        <h3>{course.title}</h3>
                      </Link>
                      <p>
                        {course.progress.completed} of {course.progress.total}{" "}
                        items completed
                      </p>
                    </div>
                    <div>
                      <progress max="100" value={course.progress.percent} />
                      <p>{course.progress.percent}%</p>
                    </div>
                  </article>
                ))}
              </section>
            )}
            {data.pending_teachers !== undefined && (
              <p>
                <Link to="/admin/users">
                  {data.pending_teachers} lecturer applications awaiting review
                  →
                </Link>
              </p>
            )}
            <div className="actions">
              <Link
                className="button"
                to={user.role === "Learner" ? "/courses" : "/author/courses"}
              >
                {user.role === "Learner"
                  ? "Explore more courses"
                  : "Open course studio"}
              </Link>
              <Link to="/results">Recent results →</Link>
            </div>
          </>
        )}
      </ResourceState>
    </>
  );
}

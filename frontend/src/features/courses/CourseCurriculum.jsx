/** Course outline uses server-issued access flags and completion IDs. */
import { Link } from "react-router-dom";
export default function CourseCurriculum({ course }) {
  const canOpen = course.can_study || course.can_preview;
  return (
    <section>
      <h2>Inside this course</h2>
      {course.topics.map((topic, index) => (
        <section className="topic" key={topic.id}>
          <h3>
            <span>{String(index + 1).padStart(2, "0")}</span>
            {topic.title}
          </h3>
          <ul className="curriculum">
            {topic.materials.map((material) => (
              <li key={`m${material.id}`}>
                <span>
                  {course.progress?.materials.includes(material.id) ? "✓" : "○"}
                </span>
                {canOpen || material.is_preview ? (
                  <Link to={`/lessons/${material.id}`}>{material.title}</Link>
                ) : (
                  <span>{material.title}</span>
                )}
                <small>
                  {material.is_preview ? "Free preview" : material.kind}
                </small>
              </li>
            ))}
            {topic.activities.map((activity) => (
              <li key={`a${activity.id}`}>
                <span>
                  {course.progress?.activities.includes(activity.id)
                    ? "✓"
                    : "○"}
                </span>
                {canOpen ? (
                  <Link
                    to={`/activities/${activity.id}${course.can_preview ? "?preview=1" : ""}`}
                  >
                    {activity.title}
                  </Link>
                ) : (
                  <span>{activity.title}</span>
                )}
                <small>{activity.game_template || activity.kind}</small>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </section>
  );
}

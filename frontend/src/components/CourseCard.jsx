/** A reusable catalogue card with clear free/paid labeling. */
import { Link } from "react-router-dom";
export default function CourseCard({ course }) {
  return (
    <article className="course-card">
      <Link to={`/courses/${course.id}`} tabIndex={-1} aria-hidden="true">
        {course.cover_url ? (
          <img src={course.cover_url} alt="" />
        ) : (
          <div className="cover-placeholder">Inkwell</div>
        )}
      </Link>
      <div className="card-body">
        <span className="eyebrow">{course.subject_name}</span>
        <h2>
          <Link to={`/courses/${course.id}`}>{course.title}</Link>
        </h2>
        <p className="muted">{course.teacher_name}</p>
        <p>{course.description.slice(0, 145)}…</p>
        <div className="card-footer">
          <strong>
            {course.is_paid ? `NPR ${course.price_npr}` : "Free course"}
          </strong>
          <Link to={`/courses/${course.id}`}>Explore →</Link>
        </div>
      </div>
    </article>
  );
}

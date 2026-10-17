/** Course introduction and enrollment decisions stay separate from curriculum rendering. */
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useResource } from "../../hooks/useResource";
import { useAuth } from "../../context/AuthContext";
import { enroll, leave } from "../../api/courses";
import { api } from "../../api/client";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import CourseCurriculum from "../../features/courses/CourseCurriculum";
import CourseReviews from "../../features/courses/CourseReviews";
export default function CourseDetailPage() {
  const { id } = useParams();
  const resource = useResource(`courses/${id}/`);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function join(course) {
    try {
      await enroll(id);
      resource.reload();
    } catch (failure) {
      if (course.is_paid && failure.message.includes("payment")) {
        try {
          const payment = await api("payments/checkout/", {
            method: "POST",
            body: { course_id: Number(id) },
          });
          navigate(`/payments/${payment.id}`);
        } catch (paymentError) {
          setError(paymentError.message);
        }
      } else setError(failure.message);
    }
  }
  async function leaveCourse() {
    try {
      await leave(id);
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <ResourceState resource={resource}>
      {(course) => (
        <>
          <Link to="/courses">← Course library</Link>
          <div className="course-intro">
            <div>
              <span className="eyebrow">{course.subject_name}</span>
              <h1>{course.title}</h1>
              <p className="lead">{course.description}</p>
              <p>
                With <b>{course.teacher_name}</b>
              </p>
              <ErrorMessage>{error}</ErrorMessage>
              {course.can_study ? (
                <>
                  <p>Your progress: {course.progress.percent}%</p>
                  <progress value={course.progress.percent} max="100" />
                  <div className="actions">
                    <button className="secondary" onClick={leaveCourse}>
                      Leave course
                    </button>
                    {Number(course.progress.percent) === 100 && (
                      <Link to={`/courses/${id}/certificate`}>
                        View certificate →
                      </Link>
                    )}
                  </div>
                </>
              ) : user?.role === "Learner" ? (
                <button onClick={() => join(course)}>
                  {course.is_paid
                    ? `Buy with eSewa · NPR ${course.price_npr}`
                    : "Enroll for free"}
                </button>
              ) : (
                !user && (
                  <Link className="button" to="/login/Learner">
                    Log in to enroll
                  </Link>
                )
              )}
              {course.can_preview && (
                <p className="notice">
                  Author preview — practice here does not create learner
                  results.
                </p>
              )}
            </div>
            {course.cover_url && (
              <img className="course-cover" src={course.cover_url} alt="" />
            )}
          </div>
          <CourseCurriculum course={course} />
          <CourseReviews course={course} reload={resource.reload} />
        </>
      )}
    </ResourceState>
  );
}

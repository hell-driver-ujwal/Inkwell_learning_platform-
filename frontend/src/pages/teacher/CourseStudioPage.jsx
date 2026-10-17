/** Lecturer-owned course list and a conventional course creation form. */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import CourseForm from "../../features/authoring/CourseForm";
export default function CourseStudioPage() {
  const resource = useResource("author/courses/", { all: true });
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function create(body) {
    try {
      const course = await api("author/courses/", { method: "POST", body });
      navigate(`/author/courses/${course.id}`);
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <span className="eyebrow">LECTURER STUDIO</span>
      <h1>Make room for understanding.</h1>
      <ResourceState resource={resource}>
        {(data) => (
          <ul className="record-list">
            {data.results.map((course) => (
              <li key={course.id}>
                <Link to={`/author/courses/${course.id}`}>{course.title}</Link>
                <span>
                  {course.status} ·{" "}
                  {course.is_paid ? `NPR ${course.price_npr}` : "Free"}
                </span>
              </li>
            ))}
          </ul>
        )}
      </ResourceState>
      <details>
        <summary>Create a course</summary>
        <ErrorMessage>{error}</ErrorMessage>
        <CourseForm save={create} />
      </details>
    </>
  );
}

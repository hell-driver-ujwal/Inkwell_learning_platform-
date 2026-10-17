/** Learner navigation includes activities in the same order as course progress. */
import { Link } from "react-router-dom";
import { useResource } from "../../hooks/useResource";
import CourseCurriculum from "../courses/CourseCurriculum";
export default function LessonNavigation({ lesson }) {
  const resource = useResource(`courses/${lesson.course_id}/`);
  const course = resource.data;
  if (!course || (!course.can_study && !course.can_preview)) return null;
  const items = course.topics.flatMap((topic) => [
    ...topic.materials.map((material) => ({
      ...material,
      path: `/lessons/${material.id}`,
      isLesson: true,
    })),
    ...(course.can_study
      ? topic.activities.map((activity) => ({
          ...activity,
          path: `/activities/${activity.id}`,
          isLesson: false,
        }))
      : []),
  ]);
  const index = items.findIndex(
    (item) => item.isLesson && item.id === lesson.id,
  );
  return (
    <>
      <nav className="actions" aria-label="Lesson navigation">
        {index > 0 && (
          <Link to={items[index - 1].path}>
            ← Previous: {items[index - 1].title}
          </Link>
        )}
        {index >= 0 && index < items.length - 1 && (
          <Link to={items[index + 1].path}>
            Next: {items[index + 1].title} →
          </Link>
        )}
      </nav>
      <details>
        <summary>Course outline</summary>
        <CourseCurriculum course={course} />
      </details>
    </>
  );
}

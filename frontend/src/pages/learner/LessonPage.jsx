/** Authorized lesson reader; rendering, actions and navigation have separate responsibilities. */
import { Link, useParams } from "react-router-dom";
import { useResource } from "../../hooks/useResource";
import { ResourceState } from "../../components/Feedback";
import LessonContent from "../../features/lessons/LessonContent";
import LessonActions from "../../features/lessons/LessonActions";
import LessonNavigation from "../../features/lessons/LessonNavigation";
export default function LessonPage() {
  const { id } = useParams();
  const resource = useResource(`materials/${id}/`);
  return (
    <ResourceState resource={resource}>
      {(lesson) => (
        <>
          <Link to={`/courses/${lesson.course_id}`}>← Back to course</Link>
          <span className="eyebrow">{lesson.kind} LESSON</span>
          <h1>{lesson.title}</h1>
          <LessonContent key={lesson.id} lesson={lesson} />
          <LessonActions lesson={lesson} reload={resource.reload} />
          <LessonNavigation lesson={lesson} />
        </>
      )}
    </ResourceState>
  );
}

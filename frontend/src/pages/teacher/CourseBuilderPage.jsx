/** Course builder coordinates separate topic, lesson and activity editors. */
import { useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, Notice, ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
import CourseForm from "../../features/authoring/CourseForm";
function TopicPanel({ topic, reload, reportError }) {
  const lessons = useResource(`author/materials/?topic=${topic.id}`, {
    all: true,
  });
  const activities = useResource(`author/activities/?topic=${topic.id}`, {
    all: true,
  });
  async function save(event) {
    event.preventDefault();
    try {
      await api(`author/topics/${topic.id}/`, {
        method: "PATCH",
        body: Object.fromEntries(new FormData(event.currentTarget)),
      });
      reload();
    } catch (failure) {
      reportError(failure.message);
    }
  }
  async function remove(path) {
    if (
      !window.confirm(
        "Delete this content? Existing learning history may prevent deletion.",
      )
    )
      return;
    try {
      await api(path, { method: "DELETE" });
      reload();
      lessons.reload();
      activities.reload();
    } catch (failure) {
      reportError(failure.message);
    }
  }
  return (
    <section className="topic">
      <h2>{topic.title}</h2>
      <details>
        <summary>Edit topic</summary>
        <form onSubmit={save}>
          <Field
            label="Title"
            name="title"
            defaultValue={topic.title}
            minLength={3}
            required
          />
          <Field
            label="Order"
            name="sort_order"
            type="number"
            min="1"
            max="100"
            defaultValue={topic.sort_order}
          />
          <div className="actions">
            <button>Save topic</button>
            <button
              type="button"
              className="danger"
              onClick={() => remove(`author/topics/${topic.id}/`)}
            >
              Delete topic
            </button>
          </div>
        </form>
      </details>
      <ul className="record-list">
        {lessons.data?.results.map((lesson) => (
          <li key={lesson.id}>
            <Link to={`/author/lessons/${lesson.id}?topic=${topic.id}`}>
              {lesson.title}
            </Link>
            <span>
              {lesson.kind} · {lesson.status}
            </span>
            <button
              className="text-button"
              onClick={() => remove(`author/materials/${lesson.id}/`)}
            >
              Delete
            </button>
          </li>
        ))}
        {activities.data?.results.map((activity) => (
          <li key={activity.id}>
            <Link to={`/author/activities/${activity.id}?topic=${topic.id}`}>
              {activity.title}
            </Link>
            <span>
              {activity.kind} · {activity.status}
            </span>
            <button
              className="text-button"
              onClick={() => remove(`author/activities/${activity.id}/`)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
      <div className="actions">
        <Link to={`/author/lessons/new?topic=${topic.id}`}>+ Add lesson</Link>
        <Link to={`/author/activities/new?topic=${topic.id}`}>
          + Add activity
        </Link>
      </div>
    </section>
  );
}
export default function CourseBuilderPage() {
  const { id } = useParams();
  const course = useResource(`author/courses/${id}/`);
  const topics = useResource(`author/topics/?course=${id}`, { all: true });
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function saveCourse(body) {
    try {
      await api(`author/courses/${id}/`, { method: "PATCH", body });
      course.reload();
      setMessage("Course saved.");
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function addTopic(event) {
    event.preventDefault();
    const form = event.currentTarget;
    try {
      await api("author/topics/", {
        method: "POST",
        body: { ...Object.fromEntries(new FormData(form)), course: Number(id) },
      });
      topics.reload();
      form.reset();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function deleteCourse() {
    if (!window.confirm("Delete this course and its content?")) return;
    try {
      await api(`author/courses/${id}/`, { method: "DELETE" });
      navigate("/author/courses");
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <Link to="/author/courses">← Course studio</Link>
      <ErrorMessage>{error}</ErrorMessage>
      <Notice>{message}</Notice>
      <ResourceState resource={course}>
        {(data) => (
          <>
            <h1>{data.title}</h1>
            <div className="actions">
              <Link to={`/courses/${id}`}>Preview course →</Link>
              <Link to={`/author/courses/${id}/learners`}>
                Learners and progress →
              </Link>
              <Link to={`/results?activity__topic__course=${id}`}>
                Results →
              </Link>
            </div>
            <details>
              <summary>Course settings</summary>
              <CourseForm course={data} save={saveCourse} />
              <button className="danger" onClick={deleteCourse}>
                Delete course
              </button>
            </details>
          </>
        )}
      </ResourceState>
      <ResourceState resource={topics}>
        {(data) =>
          data.results.map((topic) => (
            <TopicPanel
              key={topic.id}
              topic={topic}
              reload={topics.reload}
              reportError={setError}
            />
          ))
        }
      </ResourceState>
      <section className="panel">
        <h2>Add a topic</h2>
        <form onSubmit={addTopic}>
          <Field label="Topic title" name="title" minLength={3} required />
          <Field
            label="Order"
            name="sort_order"
            type="number"
            min="1"
            max="100"
            defaultValue="1"
          />
          <button>Add topic</button>
        </form>
      </section>
    </>
  );
}
export function CourseLearnersPage() {
  const { id } = useParams();
  const resource = useResource(`author/courses/${id}/learners/`);
  return (
    <>
      <h1>Learners and progress</h1>
      <ResourceState resource={resource}>
        {(data) =>
          data.map((learner) => (
            <article className="progress-row" key={learner.id}>
              <b>{learner.name}</b>
              <progress max="100" value={learner.progress.percent} />
              <span>{learner.progress.percent}%</span>
            </article>
          ))
        }
      </ResourceState>
    </>
  );
}

/** Load and save structured content through its dedicated domain editor. */
import { useEffect, useState } from "react";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, Notice, Loading } from "../../components/Feedback";
import ScenarioImageEditor from "./ScenarioImageEditor";
import QuizEditor from "./QuizEditor";
import AssessmentEditor from "./AssessmentEditor";
import GameEditor from "./GameEditor";
import ScenarioEditor from "./ScenarioEditor";
export default function ActivityContentEditor({ activity }) {
  const resource = useResource(`author/activities/${activity.id}/content/`);
  const [content, setContent] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (resource.data) setContent(resource.data);
  }, [resource.data]);
  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      setContent(
        await api(`author/activities/${activity.id}/content/`, {
          method: "PUT",
          body: content,
        }),
      );
      setMessage("Content saved.");
    } catch (failure) {
      setError(failure.message);
    }
  }
  if (resource.error) return <ErrorMessage>{resource.error}</ErrorMessage>;
  if (content === null) return <Loading />;
  return (
    <>
      {" "}
      <form onSubmit={save}>
        <h2>Activity content</h2>
        <p className="muted">
          Save drafts while building. Published activities must remain valid;
          content locks after the first learner attempt.
        </p>
        <ErrorMessage>{error}</ErrorMessage>
        <Notice>{message}</Notice>
        {activity.kind === "Quiz" && (
          <QuizEditor value={content} onChange={setContent} />
        )}
        {activity.kind === "SelfAssessment" && (
          <AssessmentEditor value={content} onChange={setContent} />
        )}
        {activity.kind === "Game" && (
          <GameEditor
            value={content}
            onChange={setContent}
            template={activity.game_template}
          />
        )}
        {activity.kind === "Scenario" && (
          <ScenarioEditor value={content} onChange={setContent} />
        )}
        <div className="actions">
          <button>Save content</button>
        </div>
      </form>
      {activity.kind === "Scenario" && (
        <ScenarioImageEditor
          activity={activity}
          steps={content.steps}
          reload={resource.reload}
        />
      )}{" "}
    </>
  );
}

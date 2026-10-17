/** Coordinate start/submit requests; each domain owns its own interaction component. */
import { useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import { useResource } from "../../hooks/useResource";
import {
  startActivity,
  submitActivity,
  moveScenario,
} from "../../api/activities";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import QuizPlayer from "../../features/quizzes/QuizPlayer";
import AssessmentPlayer from "../../features/assessments/AssessmentPlayer";
import GamePlayer from "../../features/games/GamePlayer";
import ScenarioPlayer from "../../features/scenarios/ScenarioPlayer";
import ActivityResult from "../../features/activities/ActivityResult";
import Discussion from "../../features/discussions/Discussion";
function ActivitySession({ activity, preview }) {
  const [run, setRun] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function perform(operation) {
    setBusy(true);
    setError("");
    try {
      setRun(await operation());
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }
  const submit = (body) =>
    perform(() => submitActivity(activity.id, { ...body, run_id: run.id }));
  const move = (body) =>
    perform(() =>
      moveScenario(activity.id, {
        ...body,
        run_id: run.id,
        step_version: run.step_version,
      }),
    );
  const start = () => perform(() => startActivity(activity.id, preview));
  if (activity.kind === "Discussion") return <Discussion activity={activity} />;
  return (
    <>
      <ErrorMessage>{error}</ErrorMessage>
      {preview && (
        <p className="notice">
          Preview mode: no learner attempt or progress will be recorded.
        </p>
      )}
      {!run ? (
        <>
          <p>
            {activity.time_limit_minutes
              ? `${activity.time_limit_minutes} minute timer.`
              : "Work at your own pace."}{" "}
            {activity.max_attempts
              ? `Maximum ${activity.max_attempts} attempts.`
              : "Unlimited attempts."}
          </p>
          <button disabled={busy} onClick={start}>
            Start{" "}
            {activity.kind === "SelfAssessment"
              ? "reflection"
              : activity.kind.toLowerCase()}
          </button>
        </>
      ) : run.finished ? (
        <>
          <ActivityResult run={run} />
          <button className="secondary" onClick={start}>
            Try again
          </button>
        </>
      ) : (
        <>
          {activity.kind === "Quiz" && (
            <QuizPlayer
              activity={activity}
              run={run}
              submit={submit}
              busy={busy}
            />
          )}
          {activity.kind === "Game" && (
            <GamePlayer activity={activity} submit={submit} busy={busy} />
          )}
          {activity.kind === "SelfAssessment" && (
            <AssessmentPlayer activity={activity} submit={submit} busy={busy} />
          )}
          {activity.kind === "Scenario" && (
            <ScenarioPlayer run={run} move={move} busy={busy} />
          )}
        </>
      )}
    </>
  );
}
export default function ActivityPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const preview = params.get("preview") === "1";
  const resource = useResource(
    `activities/${id}/${preview ? "?preview=1" : ""}`,
  );
  return (
    <ResourceState resource={resource}>
      {(activity) => (
        <>
          <Link to="/courses">← Course library</Link>
          <span className="eyebrow">
            {activity.game_template || activity.kind}
          </span>
          <h1>{activity.title}</h1>
          <p className="lead">{activity.description}</p>
          <ActivitySession
            key={activity.id}
            activity={activity}
            preview={preview}
          />
        </>
      )}
    </ResourceState>
  );
}

/** Only choices for the current server-selected scenario step are displayed. */
export default function ScenarioPlayer({ run, move, busy }) {
  const step = run.step;
  if (!step) return <p>This scenario has no start step.</p>;
  return (
    <section className="panel">
      <span className="eyebrow">YOUR NEXT DECISION</span>
      <h2>{step.text}</h2>
      {step.image_url && (
        <img
          className="lesson-image"
          src={step.image_url}
          alt={step.image_alt}
        />
      )}
      {step.is_ending ? (
        <>
          <h3>{step.outcome} outcome</h3>
          <p>{step.feedback}</p>
          {!run.finished && (
            <button disabled={busy} onClick={() => move({ finish: true })}>
              Finish scenario
            </button>
          )}
        </>
      ) : (
        <div className="scenario-choices">
          {step.choices.map((choice) => (
            <button
              className="secondary"
              disabled={busy}
              key={choice.id}
              onClick={() => move({ choice_id: choice.id })}
            >
              {choice.text} →
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

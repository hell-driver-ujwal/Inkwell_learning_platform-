/** The original speed round gives twelve seconds per statement. */
import { useEffect, useState } from "react";
export default function TrueFalseGame({ items, submit, busy }) {
  const [answers, setAnswers] = useState([]);
  const [seconds, setSeconds] = useState(12);
  const index = answers.length;
  const item = items[index];
  useEffect(() => {
    if (!item) return;
    setSeconds(12);
    const deadline = Date.now() + 12000;
    const timer = setInterval(() => {
      const left = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
      setSeconds(left);
      if (left === 0) {
        clearInterval(timer);
        setAnswers((current) =>
          current.length === index
            ? [...current, { item_id: item.id, value: "Skip" }]
            : current,
        );
      }
    }, 100);
    return () => clearInterval(timer);
  }, [index, item]);
  function choose(value) {
    setAnswers((current) =>
      current.length === index
        ? [...current, { item_id: item.id, value }]
        : current,
    );
  }
  if (!item)
    return (
      <section className="panel">
        <h2>Round complete.</h2>
        <p>Submit to see your server-checked score.</p>
        <button
          disabled={busy}
          onClick={() => submit({ game_answers: answers })}
        >
          Save speed-round result
        </button>
      </section>
    );
  return (
    <section className="flashcard">
      <p>
        Statement {index + 1} of {items.length} · {seconds} seconds remaining
      </p>
      <progress max="12" value={seconds} />
      <h2>{item.match_text}</h2>
      <div className="actions">
        <button onClick={() => choose("True")}>True</button>
        <button className="secondary" onClick={() => choose("False")}>
          False
        </button>
      </div>
    </section>
  );
}

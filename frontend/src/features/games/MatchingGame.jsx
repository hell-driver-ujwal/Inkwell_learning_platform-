/** Match a prompt to its counterpart using keyboard-accessible buttons. */
import { useState } from "react";
export default function MatchingGame({ items, targets, submit, busy }) {
  const [selected, setSelected] = useState(null);
  const [matched, setMatched] = useState([]);
  const [feedback, setFeedback] = useState(
    "Choose a prompt, then its matching answer.",
  );
  function match(target) {
    if (!selected) return;
    if (selected === target.id) {
      setMatched([...matched, selected]);
      setSelected(null);
      setFeedback("Correct match. Keep going.");
    } else setFeedback("Not quite. Try another match.");
  }
  return (
    <section>
      <p role="status">{feedback}</p>
      <p>
        {matched.length} of {items.length} pairs matched
      </p>
      <div className="matching-board">
        <div>
          {items.map((item) => (
            <button
              className={selected === item.id ? "" : "secondary"}
              key={item.id}
              disabled={matched.includes(item.id)}
              onClick={() => setSelected(item.id)}
              aria-pressed={selected === item.id}
            >
              {item.text}
              {matched.includes(item.id) && " ✓"}
            </button>
          ))}
        </div>
        <div>
          {targets.map((target) => (
            <button
              className="secondary"
              key={target.id}
              disabled={matched.includes(target.id)}
              onClick={() => match(target)}
            >
              {target.text}
              {matched.includes(target.id) && " ✓"}
            </button>
          ))}
        </div>
      </div>
      {matched.length === items.length && (
        <button
          disabled={busy}
          onClick={() =>
            submit({
              game_answers: items.map((item) => ({
                item_id: item.id,
                value: String(item.id),
              })),
            })
          }
        >
          Save matching result
        </button>
      )}
    </section>
  );
}

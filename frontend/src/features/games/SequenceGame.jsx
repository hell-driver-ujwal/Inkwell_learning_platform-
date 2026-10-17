/** Learners order steps with arrow controls instead of typing positions. */
import { useState } from "react";
export default function SequenceGame({ items, submit, busy }) {
  const [ordered, setOrdered] = useState(items);
  function move(index, offset) {
    const next = [...ordered];
    const destination = index + offset;
    [next[index], next[destination]] = [next[destination], next[index]];
    setOrdered(next);
  }
  return (
    <section>
      <p>Move each step into the correct order.</p>
      <ol className="sequence-list">
        {ordered.map((item, index) => (
          <li key={item.id}>
            <span>{item.text}</span>
            <div className="actions">
              <button
                className="secondary"
                disabled={index === 0}
                aria-label={`Move ${item.text} up`}
                onClick={() => move(index, -1)}
              >
                ↑
              </button>
              <button
                className="secondary"
                disabled={index === ordered.length - 1}
                aria-label={`Move ${item.text} down`}
                onClick={() => move(index, 1)}
              >
                ↓
              </button>
            </div>
          </li>
        ))}
      </ol>
      <button
        disabled={busy}
        onClick={() =>
          submit({
            game_answers: ordered.map((item, index) => ({
              item_id: item.id,
              value: String(index + 1),
            })),
          })
        }
      >
        Check the order
      </button>
    </section>
  );
}

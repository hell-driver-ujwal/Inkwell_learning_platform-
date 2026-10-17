/** A keyboard-accessible memory board counts completed two-card moves. */
import { useState } from "react";
export default function MemoryGame({ items, submit, busy }) {
  const [cards] = useState(() =>
    items
      .flatMap((item) => [
        { key: `${item.id}-front`, id: item.id, text: item.text },
        { key: `${item.id}-back`, id: item.id, text: item.match_text },
      ])
      .sort(() => Math.random() - 0.5),
  );
  const [selected, setSelected] = useState([]);
  const [matched, setMatched] = useState([]);
  const [moves, setMoves] = useState(0);
  function flip(card) {
    if (
      selected.length === 2 ||
      selected.includes(card.key) ||
      matched.includes(card.id)
    )
      return;
    const next = [...selected, card.key];
    setSelected(next);
    if (next.length === 2) {
      setMoves((count) => count + 1);
      const first = cards.find((candidate) => candidate.key === next[0]);
      if (first.id === card.id) setMatched((current) => [...current, card.id]);
    }
  }
  return (
    <section>
      <p>
        Find the matching pairs. Moves: {moves} · Pairs: {matched.length}/
        {items.length}
      </p>
      <div className="memory-grid">
        {cards.map((card) => (
          <button
            className="memory-card"
            key={card.key}
            disabled={matched.includes(card.id)}
            onClick={() => flip(card)}
            aria-label={
              selected.includes(card.key) || matched.includes(card.id)
                ? card.text
                : "Turn over card"
            }
          >
            {selected.includes(card.key) || matched.includes(card.id)
              ? card.text
              : "?"}
          </button>
        ))}
      </div>
      {selected.length === 2 && (
        <button className="secondary" onClick={() => setSelected([])}>
          Next turn
        </button>
      )}
      {matched.length === items.length && (
        <button
          disabled={busy}
          onClick={() => submit({ moves, game_answers: [] })}
        >
          Save memory result
        </button>
      )}
    </section>
  );
}

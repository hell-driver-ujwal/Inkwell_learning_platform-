/** Flashcards retain the original self-rating behavior. */
import { useState } from "react";
export default function FlashcardGame({ items, submit, busy }) {
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [answers, setAnswers] = useState([]);
  const item = items[index];
  function rate(value) {
    setAnswers([...answers, { item_id: item.id, value }]);
    setIndex(index + 1);
    setRevealed(false);
  }
  if (!item)
    return (
      <button disabled={busy} onClick={() => submit({ game_answers: answers })}>
        Save flashcard result
      </button>
    );
  return (
    <section className="flashcard">
      <p>
        Card {index + 1} of {items.length}
      </p>
      <h2>{item.text}</h2>
      {revealed ? (
        <>
          <p className="lead">{item.match_text}</p>
          <div className="actions">
            <button onClick={() => rate("known")}>I knew it</button>
            <button className="secondary" onClick={() => rate("learning")}>
              Still learning
            </button>
          </div>
        </>
      ) : (
        <button onClick={() => setRevealed(true)}>Reveal answer</button>
      )}
    </section>
  );
}

/** Choose a dedicated interaction while retaining template-specific scoring on the server. */
import MatchingGame from "./MatchingGame";
import SequenceGame from "./SequenceGame";
import TrueFalseGame from "./TrueFalseGame";
import AnswerGames from "./AnswerGames";
import FlashcardGame from "./FlashcardGame";
import MemoryGame from "./MemoryGame";
export default function GamePlayer({ activity, submit, busy }) {
  if (activity.game_template === "Matching")
    return (
      <MatchingGame
        items={activity.items}
        targets={activity.targets}
        submit={submit}
        busy={busy}
      />
    );
  if (activity.game_template === "Sequence")
    return <SequenceGame items={activity.items} submit={submit} busy={busy} />;
  if (activity.game_template === "TrueFalse")
    return <TrueFalseGame items={activity.items} submit={submit} busy={busy} />;
  if (activity.game_template === "Memory")
    return <MemoryGame items={activity.items} submit={submit} busy={busy} />;
  if (activity.game_template === "Flashcards")
    return <FlashcardGame items={activity.items} submit={submit} busy={busy} />;
  return <AnswerGames activity={activity} submit={submit} busy={busy} />;
}

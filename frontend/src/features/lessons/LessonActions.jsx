/** Completion and bookmark controls reflect server state after each successful action. */
import { useState } from "react";
import { api } from "../../api/client";
import { completeLesson, bookmarkLesson } from "../../api/courses";
import { ErrorMessage, Notice } from "../../components/Feedback";
export default function LessonActions({ lesson, reload }) {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function complete() {
    try {
      await completeLesson(lesson.id);
      setMessage("Lesson completed. Your progress is updated.");
      reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function bookmark() {
    try {
      if (lesson.bookmarked)
        await api(`materials/${lesson.id}/bookmark/`, { method: "DELETE" });
      else await bookmarkLesson(lesson.id);
      setMessage(
        lesson.bookmarked ? "Bookmark removed." : "Lesson bookmarked.",
      );
      reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  if (!lesson.can_complete) return null;
  return (
    <>
      <ErrorMessage>{error}</ErrorMessage>
      <Notice>{message}</Notice>
      <div className="actions">
        <button disabled={lesson.completed} onClick={complete}>
          {lesson.completed ? "Completed ✓" : "Mark complete"}
        </button>
        <button className="secondary" onClick={bookmark}>
          {lesson.bookmarked ? "Remove bookmark" : "Bookmark lesson"}
        </button>
      </div>
    </>
  );
}

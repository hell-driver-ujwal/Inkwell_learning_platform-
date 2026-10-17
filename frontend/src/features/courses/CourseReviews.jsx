/** Enrolled learners can create or replace their one course review. */
import { useState } from "react";
import { api } from "../../api/client";
import Field from "../../components/Field";
import { ErrorMessage } from "../../components/Feedback";
import { useAuth } from "../../context/AuthContext";
export default function CourseReviews({ course, reload }) {
  const { user } = useAuth();
  const [error, setError] = useState("");
  const ownReview = course.reviews.find(
    (review) => review.learner === user?.id,
  );
  async function remove() {
    try {
      await api(`courses/${course.id}/review/`, { method: "DELETE" });
      reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function submit(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      await api(`courses/${course.id}/review/`, {
        method: "PUT",
        body: { ...values, rating: Number(values.rating) },
      });
      reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <section>
      <h2>Learner reflections</h2>
      {course.reviews.map((review) => (
        <blockquote key={review.id}>
          <b>
            {"★".repeat(review.rating)} · {review.learner_name}
          </b>
          <p>{review.comment}</p>
        </blockquote>
      ))}
      {!course.reviews.length && (
        <p className="muted">Be the first to share what you learned.</p>
      )}
      {course.can_study && (
        <form key={ownReview?.id || "new"} className="panel" onSubmit={submit}>
          <h3>Share your experience</h3>
          <ErrorMessage>{error}</ErrorMessage>
          <Field
            label="Rating"
            name="rating"
            as="select"
            defaultValue={ownReview?.rating || 5}
          >
            {[5, 4, 3, 2, 1].map((rating) => (
              <option key={rating} value={rating}>
                {rating} stars
              </option>
            ))}
          </Field>
          <Field
            label="Your review"
            name="comment"
            defaultValue={ownReview?.comment || ""}
            as="textarea"
            minLength={10}
            maxLength={1000}
            required
          />
          <button>Save review</button>
          {ownReview && (
            <button type="button" className="text-button" onClick={remove}>
              Delete my review
            </button>
          )}
        </form>
      )}
    </section>
  );
}

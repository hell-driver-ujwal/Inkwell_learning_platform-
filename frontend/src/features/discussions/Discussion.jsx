/** Threaded discussion with learner ownership and lecturer moderation. */
import { useState } from "react";
import { api } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import { useResource } from "../../hooks/useResource";
import Field from "../../components/Field";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
export default function Discussion({ activity }) {
  const { user } = useAuth();
  const resource = useResource(`posts/?activity=${activity.id}`, { all: true });
  const [replyTo, setReplyTo] = useState(null);
  const [editing, setEditing] = useState(null);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await api(editing ? `posts/${editing}/` : "posts/", {
        method: editing ? "PATCH" : "POST",
        body: { activity: activity.id, parent: replyTo, content: text },
      });
      setText("");
      setEditing(null);
      setReplyTo(null);
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function remove(id) {
    try {
      await api(`posts/${id}/`, { method: "DELETE" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <ErrorMessage>{error}</ErrorMessage>
      <ResourceState resource={resource}>
        {(data) => (
          <div>
            {data.results.map((post) => (
              <article
                className={`post ${post.parent ? "reply" : ""}`}
                key={post.id}
              >
                <p>
                  <b>{post.author}</b> · {post.role} ·{" "}
                  {new Date(post.created_at).toLocaleString()}
                </p>
                <p>{post.content}</p>
                <div className="actions">
                  {!activity.is_closed && !post.parent && (
                    <button
                      className="text-button"
                      onClick={() => {
                        setReplyTo(post.id);
                        setEditing(null);
                        setText("");
                      }}
                    >
                      Reply
                    </button>
                  )}
                  {user.id === post.user && !activity.is_closed && (
                    <button
                      className="text-button"
                      onClick={() => {
                        setEditing(post.id);
                        setReplyTo(post.parent);
                        setText(post.content);
                      }}
                    >
                      Edit
                    </button>
                  )}
                  {(user.id === post.user || user.role !== "Learner") && (
                    <button
                      className="text-button"
                      onClick={() => remove(post.id)}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </article>
            ))}
            {!data.count && <p>Start the conversation.</p>}
          </div>
        )}
      </ResourceState>
      {activity.is_closed ? (
        <p className="notice">This discussion is closed.</p>
      ) : (
        <form onSubmit={submit}>
          <h2>
            {editing
              ? "Edit your post"
              : replyTo
                ? "Write a reply"
                : "Join the discussion"}
          </h2>
          <Field
            label="Your contribution"
            as="textarea"
            value={text}
            onChange={(event) => setText(event.target.value)}
            minLength={2}
            maxLength={2000}
            required
          />
          <div className="actions">
            <button>Save post</button>
            {(replyTo || editing) && (
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setReplyTo(null);
                  setEditing(null);
                  setText("");
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      )}
    </>
  );
}

/** Profile and password screens, including the mandatory temporary-password flow. */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import Field from "../../components/Field";
import { ErrorMessage, Notice } from "../../components/Feedback";
export function ProfilePage() {
  const { user, setUser } = useAuth();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function submit(event) {
    event.preventDefault();
    try {
      setUser(
        await api("auth/profile/", {
          method: "PATCH",
          body: Object.fromEntries(new FormData(event.currentTarget)),
        }),
      );
      setMessage("Profile updated.");
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <section className="narrow">
      <h1>Your profile</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <Notice>{message}</Notice>
      <form onSubmit={submit}>
        <Field
          label="Full name"
          name="full_name"
          defaultValue={user.full_name}
          required
        />
        <Field
          label="Email address"
          name="email"
          type="email"
          defaultValue={user.email}
          required
        />
        <p>
          {user.email} · {user.role === "Teacher" ? "Lecturer" : user.role}
        </p>
        <button>Save profile</button>
      </form>
      <p>
        <Link to="/password">Change password →</Link>
      </p>
    </section>
  );
}
export function PasswordPage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    try {
      setUser(
        await api("auth/password/", {
          method: "POST",
          body: Object.fromEntries(new FormData(event.currentTarget)),
        }),
      );
      navigate("/dashboard");
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <section className="narrow">
      <h1>Change password</h1>
      {user.must_change_password && (
        <p className="notice">
          Replace your temporary password before using your workspace.
        </p>
      )}
      <ErrorMessage>{error}</ErrorMessage>
      <form onSubmit={submit}>
        <Field
          label="Current password"
          name="current_password"
          type="password"
          autoComplete="current-password"
          required
        />
        <Field
          label="New password"
          name="new_password"
          type="password"
          autoComplete="new-password"
          minLength={8}
          required
        />
        <button>Update password</button>
      </form>
    </section>
  );
}

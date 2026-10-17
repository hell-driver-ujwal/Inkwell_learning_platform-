/** Separate role portals preserve the original login experience. */
import { useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import Field from "../../components/Field";
import { ErrorMessage, Notice } from "../../components/Feedback";
import { useAuth } from "../../context/AuthContext";
import { register } from "../../api/auth";
export function LoginChoicePage() {
  return (
    <>
      <h1>Welcome back.</h1>
      <p>Choose your workspace to continue.</p>
      <div className="three-columns">
        {[
          ["Learner", "Learn at your own pace."],
          ["Teacher", "Build your next great lesson."],
          ["Admin", "Look after the learning community."],
        ].map(([role, description]) => (
          <Link className="panel" key={role} to={`/login/${role}`}>
            <h2>{role === "Teacher" ? "Lecturer" : role}</h2>
            <p>{description}</p>
            <span>Log in →</span>
          </Link>
        ))}
      </div>
    </>
  );
}
export function LoginPage() {
  const { role } = useParams();
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const user = await signIn({ ...values, role });
      navigate(user.must_change_password ? "/password" : "/dashboard");
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="narrow">
      <span className="eyebrow">YOUR INKWELL WORKSPACE</span>
      <h1>{role === "Teacher" ? "Lecturer" : role} log in</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <form onSubmit={submit}>
        <Field
          label="Email address"
          name="email"
          type="email"
          autoComplete="username"
          required
        />
        <Field
          label="Password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
        />
        <button disabled={busy}>{busy ? "Signing in…" : "Log in"}</button>
      </form>
      <p>
        <Link to="/login">Choose another role</Link> ·{" "}
        <Link to="/register">Create an account</Link>
      </p>
    </section>
  );
}
export function RegisterPage() {
  const [params] = useSearchParams();
  const [role, setRole] = useState(
    params.get("role") === "Teacher" ? "Teacher" : "Learner",
  );
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      await register({
        ...Object.fromEntries(new FormData(event.currentTarget)),
        role,
      });
      setMessage(
        role === "Teacher"
          ? "Application received. An administrator must approve it before you can log in."
          : "Account created. You can now log in.",
      );
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <section className="narrow">
      <h1>A new chapter starts here.</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <Notice>{message}</Notice>
      {message ? (
        <Link to="/login">Go to log in →</Link>
      ) : (
        <form onSubmit={submit}>
          <Field
            label="I want to"
            as="select"
            value={role}
            onChange={(event) => setRole(event.target.value)}
          >
            <option value="Learner">Learn</option>
            <option value="Teacher">Apply to teach</option>
          </Field>
          <Field label="Full name" name="full_name" minLength={2} required />
          <Field label="Email address" name="email" type="email" required />
          <Field
            label="Password"
            name="password"
            type="password"
            minLength={8}
            required
          />
          {role === "Teacher" && (
            <Field
              label="Why would you like to teach?"
              as="textarea"
              name="application_reason"
              minLength={20}
              maxLength={500}
              required
            />
          )}
          <button>Create account</button>
        </form>
      )}
    </section>
  );
}

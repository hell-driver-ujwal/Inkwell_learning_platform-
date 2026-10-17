/** Contact messages use a one-use session CAPTCHA and CSRF protection. */
import { useState } from "react";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import Field from "../../components/Field";
import { ErrorMessage, Notice } from "../../components/Feedback";
export default function ContactPage() {
  const captcha = useResource("captcha/");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  async function submit(event) {
    event.preventDefault();
    setError("");
    const form = event.currentTarget;
    try {
      await api("contact/", {
        method: "POST",
        body: Object.fromEntries(new FormData(form)),
      });
      setMessage("Your message has been received.");
      form.reset();
    } catch (failure) {
      setError(failure.message);
    }
    captcha.reload();
  }
  return (
    <section className="narrow">
      <h1>Let’s talk.</h1>
      <p>Questions, ideas or a little help getting started.</p>
      <ErrorMessage>{error || captcha.error}</ErrorMessage>
      <Notice>{message}</Notice>
      <form onSubmit={submit}>
        <Field label="Your name" name="sender_name" minLength={2} required />
        <Field
          label="Email address"
          name="sender_email"
          type="email"
          required
        />
        <Field label="Subject" name="subject" minLength={3} required />
        <Field
          label="Message"
          name="message"
          as="textarea"
          minLength={10}
          maxLength={2000}
          required
        />
        <Field
          label={captcha.data?.question || "Loading verification question…"}
          name="captcha"
          type="number"
          required
        />
        <button>Send message</button>
      </form>
    </section>
  );
}

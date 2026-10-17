/** Clearly labeled local payment simulation and private receipts. */
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
export function PaymentsPage() {
  const resource = useResource("payments/", { all: true });
  return (
    <>
      <h1>My payments</h1>
      <p>Demo receipts only. No real money is transferred.</p>
      <ResourceState resource={resource}>
        {(data) => (
          <ul className="record-list">
            {data.results.map((payment) => (
              <li key={payment.id}>
                <Link to={`/payments/${payment.id}`}>
                  {payment.course_title}
                </Link>
                <span>
                  NPR {payment.amount_npr} · {payment.status}
                </span>
              </li>
            ))}
          </ul>
        )}
      </ResourceState>
    </>
  );
}
export function PaymentPage() {
  const { id } = useParams();
  const resource = useResource(`payments/${id}/`);
  const [error, setError] = useState("");
  async function verify(event) {
    event.preventDefault();
    setError("");
    try {
      await api(`payments/${id}/verify/`, {
        method: "POST",
        body: Object.fromEntries(new FormData(event.currentTarget)),
      });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
      resource.reload();
    }
  }
  async function cancel() {
    try {
      await api(`payments/${id}/cancel/`, { method: "POST" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <section className="narrow">
      <h1>eSewa demo checkout</h1>
      <p className="notice">
        This is a local learning simulation. No real payment or eSewa account is
        involved.
      </p>
      <ErrorMessage>{error}</ErrorMessage>
      <ResourceState resource={resource}>
        {(payment) => (
          <>
            <h2>{payment.course_title}</h2>
            <p className="price">NPR {payment.amount_npr}</p>
            <p>
              Status: <b>{payment.status}</b>
            </p>
            {payment.status === "Pending" ? (
              <form onSubmit={verify}>
                <Field
                  label="Demo mobile number"
                  name="phone"
                  placeholder="9841234567"
                  pattern="9[78][0-9]{8}"
                  required
                />
                <Field
                  label="Verification code (last four digits of the number)"
                  name="code"
                  pattern="[0-9]{4}"
                  required
                />
                <div className="actions">
                  <button>Verify payment</button>
                  <button type="button" className="secondary" onClick={cancel}>
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <>
                <p>
                  Reference:{" "}
                  {payment.provider_reference || payment.transaction_uuid}
                </p>
                {payment.verified_at && (
                  <p>
                    Verified: {new Date(payment.verified_at).toLocaleString()}
                  </p>
                )}
                <Link className="button" to={`/courses/${payment.course}`}>
                  Return to course
                </Link>
              </>
            )}
          </>
        )}
      </ResourceState>
    </section>
  );
}

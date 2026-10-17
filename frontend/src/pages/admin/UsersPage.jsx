/** Account review and temporary-password actions are explicit administrator operations. */
import { useState } from "react";
import { api } from "../../api/client";
import { useResource } from "../../hooks/useResource";
import { ErrorMessage, ResourceState } from "../../components/Feedback";
import Field from "../../components/Field";
export default function UsersPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const resource = useResource(
    `admin/users/?search=${encodeURIComponent(search)}&status=${status}`,
    { all: true },
  );
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null);
  async function action(user, operation) {
    const body = { action: operation };
    if (operation === "reset_password") {
      body.password = window.prompt(
        "Enter a temporary password (at least eight characters).",
      );
      if (!body.password) return;
    }
    try {
      await api(`admin/users/${user.id}/action/`, { method: "POST", body });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function remove(user) {
    if (
      !window.confirm(
        `Delete ${user.full_name} and their learning history? Accounts with payments or courses cannot be deleted.`,
      )
    )
      return;
    try {
      await api(`admin/users/${user.id}/`, { method: "DELETE" });
      resource.reload();
    } catch (failure) {
      setError(failure.message);
    }
  }
  async function save(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const body = Object.fromEntries(new FormData(form));
    if (!body.password) delete body.password;
    try {
      await api(editing ? `admin/users/${editing.id}/` : "admin/users/", {
        method: editing ? "PATCH" : "POST",
        body,
      });
      setEditing(null);
      resource.reload();
      form.reset();
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <>
      <h1>Accounts & lecturer applications</h1>
      <ErrorMessage>{error}</ErrorMessage>
      <div className="filter-bar">
        <Field
          label="Search users"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <Field
          label="Status"
          as="select"
          value={status}
          onChange={(event) => setStatus(event.target.value)}
        >
          <option value="">All statuses</option>
          {["Active", "Pending", "Rejected", "Deactivated"].map((value) => (
            <option key={value}>{value}</option>
          ))}
        </Field>
      </div>
      <ResourceState resource={resource}>
        {(data) => (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role / status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((user) => (
                  <tr key={user.id}>
                    <td>
                      {user.full_name}
                      <small>{user.email}</small>
                    </td>
                    <td>
                      {user.role} · {user.status}
                      <small>{user.application_reason}</small>
                      <small>
                        {user.locked_until
                          ? `Locked until ${new Date(user.locked_until).toLocaleString()}`
                          : ""}
                      </small>
                    </td>
                    <td>
                      {user.role !== "Admin" && (
                        <div className="actions">
                          <button
                            className="text-button"
                            onClick={() => remove(user)}
                          >
                            Delete
                          </button>
                          <button
                            className="text-button"
                            onClick={() => setEditing(user)}
                          >
                            Edit
                          </button>
                          {user.status === "Pending" && (
                            <>
                              <button onClick={() => action(user, "approve")}>
                                Approve
                              </button>
                              <button
                                className="secondary"
                                onClick={() => action(user, "reject")}
                              >
                                Reject
                              </button>
                            </>
                          )}
                          <button
                            className="text-button"
                            onClick={() =>
                              action(
                                user,
                                user.status === "Active"
                                  ? "deactivate"
                                  : "activate",
                              )
                            }
                          >
                            {user.status === "Active"
                              ? "Deactivate"
                              : "Activate"}
                          </button>
                          <button
                            className="text-button"
                            onClick={() => action(user, "unlock")}
                          >
                            Unlock
                          </button>
                          <button
                            className="text-button"
                            onClick={() => action(user, "reset_password")}
                          >
                            Reset password
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </ResourceState>
      <section className="panel">
        <h2>{editing ? `Edit ${editing.full_name}` : "Create an account"}</h2>
        <form key={editing?.id || "new"} onSubmit={save}>
          <Field
            label="Full name"
            name="full_name"
            defaultValue={editing?.full_name}
            required
          />
          <Field
            label="Email"
            name="email"
            type="email"
            defaultValue={editing?.email}
            required
          />
          <Field
            label="Role"
            name="role"
            as="select"
            defaultValue={editing?.role || "Learner"}
          >
            <option>Learner</option>
            <option>Teacher</option>
          </Field>
          <Field
            label="Temporary password"
            name="password"
            type="password"
            minLength={8}
            required={!editing}
          />
          <button>Save account</button>
          {editing && (
            <button
              type="button"
              className="secondary"
              onClick={() => setEditing(null)}
            >
              Cancel edit
            </button>
          )}
        </form>
      </section>
    </>
  );
}

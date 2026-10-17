/** Activity play uses a server-issued run ID, never a client score. */
import { api } from "./client";
export const startActivity = (id, preview) =>
  api(`activities/${id}/start/`, { method: "POST", body: { preview } });
export const submitActivity = (id, body) =>
  api(`activities/${id}/submit/`, { method: "POST", body });
export const moveScenario = (id, body) =>
  api(`activities/${id}/move/`, { method: "POST", body });

/** Authentication requests, including CSRF bootstrap before public forms. */
import { api } from "./client";
export const getSession = () => api("auth/session/");
export const login = (credentials) =>
  api("auth/login/", { method: "POST", body: credentials });
export const logout = () => api("auth/logout/", { method: "POST" });
export const register = (details) =>
  api("auth/register/", { method: "POST", body: details });

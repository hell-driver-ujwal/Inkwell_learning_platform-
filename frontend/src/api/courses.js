/** Course and learner-action endpoints. */
import { api } from "./client";
export const getCourse = (id) => api(`courses/${id}/`);
export const enroll = (id) =>
  api(`courses/${id}/enrollment/`, { method: "POST" });
export const leave = (id) =>
  api(`courses/${id}/enrollment/`, { method: "DELETE" });
export const completeLesson = (id) =>
  api(`materials/${id}/complete/`, { method: "POST" });
export const bookmarkLesson = (id) =>
  api(`materials/${id}/bookmark/`, { method: "POST" });

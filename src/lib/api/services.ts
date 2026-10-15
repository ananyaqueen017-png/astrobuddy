// Every backend call lives here. UI components import these functions only.
// Endpoint paths are assumptions: adjust them to match your backend.
import { apiRequest } from "./client";
import type * as T from "./types";

export const getHealth = (signal?: AbortSignal) =>
  apiRequest<T.HealthResponse>("/health", { signal, timeoutMs: 6000 });

export const calculateChart = (birth: T.BirthDetails) =>
  apiRequest<T.ChartResponse>("/charts/calculate", { method: "POST", body: birth });

export const getTransits = (req: T.TransitsRequest) =>
  apiRequest<T.TransitsResponse>("/transits", { method: "POST", body: req });

export const getDashas = (birth: T.BirthDetails, asOf?: string) =>
  apiRequest<T.DashasResponse>("/dashas", { method: "POST", body: { ...birth, asOf } });

// The backend holds AI-provider credentials; the browser never does.
export const askKundli = (req: T.AskRequest) =>
  apiRequest<T.AskResponse>("/ask", { method: "POST", body: req, timeoutMs: 60000 });

export const listJournalEntries = (q: T.JournalQuery = {}) =>
  apiRequest<T.JournalEntry[]>("/journal", { query: { ...q } });
export const createJournalEntry = (entry: T.NewJournalEntry) =>
  apiRequest<T.JournalEntry>("/journal", { method: "POST", body: entry });

export const listCalendarEntries = (month: string /* YYYY-MM */) =>
  apiRequest<T.CalendarEntry[]>("/calendar", { query: { month } });

export const compareCompatibility = (req: T.CompatibilityRequest) =>
  apiRequest<T.CompatibilityResponse>("/compatibility", { method: "POST", body: req });

export const runLabComparison = (req: T.LabRequest) =>
  apiRequest<T.LabResponse>("/lab/compare", { method: "POST", body: req });

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly fieldErrors?: Record<string, string>,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export const isApiConfigured = () => Boolean(BASE_URL);
export const getApiBaseUrl = () => BASE_URL ?? "";

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  query?: Record<string, string | undefined>;
  signal?: AbortSignal;
  timeoutMs?: number;
}

export async function apiRequest<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  if (!BASE_URL) {
    throw new ApiError("NEXT_PUBLIC_API_BASE_URL is not set. Add it to .env.local and restart the dev server.", 0);
  }
  const url = new URL(`${BASE_URL}${path}`);
  Object.entries(opts.query ?? {}).forEach(([k, v]) => v && url.searchParams.set(k, v));

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), opts.timeoutMs ?? 20000);
  opts.signal?.addEventListener("abort", () => controller.abort());

  try {
    const res = await fetch(url, {
      method: opts.method ?? "GET",
      headers: opts.body ? { "Content-Type": "application/json" } : undefined,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      signal: controller.signal,
    });
    if (!res.ok) {
      let message = `Request failed (${res.status}).`;
      let fieldErrors: Record<string, string> | undefined;
      try {
        const data = await res.json();
        message = data.message ?? data.detail ?? message;
        fieldErrors = data.fieldErrors;
      } catch { /* non-JSON error body */ }
      throw new ApiError(message, res.status, fieldErrors);
    }
    return (res.status === 204 ? undefined : await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if ((err as Error).name === "AbortError") throw new ApiError("The request timed out or was cancelled.", 0);
    throw new ApiError("Could not reach the server. Check your connection and the API URL.", 0);
  } finally {
    clearTimeout(timer);
  }
}

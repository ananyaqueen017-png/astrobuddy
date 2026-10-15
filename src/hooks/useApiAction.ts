"use client";
import { useCallback, useRef, useState } from "react";
import { ApiError } from "@/lib/api/client";

type Status = "idle" | "loading" | "success" | "error";

/** Runs an API call, tracks its state, and can retry with the last arguments. */
export function useApiAction<A extends unknown[], R>(fn: (...args: A) => Promise<R>) {
  const [status, setStatus] = useState<Status>("idle");
  const [data, setData] = useState<R | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const lastArgs = useRef<A | null>(null);

  const run = useCallback(async (...args: A) => {
    lastArgs.current = args;
    setStatus("loading");
    setError(null);
    try {
      const result = await fn(...args);
      setData(result);
      setStatus("success");
      return result;
    } catch (e) {
      setError(e instanceof ApiError ? e : new ApiError("Something went wrong.", 0));
      setStatus("error");
      return null;
    }
  }, [fn]);

  const retry = useCallback(() => (lastArgs.current ? run(...lastArgs.current) : Promise.resolve(null)), [run]);
  return { status, data, error, run, retry };
}

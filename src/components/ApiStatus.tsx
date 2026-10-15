"use client";
import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api/services";
import { isApiConfigured } from "@/lib/api/client";

export function ApiStatus() {
  const [state, setState] = useState<"checking" | "online" | "offline" | "unconfigured">("checking");

  useEffect(() => {
    if (!isApiConfigured()) { setState("unconfigured"); return; }
    const c = new AbortController();
    getHealth(c.signal).then(() => setState("online")).catch(() => setState("offline"));
    return () => c.abort();
  }, []);

  const map = {
    checking: ["Checking backend…", "bg-slate-500"],
    online: ["Backend reachable", "bg-emerald-400"],
    offline: ["Backend unreachable", "bg-red-400"],
    unconfigured: ["API URL not set", "bg-amber-400"],
  } as const;
  return (
    <span role="status" className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-1 text-xs text-slate-300">
      <span className={`h-2 w-2 rounded-full ${map[state][1]}`} aria-hidden /> {map[state][0]}
    </span>
  );
}

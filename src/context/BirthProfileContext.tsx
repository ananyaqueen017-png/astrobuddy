"use client";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { BirthDetails, ChartResponse } from "@/lib/api/types";

interface Ctx {
  birth: BirthDetails | null;
  chart: ChartResponse | null;
  setBirth: (b: BirthDetails | null) => void;
  setChart: (c: ChartResponse | null) => void;
  clear: () => void;
}
const BirthProfileContext = createContext<Ctx | null>(null);
const KEY = "astrobuddy:birth";

/** Holds the birth details the user entered. The chart itself always comes from the API. */
export function BirthProfileProvider({ children }: { children: ReactNode }) {
  const [birth, setBirthState] = useState<BirthDetails | null>(null);
  const [chart, setChart] = useState<ChartResponse | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY);
      const saved = raw ? JSON.parse(raw) : null;
      // Details saved by an older version lack calculation settings; ignore them rather than assume any.
      if (saved && saved.settings) setBirthState(saved as BirthDetails);
    } catch { /* storage unavailable */ }
  }, []);

  const setBirth = useCallback((b: BirthDetails | null) => {
    setBirthState(b);
    try { b ? localStorage.setItem(KEY, JSON.stringify(b)) : localStorage.removeItem(KEY); } catch { /* ignore */ }
  }, []);
  const clear = useCallback(() => { setBirth(null); setChart(null); }, [setBirth]);

  const value = useMemo(() => ({ birth, chart, setBirth, setChart, clear }), [birth, chart, setBirth, clear]);
  return <BirthProfileContext.Provider value={value}>{children}</BirthProfileContext.Provider>;
}

export function useBirthProfile() {
  const ctx = useContext(BirthProfileContext);
  if (!ctx) throw new Error("useBirthProfile must be used inside BirthProfileProvider");
  return ctx;
}

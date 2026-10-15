"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/StateViews";
import { useApiAction } from "@/hooks/useApiAction";
import { useBirthProfile } from "@/context/BirthProfileContext";
import { getDashas } from "@/lib/api/services";
import type { DashaPeriod } from "@/lib/api/types";

const days = (a: string, b: string) => (Date.parse(b) - Date.parse(a)) / 86_400_000;
const years = (p: { start: string; end: string }) => (days(p.start, p.end) / 365.25).toFixed(2);

export default function DashaTimelinePage() {
  const { birth } = useBirthProfile();
  const dashas = useApiAction(getDashas);
  const [selected, setSelected] = useState<string | null>(null);

  const { status, run } = dashas;
  useEffect(() => { if (birth && status === "idle") void run(birth); }, [birth, status, run]);

  const data = dashas.data;
  const active: DashaPeriod | undefined = data?.periods.find((p) => p.planet === (selected ?? data.current?.major)) ?? data?.periods[0];

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl font-semibold text-slate-50">Dasha Timeline</h1>
          <p className="mt-1 max-w-xl text-slate-400">Vimshottari major periods and sub-periods, calculated from the Moon&apos;s sidereal position.</p>
        </div>
        {birth && <button className="btn-ghost" disabled={status === "loading"} onClick={() => birth && dashas.run(birth)}>Recalculate</button>}
      </header>

      {!birth && (
        <div className="panel"><EmptyState title="No birth details yet" hint="Dashas need your birth details and a sidereal zodiac setting."
          action={<Link href="/" className="btn-primary">Go to dashboard</Link>} /></div>
      )}
      {status === "loading" && <div className="panel"><LoadingState label="Calculating dashas…" /></div>}
      {status === "error" && dashas.error && <ErrorState message={dashas.error.message} onRetry={dashas.retry} />}

      {data && (
        <>
          <section className="panel grid gap-4 p-5 text-sm sm:grid-cols-2 lg:grid-cols-4" aria-label="Summary">
            <div><p className="text-xs text-slate-500">Moon nakshatra</p>{data.moon.nakshatra} (pada {data.moon.pada})</div>
            <div><p className="text-xs text-slate-500">Balance at birth</p>{data.balanceAtBirthYears.toFixed(2)} years of {data.periods[0].planet}</div>
            <div><p className="text-xs text-slate-500">Current period ({data.asOf})</p>
              {data.current ? `${data.current.major}${data.current.sub ? ` / ${data.current.sub}` : ""}` : "Outside the calculated cycle"}</div>
            <div><p className="text-xs text-slate-500">Convention</p>{data.system}, {data.yearLengthDays}-day year</div>
            {data.warnings.map((w) => <p key={w} role="note" className="text-xs text-gold-300 sm:col-span-2 lg:col-span-4">{w}</p>)}
          </section>

          <section className="panel space-y-4 p-5" aria-label="Major periods">
            <h2 className="font-display text-2xl text-gold-300">Major periods</h2>
            <ol className="flex h-14 gap-1 overflow-hidden rounded-xl">
              {data.periods.map((p) => {
                const isCurrent = data.current?.major === p.planet;
                const isActive = active?.planet === p.planet;
                return (
                  <li key={p.planet + p.start} style={{ flexGrow: days(p.start, p.end), flexBasis: 0 }} className="min-w-0">
                    <button onClick={() => setSelected(p.planet)} aria-pressed={isActive}
                      title={`${p.planet}: ${p.start} to ${p.end}${isCurrent ? " (current)" : ""}`}
                      className={`h-full w-full truncate px-1 text-xs ${isActive ? "bg-violet-500/50" : "bg-night-700 hover:bg-violet-500/25"} ${isCurrent ? "ring-2 ring-inset ring-gold-400" : ""}`}>
                      {p.planet}
                    </button>
                  </li>
                );
              })}
            </ol>
            <p className="text-xs text-slate-500">Segment width is proportional to length. The gold outline marks the current period.</p>

            {active && (
              <div className="space-y-2">
                <h3 className="font-medium text-slate-100">
                  {active.planet} mahadasha: {active.start} to {active.end} ({years(active)} years{active.startsBeforeBirth ? ", begun before birth" : ""})
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[22rem] text-left text-sm">
                    <caption className="sr-only">Sub-periods of {active.planet}</caption>
                    <thead className="text-xs text-slate-500"><tr><th className="py-2">Sub-period</th><th>Start</th><th>End</th><th>Years</th></tr></thead>
                    <tbody>
                      {active.subPeriods.map((s) => {
                        const now = data.current?.major === active.planet && data.current.sub === s.planet;
                        return (
                          <tr key={s.planet + s.start} className={`border-t border-white/5 ${now ? "bg-gold-500/10" : ""}`}>
                            <td className="py-2">{active.planet} / {s.planet}{now ? " (current)" : ""}</td><td>{s.start}</td><td>{s.end}</td><td>{years(s)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

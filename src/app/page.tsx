"use client";
import Link from "next/link";
import { useState } from "react";
import { BirthForm } from "@/components/BirthForm";
import { ApiStatus } from "@/components/ApiStatus";
import { ChartWheel } from "@/components/chart/ChartWheel";
import { ChartSummary, PlanetTable } from "@/components/chart/ChartDetails";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/StateViews";
import { useApiAction } from "@/hooks/useApiAction";
import { useBirthProfile } from "@/context/BirthProfileContext";
import { calculateChart } from "@/lib/api/services";
import { NAV_GROUPS } from "@/lib/nav";
import type { BirthDetails } from "@/lib/api/types";

export default function DashboardPage() {
  const { birth, chart, setBirth, setChart } = useBirthProfile();
  const [selected, setSelected] = useState<string | null>(null);
  const calc = useApiAction(calculateChart);

  const submit = async (b: BirthDetails) => {
    setBirth(b);
    const result = await calc.run(b);
    if (result) setChart(result);
  };
  const selectedPlanet = chart?.planets.find((p) => p.id === selected);

  return (
    <div className="space-y-10">
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-semibold text-slate-50 sm:text-5xl">Your sky, read with context</h1>
          <p className="mt-2 max-w-xl text-slate-400">
            Enter your birth details to calculate your chart through the AstroBuddy backend. Every feature below builds on that chart.
          </p>
        </div>
        <ApiStatus />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <h2 className="mb-4 font-display text-2xl text-gold-300">Birth details</h2>
          <BirthForm initial={birth} loading={calc.status === "loading"} serverErrors={calc.error?.fieldErrors} onSubmit={submit} />
          {calc.status === "error" && calc.error && (
            <div className="mt-4"><ErrorState message={calc.error.message} onRetry={calc.retry} /></div>
          )}
        </div>

        <div className="panel flex flex-col items-center gap-4 p-5">
          {calc.status === "loading" ? <LoadingState label="Calculating your chart…" /> : (
            <>
              <ChartWheel chart={chart} selectedId={selected} onSelect={setSelected} />
              {!chart && <EmptyState title="No chart yet" hint="The wheel shows only the zodiac frame until the backend returns your chart." />}
              {selectedPlanet && (
                <p className="text-center text-sm text-slate-300">
                  <span className="font-medium text-gold-300">{selectedPlanet.name}</span> in {selectedPlanet.sign}, house {selectedPlanet.house}
                  {selectedPlanet.retrograde ? ", retrograde" : ""}
                </p>
              )}
            </>
          )}
        </div>
      </section>

      {chart && (
        <section className="panel space-y-4 p-5" aria-label="Chart details">
          <h2 className="font-display text-2xl text-gold-300">Calculated chart</h2>
          <ChartSummary chart={chart} />
          <PlanetTable planets={chart.planets} selectedId={selected} onSelect={setSelected} />
        </section>
      )}

      <section aria-labelledby="features" className="space-y-8">
        <h2 id="features" className="font-display text-3xl text-slate-50">Explore</h2>
        {NAV_GROUPS.map((g) => (
          <div key={g.label}>
            <h3 className="mb-3 text-sm text-slate-400">{g.label}</h3>
            <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {g.items.map(({ slug, title, blurb, icon: Icon }) => (
                <li key={slug}>
                  <Link href={`/${slug}`} className="panel group flex h-full gap-3 p-4 transition-colors hover:border-gold-400/60">
                    <Icon className="mt-0.5 h-5 w-5 shrink-0 text-violet-400 group-hover:text-gold-300" aria-hidden />
                    <span><span className="block font-medium text-slate-100">{title}</span><span className="text-sm text-slate-400">{blurb}</span></span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </div>
  );
}

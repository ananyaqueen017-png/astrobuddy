"use client";
import Link from "next/link";
import { useState } from "react";
import { ChartWheel } from "@/components/chart/ChartWheel";
import { ChartSummary, PlanetTable, deg } from "@/components/chart/ChartDetails";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/StateViews";
import { useApiAction } from "@/hooks/useApiAction";
import { useBirthProfile } from "@/context/BirthProfileContext";
import { calculateChart } from "@/lib/api/services";

type Tab = "planets" | "houses";

export default function LivingKundliPage() {
  const { birth, chart, setChart } = useBirthProfile();
  const calc = useApiAction(calculateChart);
  const [tab, setTab] = useState<Tab>("planets");
  const [planetId, setPlanetId] = useState<string | null>(null);
  const [houseNo, setHouseNo] = useState<number | null>(null);

  const load = async () => {
    if (!birth) return;
    const result = await calc.run(birth);
    if (result) setChart(result);
  };

  const planet = chart?.planets.find((p) => p.id === planetId);
  const house = chart?.houses.find((h) => h.number === houseNo);
  const inHouse = chart?.planets.filter((p) => p.house === houseNo) ?? [];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-4xl font-semibold text-slate-50">Living Kundli</h1>
        <p className="mt-1 max-w-xl text-slate-400">Select a planet or house to see the positions the backend calculated for your chart.</p>
      </header>

      {!birth && (
        <div className="panel"><EmptyState title="No birth details yet" hint="Enter your birth details on the dashboard to calculate a chart."
          action={<Link href="/" className="btn-primary">Go to dashboard</Link>} /></div>
      )}

      {birth && !chart && (
        <div className="panel p-5">
          {calc.status === "loading" ? <LoadingState label="Calculating your chart…" /> : (
            <div className="space-y-3">
              <p className="text-sm text-slate-300">Birth details are saved in this browser, but the chart is not loaded in this session.</p>
              <button className="btn-primary" onClick={load}>Calculate chart</button>
              {calc.status === "error" && calc.error && <ErrorState message={calc.error.message} onRetry={calc.retry} />}
            </div>
          )}
        </div>
      )}

      {chart && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="panel flex flex-col items-center p-5">
            <ChartWheel chart={chart} selectedId={planetId} onSelect={(id) => { setPlanetId(id); setTab("planets"); }} />
          </div>

          <div className="panel space-y-4 p-5">
            <div role="tablist" aria-label="Chart detail" className="flex gap-2">
              {(["planets", "houses"] as Tab[]).map((t) => (
                <button key={t} role="tab" id={`tab-${t}`} aria-selected={tab === t} aria-controls={`panel-${t}`}
                  onClick={() => setTab(t)} className={tab === t ? "btn-primary" : "btn-ghost"}>
                  {t === "planets" ? "Planets" : "Houses"}
                </button>
              ))}
            </div>

            {tab === "planets" && (
              <div role="tabpanel" id="panel-planets" aria-labelledby="tab-planets" className="space-y-4">
                <PlanetTable planets={chart.planets} selectedId={planetId} onSelect={setPlanetId} />
                {planet ? (
                  <p className="rounded-xl border border-white/10 p-3 text-sm text-slate-300">
                    <span className="font-medium text-gold-300">{planet.name}</span> is at {planet.sign} {deg(planet.degreeInSign)} (longitude {deg(planet.longitude)}) in house {planet.house}
                    {planet.nakshatra ? `, nakshatra ${planet.nakshatra} pada ${planet.nakshatraPada}` : ""}.
                    Daily motion {planet.speed.toFixed(3)}°, {planet.retrograde ? "retrograde" : "direct"}.
                  </p>
                ) : <p className="text-sm text-slate-500">Select a planet in the table or on the wheel.</p>}
              </div>
            )}

            {tab === "houses" && (
              <div role="tabpanel" id="panel-houses" aria-labelledby="tab-houses" className="space-y-4">
                <ul className="grid grid-cols-3 gap-2 sm:grid-cols-4">
                  {chart.houses.map((h) => (
                    <li key={h.number}>
                      <button onClick={() => setHouseNo(h.number)} aria-pressed={houseNo === h.number}
                        className={`w-full rounded-lg border px-2 py-2 text-sm ${houseNo === h.number ? "border-gold-400 bg-violet-500/20" : "border-white/10 hover:bg-white/5"}`}>
                        <span className="block text-xs text-slate-500">House {h.number}</span>{h.sign}
                      </button>
                    </li>
                  ))}
                </ul>
                {house ? (
                  <p className="rounded-xl border border-white/10 p-3 text-sm text-slate-300">
                    House {house.number} begins at {house.sign} {deg(house.degreeInSign)}.{" "}
                    {inHouse.length ? `Planets here: ${inHouse.map((p) => p.name).join(", ")}.` : "No planets in this house."}
                  </p>
                ) : <p className="text-sm text-slate-500">Select a house.</p>}
              </div>
            )}
          </div>

          <div className="panel p-5 lg:col-span-2"><ChartSummary chart={chart} /></div>
        </div>
      )}
    </div>
  );
}

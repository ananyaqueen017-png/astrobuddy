import { AYANAMSA_LABELS, HOUSE_LABELS } from "@/lib/api/defaults";
import type { ChartResponse, PlanetPosition } from "@/lib/api/types";

export const deg = (n: number) => `${n.toFixed(2)}°`;

/** Shows exactly which settings and engine produced the chart. */
export function ChartSummary({ chart }: { chart: ChartResponse }) {
  const s = chart.settings;
  const rows: [string, string][] = [
    ["Zodiac", s.zodiac === "sidereal" ? `Sidereal, ${AYANAMSA_LABELS[s.ayanamsa ?? "lahiri"]} ayanamsa${chart.ayanamsaValue != null ? ` (${deg(chart.ayanamsaValue)})` : ""}` : "Tropical"],
    ["Houses", HOUSE_LABELS[s.houseSystem]],
    ["Nodes", s.nodeType === "mean" ? "Mean" : "True"],
    ["Ascendant", `${chart.ascendantSign} ${deg(chart.ascendantLongitude % 30)}`],
    ["Birth time (UTC)", `${chart.birthUtc.replace("T", " ").slice(0, 16)} (offset ${chart.utcOffsetMinutes} min, ${chart.offsetSource === "timezone" ? chart.timezone : "manual"})`],
    ["Engine", `${chart.engine.name}, ${chart.engine.ephemeris}`],
  ];
  return (
    <div className="space-y-3">
      <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
        {rows.map(([k, v]) => (
          <div key={k}><dt className="text-xs text-slate-500">{k}</dt><dd className="text-slate-200">{v}</dd></div>
        ))}
      </dl>
      {chart.warnings.map((w) => (
        <p key={w} role="note" className="rounded-lg border border-gold-500/40 bg-gold-500/10 p-2 text-xs text-gold-300">{w}</p>
      ))}
    </div>
  );
}

export function PlanetTable({ planets, selectedId, onSelect }: { planets: PlanetPosition[]; selectedId?: string | null; onSelect?: (id: string) => void }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[32rem] text-left text-sm">
        <caption className="sr-only">Planet positions</caption>
        <thead className="text-xs text-slate-500">
          <tr><th className="py-2 pr-3">Planet</th><th className="pr-3">Sign</th><th className="pr-3">Degree</th><th className="pr-3">House</th><th className="pr-3">Nakshatra</th><th>Motion</th></tr>
        </thead>
        <tbody>
          {planets.map((p) => (
            <tr key={p.id} className={`border-t border-white/5 ${selectedId === p.id ? "bg-violet-500/15" : ""}`}>
              <td className="py-2 pr-3">
                {onSelect ? <button className="text-gold-300 hover:underline" onClick={() => onSelect(p.id)} aria-pressed={selectedId === p.id}>{p.name}</button> : p.name}
              </td>
              <td className="pr-3">{p.sign}</td><td className="pr-3">{deg(p.degreeInSign)}</td><td className="pr-3">{p.house}</td>
              <td className="pr-3">{p.nakshatra ? `${p.nakshatra} (${p.nakshatraPada})` : "n/a"}</td>
              <td>{p.retrograde ? "Retrograde" : "Direct"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

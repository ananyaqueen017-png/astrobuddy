"use client";
import type { ChartResponse } from "@/lib/api/types";

const SIGNS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
const C = 200;

const point = (r: number, deg: number) => {
  const a = (deg * Math.PI) / 180;
  return { x: C + r * Math.cos(a), y: C - r * Math.sin(a) };
};

interface Props {
  chart: ChartResponse | null; // null draws the empty zodiac frame only
  selectedId?: string | null;
  onSelect?: (planetId: string) => void;
}

/** Renders API-provided positions. It performs no astrological calculation of its own. */
export function ChartWheel({ chart, selectedId, onSelect }: Props) {
  const asc = chart?.ascendantLongitude ?? 0;
  // Ascendant sits at the left (180°); longitude increases counter-clockwise.
  const angle = (lon: number) => 180 + (lon - asc);

  return (
    <svg viewBox="0 0 400 400" role="img" className="h-auto w-full max-w-[460px]"
      aria-label={chart ? "Birth chart wheel with planet positions" : "Empty zodiac wheel. Calculate a chart to see planets."}>
      <defs>
        <radialGradient id="wheelFill" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#1A2152" /><stop offset="100%" stopColor="#0A0F27" />
        </radialGradient>
      </defs>
      <circle cx={C} cy={C} r={190} fill="url(#wheelFill)" stroke="#C9A24B" strokeOpacity=".7" />
      <circle cx={C} cy={C} r={142} fill="none" stroke="#8B5CF6" strokeOpacity=".5" />
      <circle cx={C} cy={C} r={70} fill="none" stroke="#8B5CF6" strokeOpacity=".25" />
      {SIGNS.map((s, i) => {
        const start = angle(i * 30);
        const a = point(190, start), b = point(142, start), g = point(166, start + 15);
        return (
          <g key={s}>
            <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#C9A24B" strokeOpacity=".4" />
            <text x={g.x} y={g.y} textAnchor="middle" dominantBaseline="central" fontSize="16" fill="#E6CB86">{s}</text>
          </g>
        );
      })}
      {chart?.houses.map((h) => {
        const p = point(142, angle(h.cuspLongitude)), q = point(70, angle(h.cuspLongitude));
        const label = point(106, angle(h.cuspLongitude) + 15);
        return (
          <g key={h.number}>
            <line x1={p.x} y1={p.y} x2={q.x} y2={q.y} stroke="#6770E6" strokeOpacity=".4" />
            <text x={label.x} y={label.y} textAnchor="middle" dominantBaseline="central" fontSize="9" fill="#8B93F5">{h.number}</text>
          </g>
        );
      })}
      {chart?.planets.map((pl) => {
        const p = point(124, angle(pl.longitude));
        const active = selectedId === pl.id;
        return (
          <g key={pl.id} role="button" tabIndex={0} aria-label={`${pl.name} in ${pl.sign}, house ${pl.house}`}
            aria-pressed={active} className="cursor-pointer"
            onClick={() => onSelect?.(pl.id)}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelect?.(pl.id)}>
            <circle cx={p.x} cy={p.y} r={12} fill={active ? "#C9A24B" : "#2A2F7A"} stroke="#C4B0FF" strokeOpacity=".7" />
            <text x={p.x} y={p.y} textAnchor="middle" dominantBaseline="central" fontSize="9" fontWeight="600"
              fill={active ? "#060919" : "#F1ECFF"}>{pl.name.slice(0, 2)}</text>
          </g>
        );
      })}
    </svg>
  );
}

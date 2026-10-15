"use client";
import { useState, type FormEvent } from "react";
import { AYANAMSA_LABELS, DEFAULT_SETTINGS, HOUSE_LABELS } from "@/lib/api/defaults";
import type { Ayanamsa, BirthDetails, CalculationSettings, HouseSystem } from "@/lib/api/types";

type Errors = Partial<Record<string, string>>;
type FieldKey = "name" | "date" | "time" | "latitude" | "longitude" | "timezone";
const QUADRANT_LIMITED: HouseSystem[] = ["placidus", "koch"];

export function validateBirth(v: Record<string, string>, settings: CalculationSettings): { errors: Errors; value?: BirthDetails } {
  const errors: Errors = {};
  if (!/^\d{4}-\d{2}-\d{2}$/.test(v.date)) errors.date = "Enter a birth date.";
  if (!/^\d{2}:\d{2}$/.test(v.time)) errors.time = "Enter a birth time.";
  const lat = Number(v.latitude), lon = Number(v.longitude);
  if (v.latitude === "" || Number.isNaN(lat) || lat < -90 || lat > 90) errors.latitude = "Latitude must be between -90 and 90.";
  if (v.longitude === "" || Number.isNaN(lon) || lon < -180 || lon > 180) errors.longitude = "Longitude must be between -180 and 180.";
  try { new Intl.DateTimeFormat("en", { timeZone: v.timezone }); } catch { errors.timezone = "Use an IANA time zone, such as Asia/Kolkata."; }
  if (settings.zodiac === "sidereal" && !settings.ayanamsa) errors.ayanamsa = "Choose an ayanamsa for the sidereal zodiac.";
  if (QUADRANT_LIMITED.includes(settings.houseSystem) && Math.abs(lat) > 66) errors.houseSystem = "This house system is undefined beyond 66° latitude.";
  if (Object.keys(errors).length) return { errors };
  return {
    errors,
    value: {
      name: v.name.trim() || undefined, date: v.date, time: v.time, latitude: lat, longitude: lon, timezone: v.timezone,
      settings: { ...settings, ayanamsa: settings.zodiac === "sidereal" ? settings.ayanamsa : null },
    },
  };
}

interface Props {
  initial: BirthDetails | null;
  loading: boolean;
  serverErrors?: Record<string, string>;
  onSubmit: (b: BirthDetails) => void;
}

export function BirthForm({ initial, loading, serverErrors, onSubmit }: Props) {
  const [v, setV] = useState({
    name: initial?.name ?? "", date: initial?.date ?? "", time: initial?.time ?? "",
    latitude: initial ? String(initial.latitude) : "", longitude: initial ? String(initial.longitude) : "",
    timezone: initial?.timezone ?? "Asia/Kolkata",
  });
  const [settings, setSettings] = useState<CalculationSettings>(initial?.settings ?? DEFAULT_SETTINGS);
  const [errors, setErrors] = useState<Errors>({});

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const r = validateBirth(v, settings);
    setErrors(r.errors);
    if (r.value) onSubmit(r.value);
  };

  const err = (key: string) => errors[key] ?? serverErrors?.[key];
  const message = (key: string) => err(key) && <p id={`b-${key}-e`} className="mt-1 text-xs text-red-300">{err(key)}</p>;

  const field = (key: FieldKey, label: string, props: React.InputHTMLAttributes<HTMLInputElement> = {}) => (
    <div>
      <label htmlFor={`b-${key}`} className="mb-1 block text-xs text-slate-400">{label}</label>
      <input id={`b-${key}`} className="field" value={v[key]} aria-invalid={Boolean(err(key))} aria-describedby={err(key) ? `b-${key}-e` : undefined}
        onChange={(e) => setV({ ...v, [key]: e.target.value })} {...props} />
      {message(key)}
    </div>
  );

  const select = (key: string, label: string, value: string, options: [string, string][], onChange: (v: string) => void, disabled = false) => (
    <div>
      <label htmlFor={`b-${key}`} className="mb-1 block text-xs text-slate-400">{label}</label>
      <select id={`b-${key}`} className="field" value={value} disabled={disabled} aria-invalid={Boolean(err(key))}
        aria-describedby={err(key) ? `b-${key}-e` : undefined} onChange={(e) => onChange(e.target.value)}>
        {options.map(([val, text]) => <option key={val} value={val}>{text}</option>)}
      </select>
      {message(key)}
    </div>
  );

  const sidereal = settings.zodiac === "sidereal";

  return (
    <form onSubmit={submit} noValidate className="grid gap-3 sm:grid-cols-2">
      <div className="sm:col-span-2">{field("name", "Name (optional)", { autoComplete: "name" })}</div>
      {field("date", "Birth date", { type: "date" })}
      {field("time", "Birth time (24h)", { type: "time" })}
      {field("latitude", "Birth place latitude", { inputMode: "decimal", placeholder: "26.2183" })}
      {field("longitude", "Birth place longitude", { inputMode: "decimal", placeholder: "78.1828" })}
      <div className="sm:col-span-2">{field("timezone", "Time zone (IANA)")}</div>

      <fieldset className="grid gap-3 rounded-xl border border-white/10 p-3 sm:col-span-2 sm:grid-cols-2">
        <legend className="px-1 text-xs text-slate-400">Calculation settings (sent with every request)</legend>
        {select("zodiac", "Zodiac", settings.zodiac, [["sidereal", "Sidereal (Vedic)"], ["tropical", "Tropical (Western)"]],
          (z) => setSettings({ ...settings, zodiac: z as CalculationSettings["zodiac"], ayanamsa: z === "sidereal" ? (settings.ayanamsa ?? "lahiri") : null }))}
        {select("ayanamsa", "Ayanamsa", settings.ayanamsa ?? "", sidereal
          ? (Object.entries(AYANAMSA_LABELS) as [string, string][]) : [["", "Not used (tropical)"]],
          (a) => setSettings({ ...settings, ayanamsa: a as Ayanamsa }), !sidereal)}
        {select("houseSystem", "House system", settings.houseSystem, Object.entries(HOUSE_LABELS) as [string, string][],
          (h) => setSettings({ ...settings, houseSystem: h as HouseSystem }))}
        {select("nodeType", "Lunar nodes (Rahu/Ketu)", settings.nodeType, [["mean", "Mean node"], ["true", "True node"]],
          (n) => setSettings({ ...settings, nodeType: n as CalculationSettings["nodeType"] }))}
      </fieldset>

      <button type="submit" disabled={loading} className="btn-primary sm:col-span-2">
        {loading ? "Calculating…" : "Calculate my chart"}
      </button>
    </form>
  );
}

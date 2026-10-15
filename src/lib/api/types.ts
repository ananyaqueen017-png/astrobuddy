// Request/response contracts. They mirror backend/app/schemas (JSON is camelCase).

export type Zodiac = "sidereal" | "tropical";
export type Ayanamsa = "lahiri" | "raman" | "krishnamurti" | "fagan_bradley" | "yukteshwar";
export type HouseSystem =
  | "whole_sign" | "placidus" | "equal" | "koch" | "porphyry" | "regiomontanus" | "campanus";
export type NodeType = "mean" | "true";

export interface CalculationSettings {
  zodiac: Zodiac;
  ayanamsa: Ayanamsa | null; // required when sidereal, null when tropical
  houseSystem: HouseSystem;
  nodeType: NodeType;
}

export interface BirthDetails {
  name?: string;
  date: string; // YYYY-MM-DD
  time: string; // HH:mm (24h)
  latitude: number;
  longitude: number;
  timezone: string; // IANA, e.g. "Asia/Kolkata"
  utcOffsetMinutes?: number; // optional manual override (needed only for ambiguous DST times)
  settings: CalculationSettings;
}

export interface PlanetPosition {
  id: string;
  name: string;
  longitude: number; // 0-360 ecliptic longitude in the chosen zodiac
  sign: string;
  degreeInSign: number;
  house: number;
  retrograde: boolean;
  speed: number;
  nakshatra: string | null; // sidereal zodiac only
  nakshatraPada: number | null;
}

export interface HouseInfo {
  number: number;
  sign: string;
  cuspLongitude: number;
  degreeInSign: number;
}

export interface EngineInfo { name: string; version: string; ephemeris: string }

export interface ChartResponse {
  ascendantLongitude: number;
  ascendantSign: string;
  planets: PlanetPosition[];
  houses: HouseInfo[];
  settings: CalculationSettings;
  ayanamsaValue: number | null;
  birthUtc: string;
  utcOffsetMinutes: number;
  timezone: string;
  offsetSource: "timezone" | "manual_offset";
  julianDayUt: number;
  engine: EngineInfo;
  warnings: string[];
}

export interface TransitsRequest { birth: BirthDetails; date: string }
export interface TransitsResponse {
  date: string;
  computedAtUtc: string;
  orbDegrees: number;
  planets: PlanetPosition[]; // houses are natal houses
  highlights: { title: string; explanation: string; startsOn?: string; endsOn?: string }[];
  settings: CalculationSettings;
}

export interface SubPeriod { planet: string; start: string; end: string }
export interface DashaPeriod {
  planet: string;
  start: string; // YYYY-MM-DD (UTC date)
  end: string;
  startsBeforeBirth?: boolean; // first period is clipped at birth
  subPeriods: SubPeriod[];
}
export interface DashasResponse {
  system: string;
  yearLengthDays: number;
  moon: { longitude: number; nakshatra: string; pada: number };
  balanceAtBirthYears: number;
  asOf: string;
  periods: DashaPeriod[];
  current: { major: string; sub: string | null } | null;
  settings: CalculationSettings;
  warnings: string[];
}

export interface AskRequest { birth: BirthDetails; question: string; conversationId?: string }
export interface AskResponse {
  conversationId: string;
  answer: string;
  chartFactors: { label: string; detail: string }[];
  grounded: boolean;
  disclaimer: string;
}

export interface JournalEntry {
  id: string;
  date: string;
  title: string;
  body: string;
  tags: string[];
}
export type NewJournalEntry = Omit<JournalEntry, "id">;
export interface JournalQuery { search?: string; tag?: string; from?: string; to?: string }

export interface CalendarEntry { id: string; date: string; title: string; summary: string; category: string }

export interface CompatibilityRequest { first: BirthDetails; second: BirthDetails }
export interface CompatibilityResponse {
  categories: { name: string; score?: number; explanation: string }[];
}

export interface LabRequest {
  birth: BirthDetails;
  // Options may override: zodiac, ayanamsa, houseSystem, nodeType
  variants: { label: string; options: Record<string, string | number | boolean> }[];
}
export interface LabResponse { results: { label: string; summary: string; data: Record<string, unknown> }[] }

export interface HealthResponse {
  status: "ok" | string;
  version?: string;
  engine?: { available: boolean; name: string | null; version: string | null; error?: string };
  llm_configured?: boolean;
  auth_configured?: boolean;
  database_configured?: boolean;
}

import type { Ayanamsa, CalculationSettings, HouseSystem } from "./types";

// Pre-filled in the birth form so the user can SEE and change them. They are always sent explicitly.
export const DEFAULT_SETTINGS: CalculationSettings = {
  zodiac: "sidereal",
  ayanamsa: "lahiri",
  houseSystem: "whole_sign",
  nodeType: "mean",
};

export const AYANAMSA_LABELS: Record<Ayanamsa, string> = {
  lahiri: "Lahiri",
  raman: "Raman",
  krishnamurti: "Krishnamurti",
  fagan_bradley: "Fagan/Bradley",
  yukteshwar: "Yukteshwar",
};

export const HOUSE_LABELS: Record<HouseSystem, string> = {
  whole_sign: "Whole sign",
  placidus: "Placidus",
  equal: "Equal",
  koch: "Koch",
  porphyry: "Porphyry",
  regiomontanus: "Regiomontanus",
  campanus: "Campanus",
};

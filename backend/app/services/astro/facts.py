"""Turn calculated results into numbered, plain-text facts for an LLM. Nothing is computed here."""
from typing import Optional

from .models import ChartResult


def build_chart_facts(chart: ChartResult, current_major: Optional[str] = None, current_sub: Optional[str] = None):
    s = chart.settings
    facts = [("Calculation settings",
              f"{s.zodiac} zodiac" + (f", {s.ayanamsa} ayanamsa" if s.ayanamsa else "")
              + f", {s.house_system} houses, {s.node_type} nodes")]
    facts.append(("Ascendant", f"{chart.ascendant_sign} {chart.ascendant_longitude % 30:.2f}°"))
    for p in chart.planets:
        detail = f"{p.name}: {p.sign} {p.degree_in_sign:.2f}°, house {p.house}"
        if p.retrograde:
            detail += ", retrograde"
        if p.nakshatra:
            detail += f", nakshatra {p.nakshatra} pada {p.nakshatra_pada}"
        facts.append((p.name, detail))
    if current_major:
        facts.append(("Current dasha", f"Vimshottari {current_major} mahadasha"
                      + (f", {current_sub} antardasha" if current_sub else "")))
    return [(f"F{i}", label, detail) for i, (label, detail) in enumerate(facts, start=1)]

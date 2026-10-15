from .houses import angular_separation


def find_conjunctions(natal: dict, transiting: dict, orb: float) -> list:
    """Pairs (transit_name, natal_name, separation_degrees) within `orb`, closest first."""
    found = []
    for t_name, t_lon in transiting.items():
        for n_name, n_lon in natal.items():
            sep = angular_separation(t_lon, n_lon)
            if sep <= orb:
                found.append((t_name, n_name, sep))
    return sorted(found, key=lambda x: x[2])


def build_highlights(natal_planets: list, transit_planets: list, orb: float) -> list:
    """Factual statements only (positions, houses, conjunction geometry). No interpretation."""
    out = []
    for p in transit_planets:
        if p.id in ("saturn", "jupiter", "rahu", "ketu"):
            retro = " (retrograde)" if p.retrograde else ""
            out.append({"title": f"Transit {p.name} in natal house {p.house}",
                        "explanation": f"Transiting {p.name} is at {p.sign} {p.degree_in_sign:.1f}°{retro}, "
                                       f"which falls in natal house {p.house}. Calculated position only."})
    natal = {n.name: n.longitude for n in natal_planets}
    moving = {t.name: t.longitude for t in transit_planets}
    for t_name, n_name, sep in find_conjunctions(natal, moving, orb)[:12]:
        out.append({"title": f"Transiting {t_name} conjunct natal {n_name}",
                    "explanation": f"Separation {sep:.2f}° (orb limit {orb:g}°). Geometric relationship only; "
                                   "no interpretation is included."})
    return out

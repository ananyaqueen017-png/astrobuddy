"""Validation + orchestration around an engine. Schema-free so it is easy to test."""
from datetime import date, datetime, time, timezone
from typing import Callable, Optional

from . import dasha as D
from . import options as O
from .errors import AstroInputError
from .houses import house_of
from .models import CalcSettings, ChartResult, PlanetResult
from .timeutil import resolve_birth_moment


def validate_settings(settings: CalcSettings) -> None:
    if settings.zodiac == "sidereal":
        if settings.ayanamsa not in O.AYANAMSAS:
            raise AstroInputError("ayanamsa", "A sidereal zodiac requires an ayanamsa. Choose one explicitly.")
    elif settings.ayanamsa is not None:
        raise AstroInputError("ayanamsa", "Ayanamsa applies only to the sidereal zodiac.")


def calculate(engine_getter: Callable, d: date, t: time, tz: str, utc_offset_minutes: Optional[float],
              latitude: float, longitude: float, settings: CalcSettings) -> ChartResult:
    """Validate everything first, then obtain the engine (so validation works without it)."""
    validate_settings(settings)
    if not (O.MIN_YEAR <= d.year <= O.MAX_YEAR):
        raise AstroInputError("date", f"Birth year must be between {O.MIN_YEAR} and {O.MAX_YEAR}.")
    if settings.house_system in O.LATITUDE_LIMITED_HOUSE_SYSTEMS and abs(latitude) > O.MAX_QUADRANT_LATITUDE:
        raise AstroInputError("houseSystem", f"{settings.house_system.title()} houses are undefined beyond "
                                             f"{O.MAX_QUADRANT_LATITUDE:.0f}° latitude. Use whole sign, equal or porphyry.")
    birth = resolve_birth_moment(d, t, tz, utc_offset_minutes)
    return engine_getter().calculate_chart(birth, latitude, longitude, settings)


def require_sidereal(settings: CalcSettings) -> None:
    if settings.zodiac != "sidereal":
        raise AstroInputError("zodiac", "Vimshottari dasha is defined on the sidereal zodiac. "
                                        "Select a sidereal zodiac and an ayanamsa.")


def dasha_for(chart: ChartResult, year_days: float, as_of: Optional[datetime] = None):
    require_sidereal(chart.settings)
    moon = next(p for p in chart.planets if p.id == "moon")
    result = D.build_vimshottari(moon.longitude, chart.birth.utc, year_days)
    now = as_of or datetime.now(timezone.utc)
    return result, D.current_periods(result, now), now


def transit_positions(engine_getter: Callable, natal: ChartResult, when: datetime):
    """Transiting planets at `when` (UTC), assigned to the natal chart's houses."""
    engine = engine_getter()
    planets, _, _, _ = engine.positions(when, natal.settings)
    cusps = [h.cusp_longitude for h in natal.houses]
    return [PlanetResult(p.id, p.name, p.longitude, p.sign, p.degree_in_sign, house_of(p.longitude, cusps),
                         p.retrograde, p.speed, p.nakshatra, p.nakshatra_pada) for p in planets]

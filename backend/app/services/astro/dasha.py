"""Vimshottari dasha (120-year cycle) from the Moon's sidereal longitude.

Standard rules implemented here:
  * 27 nakshatras of 13°20' map to nine lords in the repeating order Ketu, Venus, Sun, Moon,
    Mars, Rahu, Jupiter, Saturn, Mercury (Ashwini = Ketu).
  * The mahadasha at birth is the Moon nakshatra's lord. The part already elapsed equals the
    fraction of the nakshatra the Moon has crossed.
  * Each mahadasha splits into nine antardashas, starting with the mahadasha lord and following
    the same order; antardasha length = MD years x AD lord years / 120.
Year length is a convention (365.25 days by default) and is reported with every result.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

DASHA_ORDER = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
               ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
CYCLE_YEARS = 120
DEFAULT_YEAR_DAYS = 365.25


@dataclass
class Period:
    planet: str
    start: datetime
    end: datetime
    sub_periods: list = field(default_factory=list)
    starts_before_birth: bool = False


@dataclass
class VimshottariResult:
    moon_longitude: float
    nakshatra_index: int
    birth_lord: str
    balance_at_birth_years: float
    year_days: float
    periods: list


def build_vimshottari(moon_longitude: float, birth_utc: datetime, year_days: float = DEFAULT_YEAR_DAYS):
    pos = (moon_longitude % 360.0) * 27.0 / 360.0
    nak = min(int(pos), 26)
    elapsed = pos - nak
    first = nak % 9
    first_years = DASHA_ORDER[first][1]

    cursor = birth_utc - timedelta(days=first_years * elapsed * year_days)
    periods = []
    for k in range(9):
        li = (first + k) % 9
        lord, years = DASHA_ORDER[li]
        md_end = cursor + timedelta(days=years * year_days)

        subs, sc = [], cursor
        for j in range(9):
            sub_lord, sub_years = DASHA_ORDER[(li + j) % 9]
            s_end = md_end if j == 8 else sc + timedelta(days=years * sub_years / CYCLE_YEARS * year_days)
            subs.append(Period(sub_lord, sc, s_end))
            sc = s_end

        before_birth = cursor < birth_utc
        if before_birth:  # first mahadasha: drop/clip what happened before birth
            subs = [Period(s.planet, max(s.start, birth_utc), s.end) for s in subs if s.end > birth_utc]
        periods.append(Period(lord, max(cursor, birth_utc), md_end, subs, before_birth))
        cursor = md_end

    return VimshottariResult(moon_longitude % 360.0, nak, DASHA_ORDER[first][0],
                             first_years * (1.0 - elapsed), year_days, periods)


def current_periods(result: VimshottariResult, as_of: datetime):
    """Return (major, sub) Period objects active at `as_of`, or (None, None) if outside the cycle."""
    for md in result.periods:
        if md.start <= as_of < md.end:
            for sd in md.sub_periods:
                if sd.start <= as_of < sd.end:
                    return md, sd
            return md, None
    return None, None

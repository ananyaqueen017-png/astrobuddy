"""Swiss Ephemeris adapter (pyswisseph).

LICENSING: the Swiss Ephemeris and pyswisseph are dual-licensed (AGPL or Astrodienst
professional license). Review https://www.astro.com/swisseph/ before deploying publicly.
The module is imported lazily so the rest of the API runs without it installed.
"""
import threading
from datetime import timezone

from . import houses as H
from . import zodiac as Z
from .errors import EngineUnavailableError
from .models import CalcSettings, ChartResult, HouseResult, PlanetResult

_LOCK = threading.Lock()  # Swiss Ephemeris keeps global state (sidereal mode); serialize calls.

_AYANAMSA_CONSTANTS = {"lahiri": "SIDM_LAHIRI", "raman": "SIDM_RAMAN", "krishnamurti": "SIDM_KRISHNAMURTI",
                       "fagan_bradley": "SIDM_FAGAN_BRADLEY", "yukteshwar": "SIDM_YUKTESHWAR"}
_HOUSE_CODES = {"whole_sign": b"W", "placidus": b"P", "equal": b"E", "koch": b"K",
                "porphyry": b"O", "regiomontanus": b"R", "campanus": b"C"}
_BODIES = [("sun", "Sun", "SUN"), ("moon", "Moon", "MOON"), ("mars", "Mars", "MARS"),
           ("mercury", "Mercury", "MERCURY"), ("jupiter", "Jupiter", "JUPITER"),
           ("venus", "Venus", "VENUS"), ("saturn", "Saturn", "SATURN")]


class SwissEphemerisEngine:
    def __init__(self, ephe_path: str = "", mode: str = "auto"):
        try:
            import swisseph as swe
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise EngineUnavailableError(
                "pyswisseph is not installed. Run: pip install -r requirements.txt"
            ) from exc
        self.swe = swe
        if ephe_path:
            swe.set_ephe_path(ephe_path)
        self._base_flags = (swe.FLG_MOSEPH if mode == "moshier" else swe.FLG_SWIEPH) | swe.FLG_SPEED
        self.name = "Swiss Ephemeris (pyswisseph)"
        self.version = f"pyswisseph {getattr(swe, '__version__', '?')} / swisseph {getattr(swe, 'version', '?')}"

    # -- planets -----------------------------------------------------------------------
    def positions(self, utc, settings: CalcSettings):
        """Geocentric apparent positions at a UTC instant. Houses are not assigned (house=0)."""
        swe = self.swe
        u = utc.astimezone(timezone.utc)
        sidereal = settings.zodiac == "sidereal"
        with _LOCK:
            if sidereal:
                swe.set_sid_mode(getattr(swe, _AYANAMSA_CONSTANTS[settings.ayanamsa]))
            _, jd_ut = swe.utc_to_jd(u.year, u.month, u.day, u.hour, u.minute,
                                     u.second + u.microsecond / 1e6, swe.GREG_CAL)
            flags = self._base_flags | (swe.FLG_SIDEREAL if sidereal else 0)
            ayanamsa = swe.get_ayanamsa_ut(jd_ut) if sidereal else None

            raw, ephemeris = [], "swiss_ephemeris_files"
            node_body = swe.TRUE_NODE if settings.node_type == "true" else swe.MEAN_NODE
            bodies = [(i, n, getattr(swe, c)) for i, n, c in _BODIES] + [("rahu", "Rahu", node_body)]
            for pid, name, body in bodies:
                res = swe.calc_ut(jd_ut, body, flags)
                xx, retflag = res if isinstance(res[0], (tuple, list)) else (res, flags)
                if retflag & swe.FLG_MOSEPH:
                    ephemeris = "moshier (built-in; no ephemeris files found or requested)"
                raw.append((pid, name, xx[0] % 360.0, xx[3]))

        rahu = raw[-1]
        raw.append(("ketu", "Ketu", (rahu[2] + 180.0) % 360.0, rahu[3]))
        order = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
        raw.sort(key=lambda r: order.index(r[0]))

        planets = []
        for pid, name, lon, speed in raw:
            nak, pada = Z.nakshatra_of(lon) if sidereal else (None, None)
            planets.append(PlanetResult(pid, name, lon, Z.sign_name(lon), Z.degree_in_sign(lon), 0,
                                        speed < 0, speed, nak, pada))
        return planets, ayanamsa, jd_ut, ephemeris

    # -- full chart --------------------------------------------------------------------
    def calculate_chart(self, birth, latitude: float, longitude: float, settings: CalcSettings) -> ChartResult:
        swe = self.swe
        planets, ayanamsa, jd_ut, ephemeris = self.positions(birth.utc, settings)
        sidereal = settings.zodiac == "sidereal"
        with _LOCK:
            if sidereal:
                swe.set_sid_mode(getattr(swe, _AYANAMSA_CONSTANTS[settings.ayanamsa]))
            cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, _HOUSE_CODES[settings.house_system],
                                         swe.FLG_SIDEREAL if sidereal else 0)
        asc = ascmc[0] % 360.0
        cusps = list(cusps)
        if len(cusps) == 13:  # some builds return a leading placeholder
            cusps = cusps[1:]
        if settings.house_system == "whole_sign":
            cusps = H.whole_sign_cusps(asc)  # definition: house 1 starts at 0° of the ascendant sign
        cusps = [c % 360.0 for c in cusps[:12]]

        placed = [PlanetResult(p.id, p.name, p.longitude, p.sign, p.degree_in_sign, H.house_of(p.longitude, cusps),
                               p.retrograde, p.speed, p.nakshatra, p.nakshatra_pada) for p in planets]
        house_rows = [HouseResult(i + 1, Z.sign_name(c), c, Z.degree_in_sign(c)) for i, c in enumerate(cusps)]
        return ChartResult(birth, latitude, longitude, settings, asc, Z.sign_name(asc), placed, house_rows,
                           ayanamsa, jd_ut, self.name, self.version, ephemeris, list(birth.warnings))

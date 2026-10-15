"""Plain dataclasses shared by the engine, services and routers (no third-party imports)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CalcSettings:
    zodiac: str  # "sidereal" | "tropical"
    ayanamsa: Optional[str]  # required for sidereal, None for tropical
    house_system: str
    node_type: str  # "mean" | "true"


@dataclass(frozen=True)
class BirthMoment:
    utc: datetime  # timezone-aware, UTC
    utc_offset_minutes: float  # offset that was applied (may be fractional for local mean time)
    timezone: str
    offset_source: str  # "timezone" | "manual_offset"
    warnings: tuple = ()


@dataclass(frozen=True)
class PlanetResult:
    id: str
    name: str
    longitude: float
    sign: str
    degree_in_sign: float
    house: int  # 0 when not yet assigned
    retrograde: bool
    speed: float  # degrees/day in longitude
    nakshatra: Optional[str] = None  # sidereal zodiac only
    nakshatra_pada: Optional[int] = None


@dataclass(frozen=True)
class HouseResult:
    number: int
    sign: str
    cusp_longitude: float
    degree_in_sign: float


@dataclass(frozen=True)
class ChartResult:
    birth: BirthMoment
    latitude: float
    longitude: float
    settings: CalcSettings
    ascendant_longitude: float
    ascendant_sign: str
    planets: list
    houses: list
    ayanamsa_value: Optional[float]
    julian_day_ut: float
    engine_name: str
    engine_version: str
    ephemeris: str
    warnings: list = field(default_factory=list)

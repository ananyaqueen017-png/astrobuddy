import datetime as dt
from typing import Literal, Optional

from pydantic import Field

from app.services.astro.models import CalcSettings, ChartResult, PlanetResult
from .common import CamelModel

AyanamsaT = Literal["lahiri", "raman", "krishnamurti", "fagan_bradley", "yukteshwar"]
HouseSystemT = Literal["whole_sign", "placidus", "equal", "koch", "porphyry", "regiomontanus", "campanus"]


class CalculationSettings(CamelModel):
    zodiac: Literal["sidereal", "tropical"]
    ayanamsa: Optional[AyanamsaT] = None
    house_system: HouseSystemT
    node_type: Literal["mean", "true"]

    def to_calc(self) -> CalcSettings:
        return CalcSettings(self.zodiac, self.ayanamsa, self.house_system, self.node_type)


class BirthInput(CamelModel):
    name: Optional[str] = Field(default=None, max_length=100)
    date: dt.date
    time: dt.time
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1, max_length=64)
    utc_offset_minutes: Optional[float] = Field(default=None, ge=-840, le=840)
    settings: CalculationSettings


class PlanetOut(CamelModel):
    id: str
    name: str
    longitude: float
    sign: str
    degree_in_sign: float
    house: int
    retrograde: bool
    speed: float
    nakshatra: Optional[str] = None
    nakshatra_pada: Optional[int] = None

    @classmethod
    def of(cls, p: PlanetResult) -> "PlanetOut":
        return cls(id=p.id, name=p.name, longitude=p.longitude, sign=p.sign, degree_in_sign=p.degree_in_sign,
                   house=p.house, retrograde=p.retrograde, speed=p.speed, nakshatra=p.nakshatra,
                   nakshatra_pada=p.nakshatra_pada)


class HouseOut(CamelModel):
    number: int
    sign: str
    cusp_longitude: float
    degree_in_sign: float


class EngineInfo(CamelModel):
    name: str
    version: str
    ephemeris: str


class ChartResponse(CamelModel):
    ascendant_longitude: float
    ascendant_sign: str
    planets: list[PlanetOut]
    houses: list[HouseOut]
    settings: CalculationSettings
    ayanamsa_value: Optional[float]
    birth_utc: str
    utc_offset_minutes: float
    timezone: str
    offset_source: str
    julian_day_ut: float
    engine: EngineInfo
    warnings: list[str]

    @classmethod
    def of(cls, c: ChartResult) -> "ChartResponse":
        s = c.settings
        return cls(
            ascendant_longitude=c.ascendant_longitude, ascendant_sign=c.ascendant_sign,
            planets=[PlanetOut.of(p) for p in c.planets],
            houses=[HouseOut(number=h.number, sign=h.sign, cusp_longitude=h.cusp_longitude,
                             degree_in_sign=h.degree_in_sign) for h in c.houses],
            settings=CalculationSettings(zodiac=s.zodiac, ayanamsa=s.ayanamsa, house_system=s.house_system,
                                         node_type=s.node_type),
            ayanamsa_value=c.ayanamsa_value, birth_utc=c.birth.utc.isoformat(),
            utc_offset_minutes=c.birth.utc_offset_minutes, timezone=c.birth.timezone,
            offset_source=c.birth.offset_source, julian_day_ut=c.julian_day_ut,
            engine=EngineInfo(name=c.engine_name, version=c.engine_version, ephemeris=c.ephemeris),
            warnings=c.warnings,
        )

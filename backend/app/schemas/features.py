import datetime as dt
from typing import Any, Optional, Union

from pydantic import Field

from .chart import BirthInput, CalculationSettings, PlanetOut
from .common import CamelModel


# --- Dasha ---------------------------------------------------------------------------
class DashaRequest(BirthInput):
    as_of: Optional[dt.date] = None  # defaults to today (UTC)


class SubPeriodOut(CamelModel):
    planet: str
    start: str
    end: str


class DashaPeriodOut(CamelModel):
    planet: str
    start: str
    end: str
    starts_before_birth: bool = False
    sub_periods: list[SubPeriodOut]


class MoonInfo(CamelModel):
    longitude: float
    nakshatra: str
    pada: int


class CurrentDasha(CamelModel):
    major: str
    sub: Optional[str]


class DashasResponse(CamelModel):
    system: str
    year_length_days: float
    moon: MoonInfo
    balance_at_birth_years: float
    as_of: str
    periods: list[DashaPeriodOut]
    current: Optional[CurrentDasha]
    settings: CalculationSettings
    warnings: list[str]


# --- Transits ------------------------------------------------------------------------
class TransitsRequest(CamelModel):
    birth: BirthInput
    date: dt.date


class Highlight(CamelModel):
    title: str
    explanation: str
    starts_on: Optional[str] = None
    ends_on: Optional[str] = None


class TransitsResponse(CamelModel):
    date: str
    computed_at_utc: str
    orb_degrees: float
    planets: list[PlanetOut]
    highlights: list[Highlight]
    settings: CalculationSettings


# --- Ask Your Kundli -----------------------------------------------------------------
class AskRequest(CamelModel):
    birth: BirthInput
    question: str = Field(min_length=3, max_length=1000)
    conversation_id: Optional[str] = Field(default=None, max_length=64)


class ChartFactor(CamelModel):
    label: str
    detail: str


class AskResponse(CamelModel):
    conversation_id: str
    answer: str
    chart_factors: list[ChartFactor]
    grounded: bool  # False when the model did not return parseable supporting-fact IDs
    disclaimer: str


# --- Lab -----------------------------------------------------------------------------
class LabVariant(CamelModel):
    label: str = Field(min_length=1, max_length=60)
    options: dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)


class LabRequest(CamelModel):
    birth: BirthInput
    variants: list[LabVariant] = Field(min_length=1, max_length=6)


class LabResult(CamelModel):
    label: str
    summary: str
    data: dict[str, Any]


class LabResponse(CamelModel):
    results: list[LabResult]

from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.chart import CalculationSettings
from app.schemas.features import (CurrentDasha, DashaPeriodOut, DashaRequest, DashasResponse, MoonInfo,
                                  SubPeriodOut)
from app.services.astro import chart_service
from app.services.astro.zodiac import nakshatra_of
from ._common import compute_chart

router = APIRouter(prefix="/dashas", tags=["dashas"])
_d = lambda dt: dt.date().isoformat()  # noqa: E731  (UTC calendar date)


@router.post("", response_model=DashasResponse, summary="Vimshottari dasha timeline")
def dashas(body: DashaRequest, settings: Settings = Depends(get_settings)):
    chart_service.require_sidereal(body.settings.to_calc())  # fail fast, before any calculation
    chart = compute_chart(body)
    as_of = datetime.combine(body.as_of, time.min, tzinfo=timezone.utc) if body.as_of else None
    result, (major, sub), when = chart_service.dasha_for(chart, settings.dasha_year_days, as_of)
    nak, pada = nakshatra_of(result.moon_longitude)
    s = chart.settings
    return DashasResponse(
        system="vimshottari", year_length_days=result.year_days,
        moon=MoonInfo(longitude=result.moon_longitude, nakshatra=nak, pada=pada),
        balance_at_birth_years=result.balance_at_birth_years, as_of=_d(when),
        periods=[DashaPeriodOut(planet=p.planet, start=_d(p.start), end=_d(p.end),
                                starts_before_birth=p.starts_before_birth,
                                sub_periods=[SubPeriodOut(planet=x.planet, start=_d(x.start), end=_d(x.end))
                                             for x in p.sub_periods]) for p in result.periods],
        current=CurrentDasha(major=major.planet, sub=sub.planet if sub else None) if major else None,
        settings=CalculationSettings(zodiac=s.zodiac, ayanamsa=s.ayanamsa, house_system=s.house_system,
                                     node_type=s.node_type),
        warnings=chart.warnings,
    )

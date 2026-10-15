from datetime import datetime, time, timezone

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.chart import CalculationSettings, PlanetOut
from app.schemas.features import Highlight, TransitsRequest, TransitsResponse
from app.services.astro import chart_service
from app.services.astro.factory import get_engine
from app.services.astro.transits import build_highlights
from ._common import compute_chart

router = APIRouter(prefix="/transits", tags=["transits"])


@router.post("", response_model=TransitsResponse, summary="Transiting planets over a natal chart")
def transits(body: TransitsRequest, settings: Settings = Depends(get_settings)):
    """Positions are computed for 12:00 UTC on the requested date, then placed in the natal houses."""
    natal = compute_chart(body.birth)
    when = datetime.combine(body.date, time(12, 0), tzinfo=timezone.utc)
    moving = chart_service.transit_positions(get_engine, natal, when)
    s = natal.settings
    return TransitsResponse(
        date=body.date.isoformat(), computed_at_utc=when.isoformat(), orb_degrees=settings.transit_orb_degrees,
        planets=[PlanetOut.of(p) for p in moving],
        highlights=[Highlight(**h) for h in build_highlights(natal.planets, moving, settings.transit_orb_degrees)],
        settings=CalculationSettings(zodiac=s.zodiac, ayanamsa=s.ayanamsa, house_system=s.house_system,
                                     node_type=s.node_type),
    )

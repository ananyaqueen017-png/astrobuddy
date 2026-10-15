from dataclasses import replace

from fastapi import APIRouter

from app.schemas.chart import CalculationSettings
from app.schemas.features import LabRequest, LabResponse, LabResult
from app.services.astro import chart_service, options as O
from app.services.astro.errors import AstroInputError
from app.services.astro.factory import get_engine
from app.services.astro.models import CalcSettings

router = APIRouter(prefix="/lab", tags=["lab"])
_ALLOWED = {"zodiac": {"sidereal", "tropical"}, "ayanamsa": set(O.AYANAMSAS),
            "houseSystem": set(O.HOUSE_SYSTEMS), "nodeType": {"mean", "true"}}


def _apply(base: CalcSettings, options: dict) -> CalcSettings:
    for key, value in options.items():
        if key not in _ALLOWED:
            raise AstroInputError("options", f"Unknown option '{key}'. Allowed: {', '.join(_ALLOWED)}.")
        if value not in _ALLOWED[key]:
            raise AstroInputError("options", f"Invalid value '{value}' for '{key}'.")
    s = replace(base,
                zodiac=options.get("zodiac", base.zodiac),
                ayanamsa=options.get("ayanamsa", base.ayanamsa),
                house_system=options.get("houseSystem", base.house_system),
                node_type=options.get("nodeType", base.node_type))
    if s.zodiac == "tropical" and "ayanamsa" not in options:
        s = replace(s, ayanamsa=None)  # switching to tropical clears the ayanamsa
    return s


@router.post("/compare", response_model=LabResponse, summary="Compare calculation settings side by side")
def compare(body: LabRequest):
    """Runs the same birth data through the engine once per variant. Only calculation settings can vary."""
    b = body.birth
    results = []
    for v in body.variants:
        settings = _apply(b.settings.to_calc(), v.options)
        chart = chart_service.calculate(get_engine, b.date, b.time, b.timezone, b.utc_offset_minutes,
                                        b.latitude, b.longitude, settings)
        moon = next(p for p in chart.planets if p.id == "moon")
        results.append(LabResult(
            label=v.label,
            summary=f"Ascendant {chart.ascendant_sign} {chart.ascendant_longitude % 30:.2f}°; "
                    f"Moon {moon.sign} {moon.degree_in_sign:.2f}° (house {moon.house})",
            data={"settings": CalculationSettings(zodiac=settings.zodiac, ayanamsa=settings.ayanamsa,
                                                  house_system=settings.house_system,
                                                  node_type=settings.node_type).model_dump(by_alias=True),
                  "ayanamsaValue": chart.ayanamsa_value,
                  "ascendant": {"sign": chart.ascendant_sign, "longitude": chart.ascendant_longitude},
                  "planets": [{"name": p.name, "sign": p.sign, "degreeInSign": p.degree_in_sign,
                               "house": p.house, "retrograde": p.retrograde} for p in chart.planets]}))
    return LabResponse(results=results)

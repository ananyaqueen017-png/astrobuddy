from app.schemas.chart import BirthInput
from app.services.astro import chart_service
from app.services.astro.factory import get_engine
from app.services.astro.models import ChartResult


def compute_chart(birth: BirthInput) -> ChartResult:
    """Validate input, convert local time to UTC, and run the calculation engine."""
    return chart_service.calculate(get_engine, birth.date, birth.time, birth.timezone, birth.utc_offset_minutes,
                                   birth.latitude, birth.longitude, birth.settings.to_calc())

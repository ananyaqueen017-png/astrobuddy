from fastapi import APIRouter

from app.schemas.chart import BirthInput, ChartResponse
from ._common import compute_chart

router = APIRouter(prefix="/charts", tags=["charts"])


@router.post("/calculate", response_model=ChartResponse, summary="Calculate a birth chart")
def calculate_chart(body: BirthInput):
    """Convert local birth time to UTC (IANA rules) and calculate positions with the configured engine.
    The calculation settings are required and echoed back with the engine that produced the result."""
    return ChartResponse.of(compute_chart(body))

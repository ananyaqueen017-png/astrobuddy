import uuid
from typing import Optional

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.schemas.features import AskRequest, AskResponse, ChartFactor
from app.services import ask_service
from app.services.astro import chart_service
from app.services.astro.facts import build_chart_facts
from app.services.llm.base import LLMError, LLMProvider
from app.services.llm.factory import build_provider
from ._common import compute_chart

router = APIRouter(tags=["ask"])


def get_llm_provider_dep(settings: Settings = Depends(get_settings)) -> LLMProvider:
    provider = build_provider(settings)
    if provider is None:
        raise AppError(503, "llm_not_configured",
                       "Ask Your Kundli needs an AI provider. Set LLM_PROVIDER, ANTHROPIC_API_KEY and "
                       "LLM_MODEL in backend/.env. Chart calculation works without them.")
    return provider


@router.post("/ask", response_model=AskResponse, summary="Ask a question grounded in calculated chart facts")
def ask(body: AskRequest, provider: LLMProvider = Depends(get_llm_provider_dep),
        settings: Settings = Depends(get_settings)):
    """The engine computes the chart (and dasha when sidereal); the LLM only interprets those facts.
    The conversation is stateless on the server in this version (no history is stored)."""
    chart = compute_chart(body.birth)
    major: Optional[str] = None
    sub: Optional[str] = None
    if chart.settings.zodiac == "sidereal":
        _, (md, sd), _ = chart_service.dasha_for(chart, settings.dasha_year_days)
        major, sub = (md.planet if md else None), (sd.planet if sd else None)
    facts = build_chart_facts(chart, major, sub)
    try:
        answer, factors, grounded = ask_service.answer_question(provider, facts, body.question)
    except LLMError as e:
        raise AppError(e.status_code, "llm_provider_error", e.message)
    return AskResponse(conversation_id=body.conversation_id or str(uuid.uuid4()), answer=answer,
                       chart_factors=[ChartFactor(label=l, detail=d) for l, d in factors],
                       grounded=grounded, disclaimer=ask_service.DISCLAIMER)

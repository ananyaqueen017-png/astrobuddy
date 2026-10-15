from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.services.astro.factory import engine_status

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: str
    version: str
    engine: dict
    llm_configured: bool
    auth_configured: bool
    database_configured: bool


@router.get("/health", response_model=HealthOut)
def health(settings: Settings = Depends(get_settings)):
    from app import __version__
    return HealthOut(
        status="ok", version=__version__, engine=engine_status(),
        llm_configured=bool(settings.llm_provider and settings.llm_model and settings.anthropic_api_key),
        auth_configured=bool(settings.supabase_jwt_secret),
        database_configured=bool(settings.database_url),
    )

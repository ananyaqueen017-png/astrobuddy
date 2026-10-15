"""Endpoints the frontend already calls but that are NOT implemented. They answer 501, never fake data."""
from fastapi import APIRouter, Depends

from app.core.auth import require_user_id
from app.core.errors import AppError

router = APIRouter(tags=["not-implemented"])


def _na(feature: str, needs: str):
    raise AppError(501, "not_implemented", f"{feature} is not implemented yet. {needs}")


@router.get("/journal", summary="[Not implemented] List journal entries")
def list_journal():
    _na("Journal", "It needs authenticated users and database persistence (see app/db/migrations).")


@router.post("/journal", summary="[Not implemented] Create a journal entry")
def create_journal():
    _na("Journal", "It needs authenticated users and database persistence (see app/db/migrations).")


@router.get("/calendar", summary="[Not implemented] Monthly calendar entries")
def calendar():
    _na("Astro Calendar", "It needs event generation (ingresses, stations) built on the transit engine.")


@router.post("/compatibility", summary="[Not implemented] Compare two charts")
def compatibility():
    _na("Compatibility", "It needs a documented, tested scoring rule set (e.g. Ashtakoota) before it can be offered.")


@router.get("/me", summary="Current authenticated user id (works once Supabase JWT auth is configured)")
def me(user_id: str = Depends(require_user_id)):
    return {"userId": user_id}

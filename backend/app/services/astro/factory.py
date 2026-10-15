from functools import lru_cache

from app.core.config import get_settings
from .errors import EngineUnavailableError


@lru_cache(maxsize=1)
def _build():
    from .swiss import SwissEphemerisEngine  # lazy: pyswisseph may be missing
    s = get_settings()
    return SwissEphemerisEngine(ephe_path=s.swe_ephe_path, mode=s.ephemeris_mode)


def get_engine():
    """Raises EngineUnavailableError when the engine cannot be loaded."""
    return _build()


def engine_status() -> dict:
    try:
        e = get_engine()
        return {"available": True, "name": e.name, "version": e.version}
    except EngineUnavailableError as exc:
        return {"available": False, "name": None, "version": None, "error": str(exc)}

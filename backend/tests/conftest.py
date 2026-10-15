import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app
from app.services.astro.factory import engine_status

ENGINE_AVAILABLE = engine_status()["available"]
needs_engine = pytest.mark.skipif(not ENGINE_AVAILABLE, reason="pyswisseph is not installed")


@pytest.fixture
def settings():
    # _env_file=None: tests must not depend on the developer's real .env
    return Settings(_env_file=None, llm_provider="", anthropic_api_key="", llm_model="",
                    supabase_jwt_secret="", database_url="")


@pytest.fixture
def app(settings):
    application = create_app()
    application.dependency_overrides[get_settings] = lambda: settings
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


def birth(**overrides):
    """A valid request body in the frontend's camelCase shape (Gwalior, 1 Jan 2000 12:00 IST)."""
    body = {"name": "Test", "date": "2000-01-01", "time": "12:00", "latitude": 26.2183, "longitude": 78.1828,
            "timezone": "Asia/Kolkata",
            "settings": {"zodiac": "sidereal", "ayanamsa": "lahiri", "houseSystem": "whole_sign",
                         "nodeType": "mean"}}
    body.update(overrides)
    return body

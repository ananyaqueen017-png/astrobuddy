"""Foundation tests that do not need the calculation engine."""
from tests.conftest import birth


def test_health_both_paths(client):
    for path in ("/health", "/api/v1/health"):
        r = client.get(path)
        assert r.status_code == 200 and r.json()["status"] == "ok"
        assert "available" in r.json()["engine"]
        assert r.json()["llm_configured"] is False


def test_docs_and_openapi_available(client):
    assert client.get("/docs").status_code == 200
    assert "/api/v1/charts/calculate" in client.get("/openapi.json").json()["paths"]


def test_cors_preflight_allows_local_frontend(client):
    r = client.options("/api/v1/charts/calculate", headers={
        "Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
    r = client.options("/api/v1/charts/calculate", headers={
        "Origin": "http://evil.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in r.headers


def _post(client, **overrides):
    return client.post("/api/v1/charts/calculate", json=birth(**overrides))


def test_latitude_out_of_range_returns_field_error(client):
    r = _post(client, latitude=123)
    assert r.status_code == 422 and "latitude" in r.json()["fieldErrors"]
    assert r.json()["code"] == "validation_error"


def test_missing_settings_is_rejected_not_defaulted(client):
    body = birth()
    del body["settings"]
    r = client.post("/api/v1/charts/calculate", json=body)
    assert r.status_code == 422 and "settings" in r.json()["fieldErrors"]


def test_bad_date_and_time_formats(client):
    assert "date" in _post(client, date="01-01-2000").json()["fieldErrors"]
    assert "time" in _post(client, time="noon").json()["fieldErrors"]


def test_unknown_timezone(client):
    r = _post(client, timezone="Mars/Olympus")
    assert r.status_code == 422 and "timezone" in r.json()["fieldErrors"]


def test_ambiguous_local_time(client):
    r = _post(client, date="2021-11-07", time="01:30", timezone="America/New_York")
    assert r.status_code == 422 and "time" in r.json()["fieldErrors"]


def test_sidereal_requires_ayanamsa_and_tropical_rejects_it(client):
    s = {"zodiac": "sidereal", "ayanamsa": None, "houseSystem": "whole_sign", "nodeType": "mean"}
    assert "ayanamsa" in _post(client, settings=s).json()["fieldErrors"]
    s = {"zodiac": "tropical", "ayanamsa": "lahiri", "houseSystem": "placidus", "nodeType": "mean"}
    assert "ayanamsa" in _post(client, settings=s).json()["fieldErrors"]


def test_placidus_rejected_near_polar_circle(client):
    s = {"zodiac": "tropical", "ayanamsa": None, "houseSystem": "placidus", "nodeType": "mean"}
    r = _post(client, settings=s, latitude=70.0)
    assert r.status_code == 422 and "houseSystem" in r.json()["fieldErrors"]


def test_year_out_of_supported_range(client):
    assert "date" in _post(client, date="1700-01-01").json()["fieldErrors"]


def test_dasha_requires_sidereal(client):
    s = {"zodiac": "tropical", "ayanamsa": None, "houseSystem": "whole_sign", "nodeType": "mean"}
    r = client.post("/api/v1/dashas", json=birth(settings=s))
    assert r.status_code == 422 and "zodiac" in r.json()["fieldErrors"]


def test_ask_returns_503_when_llm_not_configured(client):
    r = client.post("/api/v1/ask", json={"birth": birth(), "question": "What does my Moon say?"})
    assert r.status_code == 503 and r.json()["code"] == "llm_not_configured"


def test_unimplemented_features_answer_501_not_fake_data(client):
    for method, path in (("get", "/journal"), ("post", "/journal"), ("get", "/calendar"), ("post", "/compatibility")):
        r = getattr(client, method)(f"/api/v1{path}")
        assert r.status_code == 501 and r.json()["code"] == "not_implemented"


def test_auth_paths(client, settings):
    assert client.get("/api/v1/me").status_code == 503  # secret not configured
    settings.supabase_jwt_secret = "s3cret"
    assert client.get("/api/v1/me").status_code == 401
    assert client.get("/api/v1/me", headers={"Authorization": "Bearer garbage"}).status_code == 401

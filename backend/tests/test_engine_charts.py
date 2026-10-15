"""End-to-end tests that need pyswisseph. They check invariants and coarse sanity values only.
They do NOT prove numerical accuracy; see tests/fixtures/reference_charts.json and the README."""
import pytest

from tests.conftest import birth, needs_engine

pytestmark = needs_engine
TROPICAL = {"zodiac": "tropical", "ayanamsa": None, "houseSystem": "placidus", "nodeType": "mean"}


def _chart(client, **kw):
    r = client.post("/api/v1/charts/calculate", json=birth(**kw))
    assert r.status_code == 200, r.text
    return r.json()


def test_j2000_sun_and_ayanamsa_sanity(client):
    # 2000-01-01 12:00 UTC. The Sun's apparent tropical longitude is about 280.37° (Astronomical Almanac).
    c = _chart(client, timezone="UTC", settings=TROPICAL)
    sun = next(p for p in c["planets"] if p["id"] == "sun")
    assert abs(sun["longitude"] - 280.37) < 0.05
    sid = _chart(client, timezone="UTC")
    assert 23.83 < sid["ayanamsaValue"] < 23.89  # Lahiri ayanamsa at J2000 is about 23.86°
    sid_sun = next(p for p in sid["planets"] if p["id"] == "sun")
    assert abs((sun["longitude"] - sid["ayanamsaValue"]) % 360 - sid_sun["longitude"]) < 0.02


def test_structure_and_echoed_settings(client):
    c = _chart(client)
    assert [p["id"] for p in c["planets"]] == ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
    assert len(c["houses"]) == 12 and all(1 <= p["house"] <= 12 for p in c["planets"])
    assert c["settings"] == {"zodiac": "sidereal", "ayanamsa": "lahiri", "houseSystem": "whole_sign", "nodeType": "mean"}
    assert c["engine"]["name"] and c["engine"]["ephemeris"] and c["birthUtc"].startswith("2000-01-01T06:30")
    rahu, ketu = c["planets"][7], c["planets"][8]
    assert abs((rahu["longitude"] - ketu["longitude"]) % 360 - 180) < 1e-6
    assert rahu["retrograde"] and ketu["retrograde"]  # mean nodes always move backward
    assert not c["planets"][0]["retrograde"] and not c["planets"][1]["retrograde"]
    for p in c["planets"]:
        assert p["sign"] and 0 <= p["degreeInSign"] < 30 and p["nakshatra"]


def test_whole_sign_houses_start_at_sign_boundaries(client):
    c = _chart(client)
    assert all(abs(h["cuspLongitude"] % 30) < 1e-9 for h in c["houses"])
    assert c["houses"][0]["sign"] == c["ascendantSign"]
    assert int(c["ascendantLongitude"] // 30) == int(c["houses"][0]["cuspLongitude"] // 30)


def test_tropical_has_no_nakshatra_and_zero_ayanamsa_value(client):
    c = _chart(client, settings=TROPICAL)
    assert c["ayanamsaValue"] is None and c["planets"][0]["nakshatra"] is None


def test_zodiac_choice_changes_longitudes_by_the_ayanamsa(client):
    t = _chart(client, settings=TROPICAL)
    s = _chart(client)
    diff = (t["planets"][1]["longitude"] - s["planets"][1]["longitude"]) % 360
    assert abs(diff - s["ayanamsaValue"]) < 0.02


def test_historical_timezone_rule_is_applied(client):
    c = _chart(client, date="1943-06-01")
    assert c["utcOffsetMinutes"] == 390 and c["birthUtc"].startswith("1943-06-01T05:30")


def test_dashas_endpoint(client):
    r = client.post("/api/v1/dashas", json={**birth(), "asOf": "2026-01-01"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["system"] == "vimshottari" and len(d["periods"]) == 9 and d["yearLengthDays"] == 365.25
    assert d["periods"][0]["planet"] in ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")
    for a, b in zip(d["periods"], d["periods"][1:]):
        assert a["end"] == b["start"] and len(a["subPeriods"]) >= 1
    assert d["current"]["major"] and d["asOf"] == "2026-01-01"


def test_transits_endpoint(client):
    r = client.post("/api/v1/transits", json={"birth": birth(), "date": "2026-10-14"})
    assert r.status_code == 200, r.text
    t = r.json()
    assert len(t["planets"]) == 9 and all(1 <= p["house"] <= 12 for p in t["planets"])
    assert t["computedAtUtc"].startswith("2026-10-14T12:00") and t["orbDegrees"] == 3.0
    assert any(h["title"].startswith("Transit Saturn") for h in t["highlights"])


def test_lab_compares_settings(client):
    body = {"birth": birth(), "variants": [
        {"label": "Lahiri", "options": {}},
        {"label": "Raman", "options": {"ayanamsa": "raman"}},
        {"label": "Tropical", "options": {"zodiac": "tropical", "houseSystem": "placidus"}}]}
    r = client.post("/api/v1/lab/compare", json=body)
    assert r.status_code == 200, r.text
    results = r.json()["results"]
    assert [x["label"] for x in results] == ["Lahiri", "Raman", "Tropical"]
    assert results[0]["data"]["ayanamsaValue"] != results[1]["data"]["ayanamsaValue"]
    assert results[2]["data"]["settings"]["ayanamsa"] is None
    bad = client.post("/api/v1/lab/compare", json={"birth": birth(), "variants": [{"label": "x", "options": {"foo": 1}}]})
    assert bad.status_code == 422


class FakeProvider:
    def __init__(self, reply):
        self.reply, self.last_user = reply, None

    def complete(self, system, user):
        self.last_user = user
        return self.reply


def test_ask_is_grounded_in_engine_facts(app, client):
    from app.routers.ask import get_llm_provider_dep
    fake = FakeProvider('{"answer": "A reflective reading.", "usedFactIds": ["F2", "F999"]}')
    app.dependency_overrides[get_llm_provider_dep] = lambda: fake
    r = client.post("/api/v1/ask", json={"birth": birth(), "question": "Tell me about my ascendant"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["answer"] == "A reflective reading." and d["grounded"] is True and d["conversationId"]
    assert [f["label"] for f in d["chartFactors"]] == ["Ascendant"]  # F999 ignored
    assert "F2: Ascendant:" in fake.last_user and "Vimshottari" in fake.last_user and "disclaimer" in d


def test_ask_provider_failure_is_reported(app, client):
    from app.routers.ask import get_llm_provider_dep
    from app.services.llm.base import LLMError

    class Broken:
        def complete(self, system, user):
            raise LLMError(504, "timed out")

    app.dependency_overrides[get_llm_provider_dep] = lambda: Broken()
    r = client.post("/api/v1/ask", json={"birth": birth(), "question": "Hello there"})
    assert r.status_code == 504 and r.json()["code"] == "llm_provider_error"

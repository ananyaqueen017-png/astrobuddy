"""Dependency-free tests: time conversion, houses, dasha rules, JWT. Runnable with pytest or plain python."""
import base64, hashlib, hmac, json
from datetime import date, datetime, time, timedelta, timezone

from app.core.jwt_hs256 import JWTError, verify_hs256
from app.services.astro import dasha, houses, transits, zodiac
from app.services.astro.errors import AstroInputError
from app.services.astro.facts import build_chart_facts
from app.services.astro.models import BirthMoment, CalcSettings, ChartResult, PlanetResult
from app.services.astro.timeutil import resolve_birth_moment

BIRTH = datetime(1990, 1, 1, tzinfo=timezone.utc)


def _raises(field, fn):
    try:
        fn()
    except AstroInputError as e:
        assert e.field == field
        return
    raise AssertionError("expected AstroInputError")


# --- time zones -------------------------------------------------------------------------
def test_modern_offset():
    m = resolve_birth_moment(date(1990, 6, 1), time(12, 0), "Asia/Kolkata")
    assert m.utc_offset_minutes == 330 and m.utc.hour == 6 and m.utc.minute == 30


def test_historical_wartime_offset_is_applied():
    m = resolve_birth_moment(date(1943, 6, 1), time(12, 0), "Asia/Kolkata")
    assert m.utc_offset_minutes == 390  # +06:30 per the tz database


def test_local_mean_time_warning():
    m = resolve_birth_moment(date(1890, 6, 1), time(12, 0), "Asia/Kolkata")
    assert m.warnings and m.utc_offset_minutes % 1 != 0


def test_ambiguous_time_rejected_and_manual_offset_accepted():
    _raises("time", lambda: resolve_birth_moment(date(2021, 11, 7), time(1, 30), "America/New_York"))
    m = resolve_birth_moment(date(2021, 11, 7), time(1, 30), "America/New_York", -300)
    assert m.utc.hour == 6 and m.offset_source == "manual_offset"


def test_nonexistent_time_rejected():
    _raises("time", lambda: resolve_birth_moment(date(2021, 3, 14), time(2, 30), "America/New_York"))


def test_unknown_timezone_rejected():
    _raises("timezone", lambda: resolve_birth_moment(date(2000, 1, 1), time(0, 0), "Mars/Olympus"))


# --- zodiac / houses --------------------------------------------------------------------
def test_signs_and_nakshatras():
    assert zodiac.sign_name(0) == "Aries" and zodiac.sign_name(359.9) == "Pisces"
    assert zodiac.nakshatra_of(0) == ("Ashwini", 1)
    assert zodiac.nakshatra_of(359.99) == ("Revati", 4)
    assert zodiac.nakshatra_of(13.4)[0] == "Bharani"


def test_whole_sign_houses():
    cusps = houses.whole_sign_cusps(250.5)  # Sagittarius
    assert cusps[0] == 240 and cusps[1] == 270 and cusps[4] == 0
    assert houses.house_of(250.5, cusps) == 1
    assert houses.house_of(239.99, cusps) == 12
    assert houses.house_of(5, cusps) == 5


def test_house_of_with_unequal_cusps_and_wraparound():
    cusps = [350, 20, 55, 90, 120, 150, 170, 200, 235, 270, 300, 325]
    assert houses.house_of(355, cusps) == 1
    assert houses.house_of(10, cusps) == 1
    assert houses.house_of(25, cusps) == 2
    assert houses.house_of(340, cusps) == 12


def test_conjunction_orb_wraps_around_zero():
    found = transits.find_conjunctions({"Sun": 0.5}, {"Mars": 359.5, "Moon": 10}, 3.0)
    assert found == [("Mars", "Sun", 1.0)]


# --- vimshottari ------------------------------------------------------------------------
def test_balance_at_birth():
    assert abs(dasha.build_vimshottari(0.0, BIRTH).balance_at_birth_years - 7.0) < 1e-9
    r = dasha.build_vimshottari(40 / 6.0, BIRTH)  # half of Ashwini
    assert r.birth_lord == "Ketu" and abs(r.balance_at_birth_years - 3.5) < 1e-9
    r = dasha.build_vimshottari(40 / 3.0 + 1e-6, BIRTH)  # start of Bharani
    assert r.birth_lord == "Venus" and abs(r.balance_at_birth_years - 20.0) < 1e-3
    assert dasha.build_vimshottari(120.0, BIRTH).birth_lord == "Ketu"  # Magha repeats the cycle


def test_sequence_and_contiguity():
    r = dasha.build_vimshottari(100.0, BIRTH)  # Pushya -> Saturn
    assert r.birth_lord == "Saturn"
    assert [p.planet for p in r.periods][:3] == ["Saturn", "Mercury", "Ketu"]
    for a, b in zip(r.periods, r.periods[1:]):
        assert a.end == b.start
        for x, y in zip(a.sub_periods, a.sub_periods[1:]):
            assert x.end == y.start


def test_subperiods_sum_to_mahadasha_and_follow_rules():
    r = dasha.build_vimshottari(0.0, BIRTH)  # elapsed fraction 0 -> full first dasha
    venus = r.periods[1]
    assert venus.planet == "Venus"
    assert [s.planet for s in venus.sub_periods][:2] == ["Venus", "Sun"]
    total = sum((s.end - s.start for s in venus.sub_periods), timedelta())
    assert abs(total.total_seconds() - 20 * 365.25 * 86400) < 1
    first_sub = venus.sub_periods[0]  # Venus/Venus = 20*20/120 years
    assert abs((first_sub.end - first_sub.start).total_seconds() - (400 / 120) * 365.25 * 86400) < 1


def test_first_period_is_clipped_at_birth():
    r = dasha.build_vimshottari(40 / 6.0, BIRTH)
    first = r.periods[0]
    assert first.starts_before_birth and first.start == BIRTH
    assert first.sub_periods[0].start == BIRTH
    assert abs((first.end - BIRTH).total_seconds() - 3.5 * 365.25 * 86400) < 1


def test_cycle_covers_120_years_minus_elapsed_and_year_length_is_configurable():
    r = dasha.build_vimshottari(0.0, BIRTH)
    assert abs((r.periods[-1].end - BIRTH).total_seconds() - 120 * 365.25 * 86400) < 1
    r2 = dasha.build_vimshottari(0.0, BIRTH, year_days=360.0)
    assert r2.year_days == 360.0 and abs((r2.periods[-1].end - BIRTH).total_seconds() - 120 * 360 * 86400) < 1


def test_current_periods():
    r = dasha.build_vimshottari(0.0, BIRTH)
    md, sd = dasha.current_periods(r, BIRTH + timedelta(days=8 * 365))
    assert md.planet == "Venus" and sd is not None
    assert dasha.current_periods(r, BIRTH + timedelta(days=200 * 365)) == (None, None)


# --- facts ------------------------------------------------------------------------------
def test_chart_facts_are_numbered_and_include_dasha():
    p = PlanetResult("moon", "Moon", 100.0, "Cancer", 10.0, 8, False, 13.0, "Pushya", 1)
    chart = ChartResult(BirthMoment(BIRTH, 0, "UTC", "timezone"), 0, 0,
                        CalcSettings("sidereal", "lahiri", "whole_sign", "mean"),
                        250.5, "Sagittarius", [p], [], 24.0, 0.0, "e", "1", "x")
    facts = build_chart_facts(chart, "Venus", "Sun")
    assert [f[0] for f in facts] == ["F1", "F2", "F3", "F4"]
    assert "Sagittarius" in facts[1][2] and "Pushya" in facts[2][2] and "Venus" in facts[3][2]


# --- jwt --------------------------------------------------------------------------------
def _token(secret, **claims):
    enc = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()
    h = enc({"alg": claims.pop("alg", "HS256"), "typ": "JWT"})
    p = enc(claims)
    sig = hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{base64.urlsafe_b64encode(sig).rstrip(b'=').decode()}"


def _jwt_fails(token, secret="s3cret"):
    try:
        verify_hs256(token, secret, now=1000)
    except JWTError:
        return True
    return False


def test_jwt_verification():
    good = _token("s3cret", sub="user-1", aud="authenticated", exp=2000)
    assert verify_hs256(good, "s3cret", now=1000)["sub"] == "user-1"
    assert _jwt_fails(good, "other-secret")
    assert _jwt_fails(_token("s3cret", sub="u", aud="authenticated", exp=500))
    assert _jwt_fails(_token("s3cret", sub="u", aud="other", exp=2000))
    assert _jwt_fails(_token("s3cret", alg="none", sub="u", aud="authenticated", exp=2000))
    assert _jwt_fails("not-a-token")


# --- highlights / ask parsing -----------------------------------------------------------
def _p(pid, name, lon, house=1, retro=False):
    return PlanetResult(pid, name, lon, zodiac.sign_name(lon), zodiac.degree_in_sign(lon), house, retro, 1.0)


def test_highlights_are_factual_and_sorted():
    natal = [_p("moon", "Moon", 100.0)]
    moving = [_p("saturn", "Saturn", 101.0, 8, True), _p("sun", "Sun", 200.0)]
    h = transits.build_highlights(natal, moving, 3.0)
    assert h[0]["title"] == "Transit Saturn in natal house 8" and "retrograde" in h[0]["explanation"]
    assert h[1]["title"] == "Transiting Saturn conjunct natal Moon"
    assert len(h) == 2


def test_parse_reply_filters_unknown_fact_ids_and_handles_bad_json():
    from app.services.ask_service import parse_reply
    facts = [("F1", "Ascendant", "Ascendant: Leo"), ("F2", "Moon", "Moon: Cancer")]
    ans, factors, grounded = parse_reply('```json\n{"answer": "Hi", "usedFactIds": ["F2", "F9", "F2"]}\n```', facts)
    assert ans == "Hi" and factors == [("Moon", "Moon: Cancer")] and grounded
    ans, factors, grounded = parse_reply("plain text", facts)
    assert ans == "plain text" and factors == [] and not grounded

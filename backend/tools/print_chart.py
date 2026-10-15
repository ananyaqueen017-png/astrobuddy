"""Print engine output for comparison with a trusted reference.
Example (PowerShell, from backend/):
  python tools/print_chart.py --date 2000-01-01 --time 12:00 --tz Asia/Kolkata --lat 26.2183 --lon 78.1828
"""
import argparse
import sys
from datetime import date, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.astro import chart_service  # noqa: E402
from app.services.astro.factory import get_engine  # noqa: E402
from app.services.astro.models import CalcSettings  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--date", required=True)
p.add_argument("--time", required=True)
p.add_argument("--tz", required=True)
p.add_argument("--lat", type=float, required=True)
p.add_argument("--lon", type=float, required=True)
p.add_argument("--zodiac", default="sidereal", choices=["sidereal", "tropical"])
p.add_argument("--ayanamsa", default="lahiri")
p.add_argument("--house-system", default="whole_sign")
p.add_argument("--nodes", default="mean", choices=["mean", "true"])
a = p.parse_args()

s = CalcSettings(a.zodiac, a.ayanamsa if a.zodiac == "sidereal" else None, a.house_system, a.nodes)
c = chart_service.calculate(get_engine, date.fromisoformat(a.date), time.fromisoformat(a.time), a.tz, None,
                            a.lat, a.lon, s)
print(f"Engine: {c.engine_name} [{c.engine_version}] ephemeris={c.ephemeris}")
print(f"UTC: {c.birth.utc.isoformat()} (offset {c.birth.utc_offset_minutes:g} min)  JD(UT)={c.julian_day_ut:.6f}")
print(f"Settings: {s}  ayanamsa={c.ayanamsa_value}")
print(f"Ascendant: {c.ascendant_longitude:.6f}  ({c.ascendant_sign})")
for pl in c.planets:
    print(f"{pl.name:8s} {pl.longitude:11.6f}  {pl.sign:12s} house {pl.house:2d}  {'R' if pl.retrograde else ' '}  {pl.nakshatra or ''}")

# AstroBuddy backend (FastAPI)

Real chart calculation (Swiss Ephemeris), Vimshottari dasha, transits, a settings-comparison lab and an
optional AI endpoint. Everything else is scaffolding that answers **501 Not Implemented** (never fake data).

## Windows PowerShell: install and run

Requires Python 3.11 or 3.12 (64-bit). `pyswisseph` ships Windows wheels for common Python versions; if pip
tries to compile it and fails, install "Microsoft C++ Build Tools" or use a supported Python version.

```powershell
cd F:\astrobuddy\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # if blocked: Set-ExecutionPolicy -Scope Process Bypass
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env         # optional: every value may stay empty
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs (interactive API docs) and http://localhost:8000/health.
`/health` reports whether the engine loaded; if it says unavailable, the message says why.

Frontend (second terminal):
```powershell
cd F:\astrobuddy
Copy-Item .env.example .env.local -Force   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
npm install
npm run dev
```
Check the connection under Settings in the app; the status pill should read "Backend reachable".

## Tests
```powershell
cd F:\astrobuddy\backend
.\.venv\Scripts\Activate.ps1
python -m pytest -v                         # engine tests are skipped automatically if pyswisseph is missing
python tools\print_chart.py --date 2000-01-01 --time 12:00 --tz Asia/Kolkata --lat 26.2183 --lon 78.1828
cd ..; npm run typecheck; npm run build
```

## Design
| Folder | Purpose |
|---|---|
| `app/routers` | HTTP layer under `/api/v1` (plus plain `/health`) |
| `app/schemas` | Pydantic models; JSON is camelCase to match the frontend types |
| `app/services/astro` | `swiss.py` engine adapter (replaceable), `timeutil`, `houses`, `dasha`, `transits`, `facts` |
| `app/services/llm` | Optional provider interface (Anthropic implemented, backend-only key) |
| `app/core` | settings, error handlers, Supabase JWT check (HS256) |
| `app/db/migrations` | Supabase/PostgreSQL schema with row-level security (not applied here) |

Calculation settings are **required in every request** and echoed in every response with the engine name,
version and ephemeris mode. Nothing is assumed silently: zodiac (sidereal/tropical), ayanamsa, house system
and node type come from the user (the form pre-fills Vedic defaults you can see and change).

Conventions you should know about:
- Local time to UTC uses the IANA tz database (historical rules, e.g. India's +06:30 in 1943). Ambiguous and
  non-existent local times (DST changes) are rejected unless you pass `utcOffsetMinutes`. Dates before standardized
  time zones use local mean time and return a warning.
- Planet positions are geocentric apparent longitudes. Rahu/Ketu use mean nodes by default (`nodeType: "true"` optional).
  Retrograde = negative longitudinal speed (mean nodes are therefore always retrograde).
- Whole-sign houses start at 0° of the ascendant's sign. Placidus/Koch are rejected beyond 66° latitude.
- Vimshottari: 27 nakshatras from 0° sidereal, standard lord order and 120-year cycle. Year length is a convention
  (`DASHA_YEAR_DAYS`, default 365.25) and is returned with each result. Requires a sidereal zodiac.
- Transits are computed for 12:00 UTC on the requested date and placed in the natal houses. Highlights list only
  positions and conjunctions within `TRANSIT_ORB_DEGREES`; they contain no interpretation.
- Supported birth years: 1800-2200.

## Verifying accuracy (you must do this)
The bundled tests check invariants (nine bodies, Rahu/Ketu opposite, houses consistent, tz rules, dasha rules) and a
coarse J2000 sanity value. They do **not** prove positions are accurate.
1. Pick 3-5 birth data sets, including one before 1950 and one near a DST change.
2. Compute them in a trusted reference using identical settings (Swiss Ephemeris `swetest`, Jagannatha Hora, astro.com).
3. Add them to `tests/fixtures/reference_charts.json` (format in `_exampleCase`) and run `pytest`. Tolerance defaults to 0.01°.
4. Compare `tools/print_chart.py` output side by side to see which field differs if one fails.

## Licensing and limits you must resolve
- **Swiss Ephemeris / pyswisseph is AGPL or a paid Astrodienst professional license.** Offering AstroBuddy to the public
  as a network service generally triggers AGPL source-disclosure duties unless you hold the commercial license.
  Read https://www.astro.com/swisseph/ before deploying.
- Without ephemeris data files the engine uses the built-in Moshier fallback (reported in `engine.ephemeris`). Download the
  data files and set `SWE_EPHE_PATH` if you want file-based results.
- The Anthropic provider is optional and uses your own key from `backend/.env`. The key never reaches the browser.
  Ask Your Kundli is stateless (no history stored) and rate limiting is not implemented.
- Supabase: `core/auth.py` verifies legacy HS256 JWTs only. Projects using asymmetric signing keys need JWKS verification.
  Persistence endpoints (journal, saved charts, conversations) are not implemented, and the SQL schema has not been applied or tested.
- Production needs HTTPS, a restricted `CORS_ORIGINS`, request rate limiting and a privacy review of stored birth data.

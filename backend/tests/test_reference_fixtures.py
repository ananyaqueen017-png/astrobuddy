import json
from pathlib import Path

import pytest

from tests.conftest import needs_engine

_DATA = json.loads((Path(__file__).parent / "fixtures" / "reference_charts.json").read_text(encoding="utf-8"))
_CASES = _DATA["cases"]


@needs_engine
@pytest.mark.skipif(not _CASES, reason="No reference cases added yet (see README: Verifying accuracy)")
@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_matches_trusted_reference(client, case):
    r = client.post("/api/v1/charts/calculate", json=case["birth"])
    assert r.status_code == 200, r.text
    chart, tol = r.json(), _DATA["toleranceDegrees"]
    diff = lambda a, b: abs((a - b + 180) % 360 - 180)  # noqa: E731
    exp = case["expected"]
    if "ascendantLongitude" in exp:
        assert diff(chart["ascendantLongitude"], exp["ascendantLongitude"]) <= tol
    got = {p["id"]: p["longitude"] for p in chart["planets"]}
    for pid, lon in exp.get("planets", {}).items():
        assert diff(got[pid], lon) <= tol, f"{pid}: {got[pid]} vs {lon}"

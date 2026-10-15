from .zodiac import sign_index


def whole_sign_cusps(asc_longitude: float) -> list:
    """Whole-sign houses: house 1 begins at 0° of the ascendant's sign."""
    start = sign_index(asc_longitude) * 30.0
    return [(start + 30.0 * i) % 360.0 for i in range(12)]


def house_of(longitude: float, cusps: list) -> int:
    """House (1-12) containing `longitude`, given 12 ascending-order cusp longitudes."""
    lon = longitude % 360.0
    for i in range(12):
        start = cusps[i] % 360.0
        end = cusps[(i + 1) % 12] % 360.0
        span = (end - start) % 360.0 or 360.0
        if (lon - start) % 360.0 < span:
            return i + 1
    return 12


def angular_separation(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)

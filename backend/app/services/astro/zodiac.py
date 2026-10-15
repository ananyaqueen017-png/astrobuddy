SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# 27 equal divisions of 13°20' each, starting at 0° of the (sidereal) zodiac.
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]


def normalize(lon: float) -> float:
    return lon % 360.0


def sign_index(lon: float) -> int:
    return int(normalize(lon) // 30) % 12


def sign_name(lon: float) -> str:
    return SIGNS[sign_index(lon)]


def degree_in_sign(lon: float) -> float:
    return normalize(lon) % 30.0


def nakshatra_of(lon: float):
    """Return (name, pada 1-4) for a sidereal longitude."""
    pos = normalize(lon) * 27.0 / 360.0
    idx = min(int(pos), 26)
    pada = min(int((pos - idx) * 4.0), 3) + 1
    return NAKSHATRAS[idx], pada

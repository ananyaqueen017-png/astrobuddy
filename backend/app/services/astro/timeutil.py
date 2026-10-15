"""Local birth time -> UTC, using the IANA tz database (historical rules included)."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .errors import AstroInputError
from .models import BirthMoment


def resolve_birth_moment(d: date, t: time, tz_name: str, utc_offset_minutes=None) -> BirthMoment:
    naive = datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)

    if utc_offset_minutes is not None:
        utc = (naive - timedelta(minutes=utc_offset_minutes)).replace(tzinfo=timezone.utc)
        return BirthMoment(utc, float(utc_offset_minutes), tz_name, "manual_offset",
                           ("Manual UTC offset used; the time zone's rules were not applied.",))

    try:
        zone = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        raise AstroInputError(
            "timezone",
            f"Unknown time zone '{tz_name}'. Use an IANA name such as Asia/Kolkata "
            "(on Windows, make sure the 'tzdata' package is installed).",
        )

    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    if first.utcoffset() != second.utcoffset():
        raise AstroInputError(
            "time",
            "This local time occurred twice because clocks were set back. "
            "Provide an explicit UTC offset (utcOffsetMinutes) to say which one is correct.",
        )
    roundtrip = first.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None)
    if roundtrip != naive:
        raise AstroInputError(
            "time",
            "This local time did not exist because clocks were set forward. "
            "Check the birth time or provide an explicit UTC offset (utcOffsetMinutes).",
        )

    offset = first.utcoffset()
    warnings = []
    if offset.total_seconds() % 60 != 0:
        warnings.append("This date predates standardized time zones; local mean time offset was applied.")
    utc = first.astimezone(timezone.utc)
    return BirthMoment(utc, offset.total_seconds() / 60.0, tz_name, "timezone", tuple(warnings))

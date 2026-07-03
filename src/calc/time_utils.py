import re
from collections.abc import Callable
from datetime import timedelta
from decimal import Decimal

NUMBER = r"(\d+(?:\.\d+)?)"
DAYS = NUMBER + r" *(?:d(?:ays?)?|日(?:間)?)"
HOURS = NUMBER + r" *(?:h(?:ours?|rs?)?|時(?:間)?)"
MINUTES = NUMBER + r" *(?:m(?:in(?:utes?)?)?|分(?:間)?)"
SECONDS = NUMBER + r" *(?:s(?:ec(?:onds?)?)?|秒(?:間)?)"
TIME = r"(\d+:\d+:\d+(?:\.\d{1,6})?)"
TIME_STRICT = r"(\d+):([0-5][0-9]):([0-5][0-9])(?:\.(\d{1,6}))?"
SEPARATOR = r"(?:\s+and\s+|\s*と\s*|\s*)"
DAYS_TIME = DAYS + SEPARATOR + TIME


def _parse_time(time_str: str, days_str: str | None = None) -> str:
    """Parse time string and return timedelta constructor string"""
    time_match = re.match(TIME_STRICT, time_str)
    if not time_match:
        raise ValueError(f"Invalid time format: {time_str} (use HH:MM:SS with MM,SS as 00-59)")
    parts = []
    if days_str:
        parts.append(f"days={days_str}")
    parts.append(f"hours={int(time_match.group(1))}")
    parts.append(f"minutes={int(time_match.group(2))}")
    parts.append(f"seconds={int(time_match.group(3))}")
    if time_match.group(4):
        parts.append(f"microseconds={int(time_match.group(4).ljust(6, '0'))}")
    return f"timedelta({', '.join(parts)})"


def _timedelta_pattern(*units: str) -> tuple[str, Callable[[re.Match[str]], str]]:
    """Build a conversion entry: unit patterns joined by SEPARATOR -> timedelta constructor"""
    unit_regexes = {"days": DAYS, "hours": HOURS, "minutes": MINUTES, "seconds": SECONDS}
    pattern = SEPARATOR.join(unit_regexes[unit] for unit in units)

    def replace(m: re.Match[str]) -> str:
        args = ", ".join(f"{unit}={m.group(i + 1)}" for i, unit in enumerate(units))
        return f"timedelta({args})"

    return pattern, replace


_TIME_CONVERSION_PATTERNS = [
    _timedelta_pattern("days", "hours", "minutes", "seconds"),
    _timedelta_pattern("days", "hours", "minutes"),
    _timedelta_pattern("days", "hours", "seconds"),
    _timedelta_pattern("days", "minutes", "seconds"),
    _timedelta_pattern("hours", "minutes", "seconds"),
    _timedelta_pattern("days", "hours"),
    _timedelta_pattern("days", "minutes"),
    _timedelta_pattern("days", "seconds"),
    _timedelta_pattern("hours", "minutes"),
    _timedelta_pattern("hours", "seconds"),
    _timedelta_pattern("minutes", "seconds"),
    (DAYS_TIME, lambda m: _parse_time(m.group(2), m.group(1))),
    _timedelta_pattern("days"),
    _timedelta_pattern("hours"),
    _timedelta_pattern("minutes"),
    _timedelta_pattern("seconds"),
    (TIME, lambda m: _parse_time(m.group(1))),
]


def convert_time_expressions(expression: str) -> str:
    """Convert natural language time expressions to timedelta constructors"""
    for pattern, replacement in _TIME_CONVERSION_PATTERNS:
        expression = re.sub(pattern, replacement, expression)
    return expression


_UNIT_MICROSECONDS = {
    "sec": 1_000_000,
    "min": 60 * 1_000_000,
    "hour": 3600 * 1_000_000,
    "day": 86400 * 1_000_000,
}


def to_scalar(td: timedelta, unit: str) -> Decimal:
    """Convert timedelta to a Decimal value in the given unit"""
    total_microseconds = (td.days * 86400 + td.seconds) * 1_000_000 + td.microseconds
    return Decimal(total_microseconds) / Decimal(_UNIT_MICROSECONDS[unit])


def _format_units(
    td: timedelta, day: str, hour: str, minute: str, second: str, separator: str
) -> str:
    """Format timedelta as unit-suffixed components, omitting zero components"""
    sign = "-" if td < timedelta(0) else ""
    td = abs(td)
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if td.days:
        parts.append(f"{td.days}{day}")
    if hours:
        parts.append(f"{hours}{hour}")
    if minutes:
        parts.append(f"{minutes}{minute}")
    if td.microseconds:
        fraction = f".{td.microseconds:06d}".rstrip("0")
        parts.append(f"{seconds}{fraction}{second}")
    elif seconds or not parts:
        parts.append(f"{seconds}{second}")
    return sign + separator.join(parts)


def format_japanese(td: timedelta) -> str:
    """Format timedelta to Japanese display string (e.g. 1時間30分)"""
    return _format_units(td, "日", "時間", "分", "秒", "")


def format_english(td: timedelta) -> str:
    """Format timedelta to English display string (e.g. 1h 30m)"""
    return _format_units(td, "d", "h", "m", "s", " ")


def format_time(td: timedelta) -> str:
    """Format timedelta to display string representation"""
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    time_part = f"{hh:02d}:{mm:02d}:{ss:02d}"
    if td.microseconds:
        time_part += f".{td.microseconds:06d}"

    if td.days == 0:
        return time_part

    day_text = "day" if abs(td.days) == 1 else "days"
    if td.seconds == 0 and td.microseconds == 0:
        return f"{td.days:d} {day_text}"
    else:
        return f"{td.days:d} {day_text} and {time_part}"

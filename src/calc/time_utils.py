import re
from datetime import timedelta
from typing import Optional

NUMBER = r'(\d+(?:\.\d+)?)'
DAYS = NUMBER + r' *(?:d(?:ays?)?|日(?:間)?)'
HOURS = NUMBER + r' *(?:h(?:ours?|rs?)?|時(?:間)?)'
MINUTES = NUMBER + r' *(?:m(?:in(?:utes?)?)?|分(?:間)?)'
SECONDS = NUMBER + r' *(?:s(?:ec(?:onds?)?)?|秒(?:間)?)'
TIME = r'(\d+:\d+:\d+(?:\.\d{1,6})?)'
TIME_STRICT = r'(\d+):([0-5][0-9]):([0-5][0-9])(?:\.(\d{1,6}))?'
AND_SEPARATOR = r'(?:\s+and\s+|\s*)'
SEPARATOR = r'\s*'
DAYS_HOURS_MINUTES_SECONDS = DAYS + SEPARATOR + HOURS + SEPARATOR + MINUTES + SEPARATOR + SECONDS
DAYS_AND_HOURS_MINUTES = DAYS + AND_SEPARATOR + HOURS + SEPARATOR + MINUTES
DAYS_HOURS_SECONDS = DAYS + SEPARATOR + HOURS + SEPARATOR + SECONDS
HOURS_MINUTES_SECONDS = HOURS + SEPARATOR + MINUTES + SEPARATOR + SECONDS
DAYS_AND_HOURS = DAYS + AND_SEPARATOR + HOURS
DAYS_AND_MINUTES = DAYS + AND_SEPARATOR + MINUTES
DAYS_AND_SECONDS = DAYS + AND_SEPARATOR + SECONDS
HOURS_AND_MINUTES = HOURS + AND_SEPARATOR + MINUTES
HOURS_AND_SECONDS = HOURS + AND_SEPARATOR + SECONDS
MINUTES_AND_SECONDS = MINUTES + AND_SEPARATOR + SECONDS
DAYS_AND_TIME = DAYS + AND_SEPARATOR + TIME


def _parse_time(time_str: str, days_str: Optional[str] = None) -> str:
    """Parse time string and return timedelta constructor string"""
    time_match = re.match(TIME_STRICT, time_str)
    if not time_match:
        raise ValueError(f'Invalid time format: {time_str}')
    parts = []
    if days_str:
        parts.append(f'days={days_str}')
    parts.append(f'hours={int(time_match.group(1))}')
    parts.append(f'minutes={int(time_match.group(2))}')
    parts.append(f'seconds={int(time_match.group(3))}')
    if time_match.group(4):
        parts.append(f'microseconds={int(time_match.group(4).ljust(6, "0"))}')
    return f'timedelta({", ".join(parts)})'


_TIME_CONVERSION_PATTERNS = [
    (DAYS_HOURS_MINUTES_SECONDS,
     lambda m: (f'timedelta(days={m.group(1)}, hours={m.group(2)}, '
                f'minutes={m.group(3)}, seconds={m.group(4)})')),
    (DAYS_AND_HOURS_MINUTES,
     lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, minutes={m.group(3)})'),
    (DAYS_HOURS_SECONDS,
     lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, seconds={m.group(3)})'),
    (HOURS_MINUTES_SECONDS,
     lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)}, seconds={m.group(3)})'),
    (DAYS_AND_HOURS,
     lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)})'),
    (DAYS_AND_MINUTES,
     lambda m: f'timedelta(days={m.group(1)}, minutes={m.group(2)})'),
    (DAYS_AND_SECONDS,
     lambda m: f'timedelta(days={m.group(1)}, seconds={m.group(2)})'),
    (HOURS_AND_MINUTES,
     lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)})'),
    (HOURS_AND_SECONDS,
     lambda m: f'timedelta(hours={m.group(1)}, seconds={m.group(2)})'),
    (MINUTES_AND_SECONDS,
     lambda m: f'timedelta(minutes={m.group(1)}, seconds={m.group(2)})'),
    (DAYS_AND_TIME,
     lambda m: _parse_time(m.group(2), m.group(1))),
    (DAYS,
     lambda m: f'timedelta(days={m.group(1)})'),
    (HOURS,
     lambda m: f'timedelta(hours={m.group(1)})'),
    (MINUTES,
     lambda m: f'timedelta(minutes={m.group(1)})'),
    (SECONDS,
     lambda m: f'timedelta(seconds={m.group(1)})'),
    (TIME,
     lambda m: _parse_time(m.group(1))),
]


def convert_time_expressions(expression: str) -> str:
    """Convert natural language time expressions to timedelta constructors"""
    for pattern, replacement in _TIME_CONVERSION_PATTERNS:
        expression = re.sub(pattern, replacement, expression)
    return expression


def format_time(td: timedelta) -> str:
    """Format timedelta to display string representation"""
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    time_part = f'{hh:02d}:{mm:02d}:{ss:02d}'
    if td.microseconds:
        time_part += f'.{td.microseconds:06d}'

    if td.days == 0:
        return time_part

    day_text = 'day' if abs(td.days) == 1 else 'days'
    if td.seconds == 0 and td.microseconds == 0:
        return f'{td.days:d} {day_text}'
    else:
        return f'{td.days:d} {day_text} and {time_part}'

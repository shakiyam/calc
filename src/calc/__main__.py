import re
import sys
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from prompt_toolkit import PromptSession

from .evaluator import safe_eval as ast_safe_eval

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

PRESERVED_WORDS = {
    'abs', 'avg', 'ceil', 'cos', 'e', 'exp',
    'floor', 'log', 'max', 'min', 'pi', 'round',
    'sin', 'sqrt', 'sum', 'tan', 'timedelta'
}
UNIT_PATTERN = r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*([^\d\s\-+*/(),.^%]+)\b'
PRECISION_DIGITS = 12


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


def _remove_non_time_units(expression: str) -> str:
    """Remove non-time unit words after numbers."""
    def replace_unit(match):
        number = match.group(1)
        word = match.group(2)
        if word in PRESERVED_WORDS:
            return match.group(0)
        return number

    return re.sub(UNIT_PATTERN, replace_unit, expression)


def _has_precision_artifact(value: Decimal) -> bool:
    """Check if value has precision artifacts like repeated 9s or 0s"""
    str_val = str(value)
    pattern_9s = '9' * PRECISION_DIGITS
    pattern_0s = '0' * PRECISION_DIGITS
    return (pattern_9s in str_val or pattern_0s in str_val)


def _normalize_result(value: Decimal) -> Decimal:
    """Normalize high-precision Decimal to user-friendly display format"""
    if _has_precision_artifact(value):
        quantize_pattern = Decimal('0.' + '0' * PRECISION_DIGITS)
        tolerance = Decimal('1e-' + str(PRECISION_DIGITS - 2))
        rounded = value.quantize(quantize_pattern)
        if abs(rounded - round(rounded)) < tolerance:
            return Decimal(int(round(rounded)))
        return rounded.normalize()
    return value


def _format_time(td: timedelta) -> str:
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


def calculate(expression: str, last_result: str) -> str:
    """Calculate mathematical expression and return formatted result"""
    try:
        expression = expression.split('#', 1)[0].strip()
        if not expression:
            return last_result
        expression = expression.replace('?', last_result)
        expression = expression.replace('＋', '+')
        expression = expression.replace('－', '-')
        expression = re.sub(r'([\d\s\-+*/(),.^%])([xX])([\d\s\-+*/(),.^%])', r'\1*\3', expression)
        expression = expression.replace('×', '*')
        expression = expression.replace('÷', '/')
        expression = expression.replace('^', '**')
        expression = re.sub(
            DAYS_HOURS_MINUTES_SECONDS,
            lambda m: (f'timedelta(days={m.group(1)}, hours={m.group(2)}, '
                       f'minutes={m.group(3)}, seconds={m.group(4)})'),
            expression)
        expression = re.sub(
            DAYS_AND_HOURS_MINUTES,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, minutes={m.group(3)})',
            expression)
        expression = re.sub(
            DAYS_HOURS_SECONDS,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, seconds={m.group(3)})',
            expression)
        expression = re.sub(
            HOURS_MINUTES_SECONDS,
            lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)}, seconds={m.group(3)})',
            expression)
        expression = re.sub(
            DAYS_AND_HOURS,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)})',
            expression)
        expression = re.sub(
            DAYS_AND_MINUTES,
            lambda m: f'timedelta(days={m.group(1)}, minutes={m.group(2)})',
            expression)
        expression = re.sub(
            DAYS_AND_SECONDS,
            lambda m: f'timedelta(days={m.group(1)}, seconds={m.group(2)})',
            expression)
        expression = re.sub(
            HOURS_AND_MINUTES,
            lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)})',
            expression)
        expression = re.sub(
            HOURS_AND_SECONDS,
            lambda m: f'timedelta(hours={m.group(1)}, seconds={m.group(2)})',
            expression)
        expression = re.sub(
            MINUTES_AND_SECONDS,
            lambda m: f'timedelta(minutes={m.group(1)}, seconds={m.group(2)})',
            expression)
        expression = re.sub(
            DAYS_AND_TIME,
            lambda m: _parse_time(m.group(2), m.group(1)),
            expression)
        expression = re.sub(DAYS, lambda m: f'timedelta(days={m.group(1)})', expression)
        expression = re.sub(HOURS, lambda m: f'timedelta(hours={m.group(1)})', expression)
        expression = re.sub(MINUTES, lambda m: f'timedelta(minutes={m.group(1)})', expression)
        expression = re.sub(SECONDS, lambda m: f'timedelta(seconds={m.group(1)})', expression)
        expression = re.sub(TIME, lambda m: _parse_time(m.group(1)), expression)
        expression = _remove_non_time_units(expression)
        expression = re.sub(r'(\d),(\d)', r'\1\2', expression)
        result = ast_safe_eval(expression)
        if isinstance(result, Decimal):
            normalized_result = _normalize_result(result)
            formatted_result = f'{normalized_result:,}'
        elif isinstance(result, timedelta):
            formatted_result = _format_time(result)
        print(f'= {formatted_result}')
        return formatted_result
    except ValueError as e:
        if 'Invalid time format' in str(e):
            print('Error: Invalid time format (use HH:MM:SS with MM,SS as 00-59)')
        else:
            print(f'Error: {e}')
        return last_result
    except TypeError as e:
        print(f'Error: {e}')
        return last_result
    except ZeroDivisionError:
        print('Error: Division by zero')
        return last_result
    except OverflowError:
        print('Error: Number too large')
        return last_result
    except SyntaxError:
        print('Error: Invalid syntax')
        return last_result
    except Exception as e:
        print(f'Error: {type(e).__name__} - {e}')
        return last_result


def main() -> None:
    last_result = '0'

    if len(sys.argv) > 1:
        expression = ' '.join(sys.argv[1:])
        calculate(expression, last_result)
        sys.exit()

    if sys.stdin.isatty():
        session: PromptSession = PromptSession()
        while True:
            expression = session.prompt()
            if not expression:
                continue
            elif expression == 'exit':
                break
            last_result = calculate(expression, last_result)
    else:
        for line in sys.stdin:
            expression = line.strip()
            if not expression:
                continue
            elif expression == 'exit':
                break
            last_result = calculate(expression, last_result)


if __name__ == '__main__':
    main()

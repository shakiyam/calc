import re
import sys
from datetime import timedelta
from decimal import Decimal

from prompt_toolkit import PromptSession

from .evaluator import safe_eval as ast_safe_eval


NUMBER = r'(\d+(?:\.\d+)?)'
DAYS = NUMBER + r' *d(?:ays?)?'
HOURS = NUMBER + r' *h(?:ours?|rs?)?'
MINUTES = NUMBER + r' *m(?:in(?:utes?)?)?'
SECONDS = NUMBER + r' *s(?:ec(?:onds?)?)?'
TIME_HH_MM_SS = r'\d+:\d+:\d+(?:\.\d{1,6})?'
AND_OR_SPACE = r'(?:\s+and\s+|\s+)'
SPACE = r'\s+'
DAYS_AND_MINUTES = DAYS + AND_OR_SPACE + MINUTES
DAYS_AND_SECONDS = DAYS + AND_OR_SPACE + SECONDS
DAYS_HOURS_MINUTES_SECONDS = DAYS + SPACE + HOURS + SPACE + MINUTES + SPACE + SECONDS
DAYS_AND_HOURS_MINUTES = DAYS + AND_OR_SPACE + HOURS + SPACE + MINUTES
DAYS_HOURS_SECONDS = DAYS + SPACE + HOURS + SPACE + SECONDS
DAYS_AND_HOURS = DAYS + AND_OR_SPACE + HOURS
HOURS_MINUTES_SECONDS = HOURS + SPACE + MINUTES + SPACE + SECONDS
DAY_AND_TIME = r'(' + DAYS + r' +and +)?' + TIME_HH_MM_SS
MINUTES_AND_SECONDS = MINUTES + AND_OR_SPACE + SECONDS
HOURS_AND_MINUTES = HOURS + AND_OR_SPACE + MINUTES
HOURS_AND_SECONDS = HOURS + AND_OR_SPACE + SECONDS
SINGLE_SECOND = SECONDS
SINGLE_MINUTE = MINUTES
SINGLE_HOUR = HOURS
SINGLE_DAY = DAYS


def parse_time(time_str: str) -> str:
    """Parse time string and return timedelta constructor call"""
    time_match = re.search(
        r'(' + DAYS + r' +and +)?(\d+):([0-5][0-9]):([0-5][0-9])'
        r'(?:\.(\d{1,6}))?', time_str)
    if time_match is None:
        raise ValueError(f'Invalid time format: {time_str}')
    if time_match.group(1) is None:
        days = 0.0
    else:
        days = float(time_match.group(2))
    seconds = int(time_match.group(3)) * 60 * 60 + \
        int(time_match.group(4)) * 60 + \
        int(time_match.group(5))
    if time_match.group(6) is None:
        microseconds = 0
    else:
        microseconds = int(time_match.group(6)) * 10 ** (6 - len(time_match.group(6)))
    td = timedelta(days=days, seconds=seconds, microseconds=microseconds)

    return (f'timedelta(days={td.days}, seconds={td.seconds}, '
            f'microseconds={td.microseconds})')


def format_time(td: timedelta) -> str:
    """Format timedelta to display string representation"""
    if td.days == 0:
        s = ''
    elif abs(td.days) == 1:
        s = f'{td.days:d} day and '
    else:
        s = f'{td.days:d} days and '
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    s = s + f'{hh:02d}:{mm:02d}:{ss:02d}'
    if td.microseconds:
        s = s + f'.{td.microseconds:06d}'
    return s


def calculate(expression: str, last_result: str) -> str:
    """Calculate mathematical expression and return formatted result"""
    try:
        expression = expression.split('#', 1)[0].strip()
        if not expression:
            return last_result
        expression = expression.replace('?', last_result)
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
            DAYS_AND_MINUTES,
            lambda match: f'timedelta(days={match.group(1)}, minutes={match.group(2)})',
            expression)
        expression = re.sub(
            DAYS_AND_SECONDS,
            lambda match: f'timedelta(days={match.group(1)}, seconds={match.group(2)})',
            expression)
        expression = re.sub(
            DAYS_HOURS_SECONDS,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, seconds={m.group(3)})',
            expression)
        expression = re.sub(
            DAYS_AND_HOURS,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)})',
            expression)
        expression = re.sub(
            HOURS_MINUTES_SECONDS,
            lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)}, seconds={m.group(3)})',
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
            DAY_AND_TIME,
            lambda match: parse_time(match.group(0)),
            expression)
        expression = re.sub(MINUTES_AND_SECONDS, r'timedelta(minutes=\1, seconds=\2)', expression)
        expression = re.sub(SINGLE_SECOND, r'timedelta(seconds=\1)', expression)
        expression = re.sub(SINGLE_MINUTE, r'timedelta(minutes=\1)', expression)
        expression = re.sub(SINGLE_HOUR, r'timedelta(hours=\1)', expression)
        expression = re.sub(SINGLE_DAY, r'timedelta(days=\1)', expression)
        expression = re.sub(r'(\d),(\d)', r'\1\2', expression)
        expression = re.sub(r'\b[xX]\b', '*', expression)
        expression = expression.replace('^', '**')
        result = ast_safe_eval(expression)
        if isinstance(result, Decimal):
            formatted_result = f'{result:,}'
        elif isinstance(result, timedelta):
            formatted_result = format_time(result)
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

    session: PromptSession = PromptSession()
    while True:
        expression = session.prompt()
        if not expression:
            continue
        elif expression == 'exit':
            break
        last_result = calculate(expression, last_result)


if __name__ == '__main__':
    main()

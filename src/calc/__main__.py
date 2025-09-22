import re
import sys
from datetime import timedelta
from decimal import Decimal

from prompt_toolkit import PromptSession

from .evaluator import safe_eval as ast_safe_eval


def parse_time(time_str: str) -> str:
    """Parse time string and return timedelta constructor call"""
    day_only_match = re.match(r'^(\d+(?:\.\d+)?) *(?:days?|d)$', time_str)
    if day_only_match:
        days = float(day_only_match.group(1))
        td = timedelta(days=days)
    else:
        time_match = re.search(
            r'((\d+(?:\.\d+)?) *(?:days?|d) +and +)?(\d+):([0-5][0-9]):([0-5][0-9])'
            r'(?:\.(\d{1,6}))?', time_str)
        if time_match is None:
            raise ValueError(f'Invalid time format: {time_str}')
        if time_match.group(2) is None:
            days = 0
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
            r'(\d+(?:\.\d+)?) *(?:days?|d) +and +(\d+(?:\.\d+)?)h\s+(\d+(?:\.\d+)?)m(?!\w)',
            lambda m: (f'timedelta(days={m.group(1)}, '
                       f'hours={m.group(2)}, minutes={m.group(3)})'),
            expression)
        pattern = (r'(\d+(?:\.\d+)?) *(?:days?|d) +and +'
                   r'(\d+(?:\.\d+)?) *hours?\s+(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?')
        expression = re.sub(
            pattern,
            lambda m: (f'timedelta(days={m.group(1)}, '
                       f'hours={m.group(2)}, minutes={m.group(3)})'),
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *(?:days?|d) +and +(\d+(?:\.\d+)?) *h(?:ours?)?',
            lambda match: f'timedelta(days={match.group(1)}, hours={match.group(2)})',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *(?:days?|d) +and +(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?',
            lambda match: f'timedelta(days={match.group(1)}, minutes={match.group(2)})',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *(?:days?|d) +and +(\d+(?:\.\d+)?) *s(?:ec(?:onds?)?)?',
            lambda match: f'timedelta(days={match.group(1)}, seconds={match.group(2)})',
            expression)
        pattern_dhms = (r'(\d+(?:\.\d+)?) *(?:days?|d)\s+(\d+(?:\.\d+)?) *hours?\s+'
                        r'(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?\s+'
                        r'(\d+(?:\.\d+)?) *s(?:ec(?:onds?)?)?')
        expression = re.sub(
            pattern_dhms,
            lambda m: (f'timedelta(days={m.group(1)}, hours={m.group(2)}, '
                       f'minutes={m.group(3)}, seconds={m.group(4)})'),
            expression)
        pattern_dhm = (r'(\d+(?:\.\d+)?) *(?:days?|d)\s+(\d+(?:\.\d+)?) *hours?\s+'
                       r'(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?')
        expression = re.sub(
            pattern_dhm,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, minutes={m.group(3)})',
            expression)
        pattern_dhs = (r'(\d+(?:\.\d+)?) *(?:days?|d)\s+(\d+(?:\.\d+)?) *hours?\s+'
                       r'(\d+(?:\.\d+)?) *s(?:ec(?:onds?)?)?')
        expression = re.sub(
            pattern_dhs,
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)}, seconds={m.group(3)})',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *(?:days?|d)\s+(\d+(?:\.\d+)?) *hours?(?!\s*\d)',
            lambda m: f'timedelta(days={m.group(1)}, hours={m.group(2)})',
            expression)
        pattern_hms = (r'(\d+(?:\.\d+)?) *hours?\s+(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?\s+'
                       r'(\d+(?:\.\d+)?) *s(?:ec(?:onds?)?)?')
        expression = re.sub(
            pattern_hms,
            lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)}, seconds={m.group(3)})',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *hours?\s+(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?(?!\s*\d)',
            lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)})',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *hours?\s+and\s+(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?',
            lambda m: f'timedelta(hours={m.group(1)}, minutes={m.group(2)})',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?\s+and\s+(\d+(?:\.\d+)?) *s(?:ec(?:onds?)?)?',
            lambda m: f'timedelta(minutes={m.group(1)}, seconds={m.group(2)})',
            expression)
        pattern_time_complex = (r'((\d+(?:\.\d+)? *(?:days?|d) +and +)?'
                                r'\d+:\d+:\d+(?:\.\d{1,6})?|\d+(?:\.\d+)? *(?:days?|d))')
        expression = re.sub(
            pattern_time_complex,
            lambda match: parse_time(match.group(1)),
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)(?:d)\s+(\d+(?:\.\d+)?)h\s+(\d+(?:\.\d+)?)m\s+(\d+(?:\.\d+)?)s',
            r'timedelta(days=\1, hours=\2, minutes=\3, seconds=\4)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)(?:d)\s+(\d+(?:\.\d+)?)h\s+(\d+(?:\.\d+)?)m',
            r'timedelta(days=\1, hours=\2, minutes=\3)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)(?:d)\s+(\d+(?:\.\d+)?)h\s+(\d+(?:\.\d+)?)s',
            r'timedelta(days=\1, hours=\2, seconds=\3)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)(?:d)\s+(\d+(?:\.\d+)?)h',
            r'timedelta(days=\1, hours=\2)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)h\s+(\d+(?:\.\d+)?)m\s+(\d+(?:\.\d+)?)s',
            r'timedelta(hours=\1, minutes=\2, seconds=\3)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)h\s+(\d+(?:\.\d+)?)m',
            r'timedelta(hours=\1, minutes=\2)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?)m\s+(\d+(?:\.\d+)?)s',
            r'timedelta(minutes=\1, seconds=\2)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *min(?:ute)?s?\s+(\d+(?:\.\d+)?) *sec(?:ond)?s?',
            r'timedelta(minutes=\1, seconds=\2)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *hr?s?\s+(\d+(?:\.\d+)?) *min(?:ute)?s?',
            r'timedelta(hours=\1, minutes=\2)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *hours?\s+(\d+(?:\.\d+)?) *min(?:ute)?s?',
            r'timedelta(hours=\1, minutes=\2)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *s(?:ec(?:onds?)?)?(?!\w)',
            r'timedelta(seconds=\1)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *m(?:in(?:utes?)?)?(?!\w)',
            r'timedelta(minutes=\1)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *(?:h(?:ours?)?|hrs?)(?!\w)',
            r'timedelta(hours=\1)',
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *d(?!\w)',
            r'timedelta(days=\1)',
            expression)
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

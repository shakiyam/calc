import re
import sys
from datetime import timedelta

from evaluator import safe_eval as ast_safe_eval

from prompt_toolkit import PromptSession


def parse_time(time_str: str) -> str:
    """Parse time string and return timedelta constructor call"""
    # Handle standalone days
    day_only_match = re.match(r'^(\d+(?:\.\d+)?) +days?$', time_str)
    if day_only_match:
        days = float(day_only_match.group(1))
        td = timedelta(days=days)
    else:
        # Handle time format with optional days
        time_match = re.search(
            r'((\d+(?:\.\d+)?) +days?, +)?(\d+):([0-5][0-9]):([0-5][0-9])'
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
        s = f'{td.days:d} day, '
    else:
        s = f'{td.days:d} days, '
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    s = s + f'{hh:02d}:{mm:02d}:{ss:02d}'
    if td.microseconds:
        s = s + f'.{td.microseconds:06d}'
    return s


def calculate(expression: str, last_result: str) -> str:
    """Calculate mathematical expression and return formatted result"""
    try:
        expression = expression.replace('?', last_result)
        expression = re.sub(
            r'((\d+(?:\.\d+)? +days?, +)?\d+:\d+:\d+(?:\.\d{1,6})?|\d+(?:\.\d+)? +days?)',
            lambda match: parse_time(match.group(1)),
            expression)
        expression = re.sub(
            r'(\d+(?:\.\d+)?) *s(?:ec)?',
            r'timedelta(seconds=\1)',
            expression)
        expression = re.sub(r'(\d),(\d)', r'\1\2', expression)
        expression = expression.replace('@', ',')
        expression = re.sub(r'\b[xX]\b', '*', expression)
        expression = expression.replace('^', '**')
        result = ast_safe_eval(expression)
        if isinstance(result, (int, float)):
            result = f'{result:,}'
        elif isinstance(result, timedelta):
            result = format_time(result)
        print(f'= {result}')
        return result
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
        elif expression[0] == '#':
            continue
        elif expression == 'exit':
            break
        last_result = calculate(expression, last_result)


if __name__ == '__main__':
    main()

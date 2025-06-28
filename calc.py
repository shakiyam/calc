import math
import re
import sys
from datetime import timedelta
from math import ceil  # noqa: F401
from math import floor  # noqa: F401
from typing import Any, Match, Optional

from prompt_toolkit import PromptSession


def str2timedelta(s: str) -> timedelta:
    # Handle standalone days
    day_only_match = re.match(r'^(\d+(?:\.\d+)?) +days?$', s)
    if day_only_match:
        days = float(day_only_match.group(1))
        return timedelta(days=days)

    # Handle time format with optional days
    time_match: Optional[Match[str]] = re.search(
        r'((\d+(?:\.\d+)?) +days?, +)?(\d+):([0-5][0-9]):([0-5][0-9])(?:\.(\d{1,6}))?', s)
    if time_match is None:
        raise ValueError(f'Invalid time format: {s}')
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
    return timedelta(days=days, seconds=seconds, microseconds=microseconds)


def timedelta2str(td: timedelta) -> str:
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


SAFE_NAMES = {
    '__builtins__': {},
    'abs': abs, 'round': round, 'ceil': ceil, 'floor': floor,
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'exp': math.exp, 'pi': math.pi, 'e': math.e,
    'timedelta': timedelta, 'str2timedelta': str2timedelta,
}


def safe_eval(expression: str) -> Any:
    """Safely evaluate expression with restricted namespace"""
    if re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', expression):
        allowed_funcs = {name for name, value in SAFE_NAMES.items()
                         if name != '__builtins__' and callable(value)}
        funcs_in_expr = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', expression)
        if any(func not in allowed_funcs for func in funcs_in_expr):
            raise ValueError('Unsafe function call')
    dangerous = ['import', '__', 'exec', 'eval', 'open', 'file']
    if any(word in expression for word in dangerous):
        raise ValueError('Unsafe expression')
    return eval(expression, SAFE_NAMES, {})


def calculate(expression: str, last_result: str) -> str:
    expression = expression.replace('?', last_result)
    expression = re.sub(
        r'((\d+(?:\.\d+)? +days?, +)?\d+:[0-5][0-9]:[0-5][0-9](?:\.\d{1,6})?|\d+(?:\.\d+)? +days?)',
        r'str2timedelta("\1")',
        expression)
    expression = re.sub(
        r'(\d+(?:\.\d+)?) *s(?:ec)?',
        r'timedelta(seconds=\1)',
        expression)
    expression = re.sub(r'(\d),(\d)', r'\1\2', expression)
    expression = expression.replace('@', ',')
    expression = expression.replace('x', '*').replace('X', '*')
    expression = expression.replace('^', '**')
    try:
        result = safe_eval(expression)
        if isinstance(result, (int, float)):
            result = f'{result:,}'
        elif isinstance(result, timedelta):
            result = timedelta2str(result)
        print(f'= {result}')
        return result
    except ValueError as e:
        if 'Invalid time format' in str(e):
            print('Error: Invalid time format (use HH:MM:SS with MM,SS as 00-59)')
        elif 'Unsafe' in str(e):
            print(f'Error: {e}')
        else:
            print(f'Error: Invalid expression - {e}')
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

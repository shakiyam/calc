import re
import sys
from datetime import timedelta
from math import ceil  # noqa: F401
from math import floor  # noqa: F401
from typing import Match
from typing import cast

from prompt_toolkit import PromptSession


def str2timedelta(s: str) -> timedelta:
    # Handle standalone days
    day_only_match = re.match(r'^(\d+(?:\.\d+)?) +days?$', s)
    if day_only_match:
        days = float(day_only_match.group(1))
        return timedelta(days=days)

    # Handle time format with optional days
    time_match = re.search(
        r'((\d+(?:\.\d+)?) +days?, +)?(\d+):([0-5][0-9]):([0-5][0-9])(?:\.(\d{1,6}))?', s)
    if not time_match:
        raise ValueError(f'Invalid time format: {s}')
    time_match = cast(Match, time_match)
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


def calculate(expression, last_result):
    expression = expression.replace('?', str(last_result))
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
        result = eval(expression)
        if type(result) in [int, float]:
            result = f'{result:,}'
        elif type(result) in [timedelta]:
            result = timedelta2str(result)
        print(f'= {result}')
        return result
    except BaseException:
        print('Error')
        return last_result


def main():
    last_result = 0

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

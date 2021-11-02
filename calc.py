import re
import sys
from datetime import timedelta
from math import ceil  # noqa: F401
from math import floor  # noqa: F401
from typing import Match
from typing import cast

from prompt_toolkit import PromptSession


def str2timedelta(s: str) -> timedelta:
    m = re.search(
        r'(?:(\d+) +days?, +)?([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(.\d{6})?',
        s)
    m = cast(Match, m)
    if m.group(1) is None:
        days = 0
    else:
        days = int(m.group(1))
    seconds = int(m.group(2)) * 60 * 60 + int(m.group(3)) * 60 + int(m.group(4))
    if m.group(5) is None:
        microseconds = 0
    else:
        microseconds = int(m.group(5))
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
        r'(\d+(?:\.\d+)?) *s(?:ec)?',
        r'timedelta(seconds=\1)',
        expression)
    expression = re.sub(
        r'((?:\d+ +days?, +)?(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:.\d{6})?)',
        r'str2timedelta("\1")', expression)
    expression = expression.replace(',', '')
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


last_result = 0

if len(sys.argv) > 1:
    expression = ' '.join(sys.argv[1:])
    calculate(expression, last_result)
    sys.exit()

session: PromptSession = PromptSession()
while True:
    expression = session.prompt()
    if len(expression) == 0:
        break
    last_result = calculate(expression, last_result)

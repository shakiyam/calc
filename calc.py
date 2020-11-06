import sys
from math import ceil  # noqa: F401
from math import floor  # noqa: F401

from prompt_toolkit import PromptSession


def calculate(expression, last_result):
    expression = expression.replace('?', str(last_result))
    expression = expression.replace(',', '')
    expression = expression.replace('@', ',')
    expression = expression.replace('x', '*').replace('X', '*')
    expression = expression.replace('^', '**')
    try:
        result = eval(expression)
        if type(result) in [int, float]:
            print(f'= {result:,}')
        else:
            print(f'= {result}')
        return result
    except BaseException:
        print('Error')
        return last_result


last_result = 0

if len(sys.argv) > 1:
    expression = " ".join(sys.argv[1:])
    calculate(expression, last_result)
    sys.exit()

session = PromptSession()
while True:
    expression = session.prompt()
    if len(expression) == 0:
        break
    last_result = calculate(expression, last_result)

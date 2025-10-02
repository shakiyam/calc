import re
import sys
from datetime import timedelta
from decimal import Decimal
from typing import Union

from prompt_toolkit import PromptSession

from .evaluator import safe_eval as ast_safe_eval
from .time_utils import convert_time_expressions, format_time

PRESERVED_WORDS = {
    'abs', 'avg', 'ceil', 'cos', 'e', 'exp',
    'floor', 'log', 'max', 'min', 'pi', 'round',
    'sin', 'sqrt', 'sum', 'tan', 'timedelta'
}
UNIT_PATTERN = r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*([^\d\s\-+*/(),.^%]+)\b'
PRECISION_DIGITS = 12


def _preprocess_expression(expression: str, last_result: str) -> str:
    """Remove comments and substitute history reference"""
    expression = expression.split('#', 1)[0].strip()
    return expression.replace('?', last_result)


def _normalize_operators(expression: str) -> str:
    """Normalize operator aliases to standard Python operators"""
    expression = expression.replace('＋', '+')
    expression = expression.replace('－', '-')
    expression = re.sub(r'([\d\s\-+*/(),.^%])([xX])([\d\s\-+*/(),.^%])', r'\1*\3', expression)
    expression = expression.replace('×', '*')
    expression = expression.replace('÷', '/')
    expression = expression.replace('^', '**')
    return expression


def _remove_non_time_units(expression: str) -> str:
    """Remove non-time unit words after numbers"""
    def replace_unit(match):
        number = match.group(1)
        word = match.group(2)
        if word in PRESERVED_WORDS:
            return match.group(0)
        return number

    return re.sub(UNIT_PATTERN, replace_unit, expression)


def _remove_thousands_separators(expression: str) -> str:
    """Remove comma separators from numbers"""
    return re.sub(r'(\d),(\d)', r'\1\2', expression)


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


def _format_result(result: Union[Decimal, timedelta]) -> str:
    """Format calculation result for display"""
    if isinstance(result, Decimal):
        normalized = _normalize_result(result)
        return f'{normalized:,}'
    elif isinstance(result, timedelta):
        return format_time(result)
    return str(result)


def calculate(expression: str, last_result: str) -> str:
    """Calculate mathematical expression and return formatted result"""
    expression = _preprocess_expression(expression, last_result)
    if not expression:
        return last_result

    try:
        expression = _normalize_operators(expression)
        expression = convert_time_expressions(expression)
        expression = _remove_non_time_units(expression)
        expression = _remove_thousands_separators(expression)

        result = ast_safe_eval(expression)
        formatted_result = _format_result(result)

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
            expression = session.prompt().strip()
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

import re
import sys
from datetime import timedelta
from decimal import Decimal
from typing import Union

from prompt_toolkit import PromptSession

from .evaluator import safe_eval as ast_safe_eval
from .help_text import get_help
from .time_utils import convert_time_expressions, format_time

PRESERVED_WORDS = {
    'abs', 'avg', 'ceil', 'cos', 'e', 'exp',
    'floor', 'log', 'max', 'min', 'pi', 'round',
    'sin', 'sqrt', 'sum', 'tan', 'timedelta'
}
NUMBER_WITH_SUFFIX_PATTERN = r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*([^\d\s\-+*/(),.^%]+)\b'
PRECISION_DIGITS = 12


def _remove_comments(expression: str) -> str:
    """Remove comments from expression"""
    return expression.split('#', 1)[0].strip()


def _substitute_history(expression: str, last_result: str) -> str:
    """Substitute ? with last result"""
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
    def replace_unit(match: re.Match[str]) -> str:
        number = match.group(1)
        word = match.group(2)
        if word in PRESERVED_WORDS:
            return match.group(0)
        return number

    return re.sub(NUMBER_WITH_SUFFIX_PATTERN, replace_unit, expression)


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


def calculate(expression: str, last_result: str) -> tuple[bool, str, str]:
    """
    Calculate mathematical expression with preprocessing

    Returns: (success: bool, value: str, error: str)
    """
    expression = _remove_comments(expression)
    expression = _substitute_history(expression, last_result)
    if not expression:
        return (True, last_result, '')

    try:
        expression = _normalize_operators(expression)
        expression = convert_time_expressions(expression)
        expression = _remove_non_time_units(expression)
        expression = _remove_thousands_separators(expression)

        result = ast_safe_eval(expression)
        formatted_result = _format_result(result)

        return (True, formatted_result, '')

    except ValueError as e:
        return (False, last_result, str(e))
    except TypeError as e:
        return (False, last_result, str(e))
    except ZeroDivisionError:
        return (False, last_result, 'Division by zero')
    except OverflowError:
        return (False, last_result, 'Number too large')
    except SyntaxError:
        return (False, last_result, 'Invalid syntax')
    except Exception as e:
        return (False, last_result, f'{type(e).__name__} - {e}')


def display_result(expression: str, last_result: str) -> str:
    """Calculate and display result"""
    if not _remove_comments(expression):
        return last_result

    success, value, error = calculate(expression, last_result)

    if success:
        print(f'= {value}')
    else:
        print(f'Error: {error}')

    return value


def _process_command(expression: str, last_result: str) -> tuple[bool, str]:
    """
    Process a single command expression

    Returns:
        (should_continue: bool, last_result: str)
    """
    if not expression:
        return (True, last_result)
    elif expression == 'exit':
        return (False, last_result)
    elif expression == 'help':
        print(get_help())
        return (True, last_result)
    else:
        new_result = display_result(expression, last_result)
        return (True, new_result)


def main() -> None:
    last_result = '0'

    if len(sys.argv) > 1:
        expression = ' '.join(sys.argv[1:])
        display_result(expression, last_result)
        sys.exit()

    if sys.stdin.isatty():
        session: PromptSession[str] = PromptSession()
        while True:
            expression = session.prompt().strip()
            should_continue, last_result = _process_command(expression, last_result)
            if not should_continue:
                break
    else:
        for line in sys.stdin:
            expression = line.strip()
            should_continue, last_result = _process_command(expression, last_result)
            if not should_continue:
                break


if __name__ == '__main__':
    main()

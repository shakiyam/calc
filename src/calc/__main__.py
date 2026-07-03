import re
import sys
from collections.abc import Iterator
from datetime import timedelta
from decimal import Decimal

from prompt_toolkit import PromptSession

from .evaluator import ALLOWED_NAMES
from .evaluator import safe_eval as ast_safe_eval
from .help_text import get_help
from .time_utils import (
    convert_time_expressions,
    format_colon,
    format_english,
    format_japanese,
    to_scalar,
)

PRESERVED_WORDS = ALLOWED_NAMES
NUMBER_WITH_SUFFIX_PATTERN = r"\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*([^\d\s\-+*/(),.^%]+)\b"
OUTPUT_DIRECTIVE_PATTERN = r"\s+as\s+(\w+)\s*$"
PRECISION_DIGITS = 12
TIME_FORMATTERS = {
    "default": format_colon,
    "colon": format_colon,
    "japanese": format_japanese,
    "jp": format_japanese,
    "ja": format_japanese,
    "english": format_english,
    "en": format_english,
}
TIME_UNITS = {
    "sec": "sec",
    "seconds": "sec",
    "s": "sec",
    "min": "min",
    "minutes": "min",
    "m": "min",
    "hour": "hour",
    "hours": "hour",
    "h": "hour",
    "day": "day",
    "days": "day",
    "d": "day",
}


def _is_valid_format(name: str) -> bool:
    """Check if name is a known time format or unit"""
    return name in TIME_FORMATTERS or name in TIME_UNITS


def _remove_comments(expression: str) -> str:
    """Remove comments from expression"""
    return expression.split("#", 1)[0].strip()


def _extract_output_directive(expression: str) -> tuple[str, str | None]:
    """Extract trailing output format directive (as <format>)"""
    match = re.search(OUTPUT_DIRECTIVE_PATTERN, expression)
    if not match:
        return (expression, None)
    return (expression[: match.start()], match.group(1))


def _substitute_history(expression: str, last_result: str) -> str:
    """Substitute ? with last result"""
    return expression.replace("?", last_result)


def _normalize_operators(expression: str) -> str:
    """Normalize operator aliases to standard Python operators"""
    expression = expression.replace("＋", "+")
    expression = expression.replace("－", "-")
    expression = re.sub(r"([\d\s\-+*/(),.^%])([xX])([\d\s\-+*/(),.^%])", r"\1*\3", expression)
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("^", "**")
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
    return re.sub(r"(\d),(\d)", r"\1\2", expression)


def _has_precision_artifact(value: Decimal) -> bool:
    """Check if value has precision artifacts like repeated 9s or 0s"""
    str_val = str(value)
    pattern_9s = "9" * PRECISION_DIGITS
    pattern_0s = "0" * PRECISION_DIGITS
    return pattern_9s in str_val or pattern_0s in str_val


def _normalize_result(value: Decimal) -> Decimal:
    """Normalize high-precision Decimal to user-friendly display format"""
    if _has_precision_artifact(value):
        quantize_pattern = Decimal(f"0.{'0' * PRECISION_DIGITS}")
        tolerance = Decimal(f"1e-{PRECISION_DIGITS - 2}")
        rounded = value.quantize(quantize_pattern)
        if abs(rounded - round(rounded)) < tolerance:
            return Decimal(int(round(rounded)))
        return rounded.normalize()
    return value


def _format_decimal(value: Decimal) -> str:
    """Format Decimal with normalization and thousands separators"""
    normalized = _normalize_result(value)
    if normalized == normalized.to_integral_value():
        return f"{int(normalized):,}"
    return f"{normalized:,f}"


def _format_result(
    result: Decimal | timedelta, directive: str | None = None, default_format: str = "default"
) -> str:
    """Format calculation result for display"""
    if directive is not None and not _is_valid_format(directive):
        raise ValueError(f"Unknown format: '{directive}'")
    if isinstance(result, Decimal):
        if directive is not None:
            raise ValueError(
                f"'{directive}' format only applies to time values, got a plain number"
            )
        return _format_decimal(result)
    elif isinstance(result, timedelta):
        directive = directive if directive is not None else default_format
        if directive in TIME_UNITS:
            unit = TIME_UNITS[directive]
            return f"{_format_decimal(to_scalar(result, unit))} {unit}"
        return TIME_FORMATTERS[directive](result)
    return str(result)


def calculate(
    expression: str, last_result: str, default_format: str = "default"
) -> tuple[bool, str, str]:
    """
    Calculate mathematical expression with preprocessing

    Returns: (success: bool, value: str, error: str)
    """
    expression = _remove_comments(expression)
    expression, directive = _extract_output_directive(expression)
    expression = _substitute_history(expression, last_result)
    if not expression:
        return (True, last_result, "")

    try:
        expression = _normalize_operators(expression)
        expression = _remove_thousands_separators(expression)
        expression = convert_time_expressions(expression)
        expression = _remove_non_time_units(expression)

        result = ast_safe_eval(expression)
        formatted_result = _format_result(result, directive, default_format)

        return (True, formatted_result, "")

    except (ValueError, TypeError) as e:
        return (False, last_result, str(e))
    except ZeroDivisionError:
        return (False, last_result, "Division by zero")
    except OverflowError:
        return (False, last_result, "Number too large")
    except SyntaxError:
        return (False, last_result, "Invalid syntax")
    except Exception as e:
        return (False, last_result, f"{type(e).__name__} - {e}")


def _evaluate_and_print(
    expression: str, last_result: str, default_format: str = "default"
) -> str:
    """Evaluate expression, print the result or error, and return the new history value"""
    if not _remove_comments(expression):
        return last_result

    success, value, error = calculate(expression, last_result, default_format)

    if success:
        print(f"= {value}")
    else:
        print(f"Error: {error}")

    return value


def _process_command(
    expression: str, last_result: str, current_format: str
) -> tuple[bool, str, str]:
    """
    Process a single command expression

    Returns:
        (should_continue: bool, last_result: str, current_format: str)
    """
    if not expression:
        return (True, last_result, current_format)
    elif expression == "exit":
        return (False, last_result, current_format)
    elif expression == "help":
        print(get_help())
        return (True, last_result, current_format)
    elif expression == "format":
        print(current_format)
        return (True, last_result, current_format)
    elif expression.startswith("format "):
        name = expression.removeprefix("format ").strip()
        if _is_valid_format(name):
            return (True, last_result, name)
        print(f"Error: Unknown format: '{name}'")
        return (True, last_result, current_format)
    else:
        new_result = _evaluate_and_print(expression, last_result, current_format)
        return (True, new_result, current_format)


def _input_lines() -> Iterator[str]:
    """Yield input lines from the prompt session (tty) or stdin (pipe)"""
    if sys.stdin.isatty():
        session: PromptSession[str] = PromptSession()
        while True:
            yield session.prompt()
    else:
        yield from sys.stdin


def main() -> None:
    last_result = "0"
    current_format = "default"

    if len(sys.argv) > 1:
        expression = " ".join(sys.argv[1:])
        _evaluate_and_print(expression, last_result)
        sys.exit()

    for line in _input_lines():
        expression = line.strip()
        should_continue, last_result, current_format = _process_command(
            expression, last_result, current_format
        )
        if not should_continue:
            break


if __name__ == "__main__":
    main()

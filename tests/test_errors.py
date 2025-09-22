import sys
from io import StringIO

from calc.__main__ import calculate


def capture_calculate_output(expression, last_result='999'):
    """Helper function to capture both result and printed output"""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    try:
        result = calculate(expression, last_result)
        output = captured_output.getvalue().strip()
        return result, output
    finally:
        sys.stdout = old_stdout


def test_syntax_errors():
    """Test syntax error handling"""
    last_result_val = '999'

    result, output = capture_calculate_output('', last_result_val)
    assert result == last_result_val
    assert output == ''

    result, output = capture_calculate_output('1 +', last_result_val)
    assert result == last_result_val
    assert 'Error: Invalid syntax' in output

    result, output = capture_calculate_output('(', last_result_val)
    assert result == last_result_val
    assert 'Error: Invalid syntax' in output

    result, output = capture_calculate_output('import os', last_result_val)
    assert result == last_result_val
    assert 'Error: Invalid syntax' in output


def test_security_errors():
    """Test security-related error handling"""
    last_result_val = '999'

    result, output = capture_calculate_output('open("test.txt")', last_result_val)
    assert result == last_result_val
    assert 'Error: Unsupported function:' in output


def test_runtime_errors():
    """Test runtime error handling"""
    last_result_val = '999'

    result, output = capture_calculate_output('1 / 0', last_result_val)
    assert result == last_result_val
    assert 'Error: Division by zero' in output

    result, output = capture_calculate_output('sqrt(-1)', last_result_val)
    assert result == last_result_val
    assert 'Error: math domain error' in output


def test_function_argument_errors():
    """Test function argument error handling"""
    last_result_val = '999'

    result, output = capture_calculate_output('min()', last_result_val)
    assert result == last_result_val
    assert 'Error: min expected at least 1 argument, got 0' in output

    result, output = capture_calculate_output('max()', last_result_val)
    assert result == last_result_val
    assert 'Error: max expected at least 1 argument, got 0' in output

    result, output = capture_calculate_output('avg()', last_result_val)
    assert result == last_result_val
    assert 'Error: avg expected at least 1 argument, got 0' in output


def test_time_related_errors():
    """Test time-related error handling"""
    last_result_val = '999'

    result, output = capture_calculate_output('25:99:99', last_result_val)
    assert result == last_result_val
    assert 'Error: Invalid time format' in output

    result, output = capture_calculate_output('03:00:00 + 2', last_result_val)
    assert result == last_result_val
    assert 'Error: Unsupported operation' in output
    assert 'between timedelta and Decimal' in output

    result, output = capture_calculate_output('2 / 03:00:00', last_result_val)
    assert result == last_result_val
    assert 'Error: Unsupported operation' in output
    assert 'between Decimal and timedelta' in output

import sys
from io import StringIO

from calc.__main__ import calculate


def test_basic_operators():
    """Test all supported operators and aliases"""
    # Basic arithmetic
    assert calculate('10 - 3', '0') == '7'
    assert calculate('12 / 4', '0') == '3'
    assert calculate('7 % 3', '0') == '1'
    assert calculate('2 ** 3', '0') == '8'

    # Operator aliases
    assert calculate('3 x 4', '0') == '12'

    # Complex expressions with parentheses and negative numbers
    assert calculate('(2 + 3) * 4', '0') == '20'
    assert calculate('-5 * -3', '0') == '15'


def test_decimal_precision():
    """Test that decimal calculations are precise"""
    # Classic floating-point error that should be fixed with Decimal
    assert calculate('0.1 + 0.2', '0') == '0.3'


def test_comments():
    """Test that comments are ignored"""
    assert calculate('1 + 1 # This is a comment', '0') == '2'
    assert calculate('# Just a comment', '0') == '0'


def test_mathematical_functions():
    """Test mathematical functions"""
    assert calculate('ceil(3.2)', '0') == '4'
    assert calculate('exp(1)', '0') == '2.718281828459045'
    assert calculate('floor(3.8)', '0') == '3'
    assert calculate('max(1, 2, 3)', '0') == '3'
    assert calculate('max(10)', '0') == '10'
    assert calculate('min(1, 2, 3)', '0') == '1'
    assert calculate('min(10)', '0') == '10'
    assert calculate('round(3.7)', '0') == '4'


def test_mathematical_constants():
    """Test mathematical constants pi and e"""
    assert calculate('pi', '0') == '3.141592653589793'
    assert calculate('e', '0') == '2.718281828459045'


def test_time_calculations():
    """Test time unit conversions and calculations"""
    # Basic second conversions
    assert calculate('60s', '0') == '00:01:00'

    # Standalone day unit tests
    assert calculate('1 day', '0') == '1 day, 00:00:00'

    # Time arithmetic
    assert calculate('00:01:00 + 30s', '0') == '00:01:30'
    assert calculate('01:00:00 - 30s', '0') == '00:59:30'
    assert calculate('00:30:00 * 2', '0') == '01:00:00'

    # Complex time expressions with decimal days
    assert calculate('0.5 day, 06:00:00 + 30s', '0') == '18:00:30'


def test_history_functionality():
    """Test history reference with ?"""
    assert calculate('5 + 3', '0') == '8'
    assert calculate('? * 2', '8') == '16'
    assert calculate('? + ?', '16') == '32'


def test_input_formatting():
    """Test comma handling and number formatting"""
    # Comma removal in input
    assert calculate('1,000 + 2,000', '0') == '3,000'

    # @ to comma conversion
    assert calculate('round(3.14159@ 2)', '0') == '3.14'

    # Large number formatting in output
    assert calculate('1000000', '0') == '1,000,000'


def test_error_handling():
    """Test error handling with both return values and error messages"""
    last_result_val = '999'

    # Capture stdout to check error messages
    def capture_calculate_output(expression):
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        try:
            result = calculate(expression, last_result_val)
            output = captured_output.getvalue().strip()
            return result, output
        finally:
            sys.stdout = old_stdout

    result, output = capture_calculate_output('')
    assert result == last_result_val
    assert output == ''

    result, output = capture_calculate_output('1 +')
    assert result == last_result_val
    assert 'Error: Invalid syntax' in output

    result, output = capture_calculate_output('(')
    assert result == last_result_val
    assert 'Error: Invalid syntax' in output

    result, output = capture_calculate_output('1 / 0')
    assert result == last_result_val
    assert 'Error: Division by zero' in output

    result, output = capture_calculate_output('sqrt(-1)')
    assert result == last_result_val
    assert 'Error: math domain error' in output

    result, output = capture_calculate_output('25:99:99')
    assert result == last_result_val
    assert 'Error: Invalid time format' in output

    result, output = capture_calculate_output('open("test.txt")')
    assert result == last_result_val
    assert 'Error: Unsupported function:' in output

    result, output = capture_calculate_output('import os')
    assert result == last_result_val
    assert 'Error: Invalid syntax' in output

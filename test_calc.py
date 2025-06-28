import sys
from datetime import timedelta
from io import StringIO

from calc import calculate, str2timedelta, timedelta2str


def test_basic_operators():
    """Test all supported operators and aliases"""
    # Basic arithmetic
    assert calculate('10 - 3', '0') == '7'
    assert calculate('12 / 4', '0') == '3.0'
    assert calculate('7 % 3', '0') == '1'
    assert calculate('2 ** 3', '0') == '8'

    # Operator aliases
    assert calculate('3 x 4', '0') == '12'

    # Complex expressions with parentheses and negative numbers
    assert calculate('(2 + 3) * 4', '0') == '20'
    assert calculate('-5 * -3', '0') == '15'


def test_mathematical_functions():
    """Test built-in mathematical functions"""
    assert calculate('ceil(3.2)', '0') == '4'
    assert calculate('floor(3.8)', '0') == '3'
    assert calculate('round(3.7)', '0') == '4'


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
    """Test that invalid expressions return last_result and don't crash"""
    # Invalid syntax
    assert calculate('1 +', '999') == '999'
    assert calculate('(', '999') == '999'

    # Division by zero
    assert calculate('1 / 0', '999') == '999'

    # Invalid function calls
    assert calculate('undefined_function()', '999') == '999'

    # Empty expressions
    assert calculate('', '999') == '999'

    # Unsafe function calls (should be blocked by safe_eval)
    assert calculate('open("test.txt")', '999') == '999'
    assert calculate('import os', '999') == '999'
    assert calculate('__import__("os")', '999') == '999'


def test_error_messages():
    """Test specific error messages are displayed"""
    # Capture stdout to check error messages
    def capture_error_message(expression, last_result='999'):
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        try:
            result = calculate(expression, last_result)
            output = captured_output.getvalue().strip()
            return result, output
        finally:
            sys.stdout = old_stdout

    # Test division by zero
    result, output = capture_error_message('1 / 0')
    assert result == '999'
    assert 'Error: Division by zero' in output

    # Test unsafe function call
    result, output = capture_error_message('open("test.txt")')
    assert result == '999'
    assert 'Error: Unsafe function call' in output

    # Test number overflow
    result, output = capture_error_message('10.0 ** 400')
    assert result == '999'
    assert 'Error: Number too large' in output

    # Test syntax error
    result, output = capture_error_message('1 +')
    assert result == '999'
    assert 'Error: Invalid syntax' in output


def test_str2timedelta():
    """Test time string parsing function"""
    # Basic time format
    td = str2timedelta('01:30:45')
    assert td.seconds == 5445  # 1*3600 + 30*60 + 45

    # With days
    td = str2timedelta('2 days, 01:30:45')
    assert td.days == 2
    assert td.seconds == 5445

    # With microseconds
    td = str2timedelta('00:00:01.500000')
    assert td.seconds == 1
    assert td.microseconds == 500000


def test_timedelta2str():
    """Test time delta to string conversion"""
    # Basic conversion
    td = timedelta(hours=1, minutes=30, seconds=45)
    assert timedelta2str(td) == '01:30:45'

    # With days
    td = timedelta(days=2, hours=1, minutes=30, seconds=45)
    assert timedelta2str(td) == '2 days, 01:30:45'

    # Single day
    td = timedelta(days=1, hours=1, minutes=30, seconds=45)
    assert timedelta2str(td) == '1 day, 01:30:45'

    # With microseconds
    td = timedelta(seconds=1, microseconds=500000)
    assert timedelta2str(td) == '00:00:01.500000'

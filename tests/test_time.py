from calc.__main__ import calculate


def test_time_formats():
    """Test various time format inputs"""
    last_result_val = '0'
    # Basic formats
    assert calculate('01:30:45', last_result_val) == '01:30:45'
    assert calculate('00:01:30.500000', last_result_val) == '00:01:30.500000'
    assert calculate('60s', last_result_val) == '00:01:00'
    assert calculate('30min', last_result_val) == '00:30:00'
    assert calculate('5hr', last_result_val) == '05:00:00'
    assert calculate('1 day', last_result_val) == '1 day'
    assert calculate('2d', last_result_val) == '2 days'
    # Compact combinations
    assert calculate('1h 30m', last_result_val) == '01:30:00'
    assert calculate('1m 5s', last_result_val) == '00:01:05'
    # Day and combinations
    assert calculate('1 day and 10 hours', last_result_val) == '1 day and 10:00:00'
    assert calculate('1 day and 1 hour 2 min', last_result_val) == '1 day and 01:02:00'
    # Natural language
    assert calculate('1 day 2 hours 30 minutes', last_result_val) == '1 day and 02:30:00'
    assert calculate('2 hours and 30 minutes', last_result_val) == '02:30:00'


def test_time_operations():
    """Test time arithmetic operations"""
    last_result_val = '0'
    assert calculate('00:01:00 + 30s', last_result_val) == '00:01:30'
    assert calculate('01:00:00 - 30s', last_result_val) == '00:59:30'
    assert calculate('00:30:00 * 2', last_result_val) == '01:00:00'
    assert calculate('02:00:00 / 2', last_result_val) == '01:00:00'
    assert calculate('0.5 day and 06:00:00 + 30s', last_result_val) == '18:00:30'
    assert calculate('1h + 30min', last_result_val) == '01:30:00'
    assert calculate('30min - 5s', last_result_val) == '00:29:55'


def test_time_functions():
    """Test functions with time values"""
    last_result_val = '0'
    assert calculate('ceil(0.1s)', last_result_val) == '00:00:01'
    assert calculate('floor(0.9s)', last_result_val) == '00:00:00'
    assert calculate('round(0.7s)', last_result_val) == '00:00:01'
    assert calculate('max(1 day, 02:00:00)', last_result_val) == '1 day'
    assert calculate('min(01:00:00, 90s)', last_result_val) == '00:01:30'
    assert calculate('sum(1:00:00, 2:00:00)', last_result_val) == '03:00:00'
    assert calculate('avg(1:00:00, 3:00:00)', last_result_val) == '02:00:00'

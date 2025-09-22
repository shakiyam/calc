from calc.__main__ import calculate


def test_time_calculations():
    """Test time unit conversions and calculations"""
    last_result_val = '0'
    assert calculate('60s', last_result_val) == '00:01:00'
    assert calculate('1 day', last_result_val) == '1 day and 00:00:00'
    assert calculate('00:01:00 + 30s', last_result_val) == '00:01:30'
    assert calculate('01:00:00 - 30s', last_result_val) == '00:59:30'
    assert calculate('00:30:00 * 2', last_result_val) == '01:00:00'
    assert calculate('0.5 day and 06:00:00 + 30s', last_result_val) == '18:00:30'


def test_time_functions():
    """Test functions with time values"""
    last_result_val = '0'
    assert calculate('ceil(0.1s)', last_result_val) == '00:00:01'
    assert calculate('floor(0.9s)', last_result_val) == '00:00:00'
    assert calculate('round(0.7s)', last_result_val) == '00:00:01'
    assert calculate('max(1 day, 02:00:00)', last_result_val) == '1 day and 00:00:00'
    assert calculate('min(01:00:00, 90s)', last_result_val) == '00:01:30'
    assert calculate('sum(1:00:00, 2:00:00)', last_result_val) == '03:00:00'
    assert calculate('avg(1:00:00, 3:00:00)', last_result_val) == '02:00:00'

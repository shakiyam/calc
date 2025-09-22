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


def test_time_minmax_functions():
    """Test min/max functions with time values"""
    last_result_val = '0'
    assert calculate('min(01:00:00, 90s)', last_result_val) == '00:01:30'
    assert calculate('min(1 day, 02:00:00, 25:00:00)', last_result_val) == '02:00:00'

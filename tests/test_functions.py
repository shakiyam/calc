from calc.__main__ import calculate


def test_numeric_functions():
    """Test functions with numeric values"""
    last_result_val = '0'
    success, value, error = calculate('exp(1)', last_result_val)
    assert success and value == '2.718281828459045'
    success, value, error = calculate('ceil(3.2)', last_result_val)
    assert success and value == '4'
    success, value, error = calculate('floor(3.8)', last_result_val)
    assert success and value == '3'
    success, value, error = calculate('round(3.7)', last_result_val)
    assert success and value == '4'
    success, value, error = calculate('max(1, 2, 3)', last_result_val)
    assert success and value == '3'
    success, value, error = calculate('max(10)', last_result_val)
    assert success and value == '10'
    success, value, error = calculate('min(1, 2, 3)', last_result_val)
    assert success and value == '1'
    success, value, error = calculate('min(10)', last_result_val)
    assert success and value == '10'
    success, value, error = calculate('sum(1, 2, 3)', last_result_val)
    assert success and value == '6'
    success, value, error = calculate('sum(10)', last_result_val)
    assert success and value == '10'
    success, value, error = calculate('avg(1, 2, 3)', last_result_val)
    assert success and value == '2'
    success, value, error = calculate('avg(10)', last_result_val)
    assert success and value == '10'


def test_mathematical_constants():
    """Test mathematical constants pi and e"""
    last_result_val = '0'
    success, value, error = calculate('pi', last_result_val)
    assert success and value == '3.141592653589793'
    success, value, error = calculate('e', last_result_val)
    assert success and value == '2.718281828459045'

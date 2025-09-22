from calc.__main__ import calculate


def test_numeric_functions():
    """Test functions with numeric values"""
    last_result_val = '0'
    assert calculate('exp(1)', last_result_val) == '2.718281828459045'
    assert calculate('ceil(3.2)', last_result_val) == '4'
    assert calculate('floor(3.8)', last_result_val) == '3'
    assert calculate('round(3.7)', last_result_val) == '4'
    assert calculate('max(1, 2, 3)', last_result_val) == '3'
    assert calculate('max(10)', last_result_val) == '10'
    assert calculate('min(1, 2, 3)', last_result_val) == '1'
    assert calculate('min(10)', last_result_val) == '10'
    assert calculate('sum(1, 2, 3)', last_result_val) == '6'
    assert calculate('sum(10)', last_result_val) == '10'
    assert calculate('avg(1, 2, 3)', last_result_val) == '2'
    assert calculate('avg(10)', last_result_val) == '10'


def test_mathematical_constants():
    """Test mathematical constants pi and e"""
    last_result_val = '0'
    assert calculate('pi', last_result_val) == '3.141592653589793'
    assert calculate('e', last_result_val) == '2.718281828459045'

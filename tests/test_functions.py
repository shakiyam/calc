from calc.__main__ import evaluate_expression


def test_numeric_functions():
    """Test functions with numeric values"""
    last_result_val = '0'
    success, value, error = evaluate_expression('exp(1)', last_result_val)
    assert success and value == '2.718281828459045'
    success, value, error = evaluate_expression('ceil(3.2)', last_result_val)
    assert success and value == '4'
    success, value, error = evaluate_expression('floor(3.8)', last_result_val)
    assert success and value == '3'
    success, value, error = evaluate_expression('round(3.7)', last_result_val)
    assert success and value == '4'
    success, value, error = evaluate_expression('max(1, 2, 3)', last_result_val)
    assert success and value == '3'
    success, value, error = evaluate_expression('max(10)', last_result_val)
    assert success and value == '10'
    success, value, error = evaluate_expression('min(1, 2, 3)', last_result_val)
    assert success and value == '1'
    success, value, error = evaluate_expression('min(10)', last_result_val)
    assert success and value == '10'
    success, value, error = evaluate_expression('sum(1, 2, 3)', last_result_val)
    assert success and value == '6'
    success, value, error = evaluate_expression('sum(10)', last_result_val)
    assert success and value == '10'
    success, value, error = evaluate_expression('avg(1, 2, 3)', last_result_val)
    assert success and value == '2'
    success, value, error = evaluate_expression('avg(10)', last_result_val)
    assert success and value == '10'


def test_mathematical_constants():
    """Test mathematical constants pi and e"""
    last_result_val = '0'
    success, value, error = evaluate_expression('pi', last_result_val)
    assert success and value == '3.141592653589793'
    success, value, error = evaluate_expression('e', last_result_val)
    assert success and value == '2.718281828459045'

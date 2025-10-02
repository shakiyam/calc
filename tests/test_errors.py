from calc.__main__ import evaluate_expression


def test_syntax_errors():
    """Test syntax error handling"""
    last_result_val = '999'
    success, value, error = evaluate_expression('', last_result_val)
    assert success and value == last_result_val
    success, value, error = evaluate_expression('1 +', last_result_val)
    assert not success and value == last_result_val and error == 'Invalid syntax'
    success, value, error = evaluate_expression('(', last_result_val)
    assert not success and value == last_result_val and error == 'Invalid syntax'
    success, value, error = evaluate_expression('import os', last_result_val)
    assert not success and value == last_result_val and error == 'Invalid syntax'


def test_security_errors():
    """Test security-related error handling"""
    last_result_val = '999'
    success, value, error = evaluate_expression('open("test.txt")', last_result_val)
    assert not success and value == last_result_val and 'Unsupported constant type: str' in error


def test_runtime_errors():
    """Test runtime error handling"""
    last_result_val = '999'
    success, value, error = evaluate_expression('1 / 0', last_result_val)
    assert not success and value == last_result_val and error == 'Division by zero'
    success, value, error = evaluate_expression('sqrt(-1)', last_result_val)
    assert not success and value == last_result_val and 'math domain error' in error


def test_function_argument_errors():
    """Test function argument error handling"""
    last_result_val = '999'
    success, value, error = evaluate_expression('min()', last_result_val)
    assert (not success and value == last_result_val and
            'min expected at least 1 argument, got 0' in error)
    success, value, error = evaluate_expression('max()', last_result_val)
    assert (not success and value == last_result_val and
            'max expected at least 1 argument, got 0' in error)
    success, value, error = evaluate_expression('avg()', last_result_val)
    assert (not success and value == last_result_val and
            'avg expected at least 1 argument, got 0' in error)


def test_time_related_errors():
    """Test time-related error handling"""
    last_result_val = '999'
    success, value, error = evaluate_expression('25:99:99', last_result_val)
    assert not success and value == last_result_val and 'Invalid time format' in error
    success, value, error = evaluate_expression('03:00:00 + 2', last_result_val)
    assert not success and value == last_result_val and 'Unsupported operation' in error
    success, value, error = evaluate_expression('sum(1:00:00, 60)', last_result_val)
    assert (not success and value == last_result_val and
            'Cannot mix timedelta and Decimal in sum' in error)

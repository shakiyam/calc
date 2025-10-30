from calc.__main__ import calculate

LAST_RESULT = "999"


def test_syntax_errors():
    """Test syntax error handling"""
    success, value, error = calculate("", LAST_RESULT)
    assert success and value == LAST_RESULT
    success, value, error = calculate("1 +", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Invalid syntax"
    success, value, error = calculate("(", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Invalid syntax"
    success, value, error = calculate("import os", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Invalid syntax"


def test_security_errors():
    """Test security-related error handling"""
    success, value, error = calculate('open("test.txt")', LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unsupported constant type: str" in error


def test_runtime_errors():
    """Test runtime error handling"""
    success, value, error = calculate("1 / 0", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Division by zero"
    success, value, error = calculate("sqrt(-1)", LAST_RESULT)
    assert (not success and value == LAST_RESULT and
            ("math domain error" in error or "expected a nonnegative input" in error))


def test_function_argument_errors():
    """Test function argument error handling"""
    success, value, error = calculate("min()", LAST_RESULT)
    assert (not success and value == LAST_RESULT and
            "min expected at least 1 argument, got 0" in error)
    success, value, error = calculate("max()", LAST_RESULT)
    assert (not success and value == LAST_RESULT and
            "max expected at least 1 argument, got 0" in error)
    success, value, error = calculate("avg()", LAST_RESULT)
    assert (not success and value == LAST_RESULT and
            "avg expected at least 1 argument, got 0" in error)


def test_time_related_errors():
    """Test time-related error handling"""
    success, value, error = calculate("25:99:99", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Invalid time format" in error
    success, value, error = calculate("03:00:00 + 2", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unsupported operation" in error
    success, value, error = calculate("sum(1:00:00, 60)", LAST_RESULT)
    assert (not success and value == LAST_RESULT and
            "Cannot mix timedelta and Decimal in sum" in error)

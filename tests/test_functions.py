from calc.__main__ import calculate

LAST_RESULT = "0"


def test_numeric_functions() -> None:
    """Test functions with numeric values"""
    success, value, error = calculate("exp(1)", LAST_RESULT)
    assert success and value == "2.718281828459045"
    success, value, error = calculate("ceil(3.2)", LAST_RESULT)
    assert success and value == "4"
    success, value, error = calculate("floor(3.8)", LAST_RESULT)
    assert success and value == "3"
    success, value, error = calculate("round(3.7)", LAST_RESULT)
    assert success and value == "4"
    success, value, error = calculate("max(1, 2, 3)", LAST_RESULT)
    assert success and value == "3"
    success, value, error = calculate("max(10)", LAST_RESULT)
    assert success and value == "10"
    success, value, error = calculate("min(1, 2, 3)", LAST_RESULT)
    assert success and value == "1"
    success, value, error = calculate("min(10)", LAST_RESULT)
    assert success and value == "10"
    success, value, error = calculate("sum(1, 2, 3)", LAST_RESULT)
    assert success and value == "6"
    success, value, error = calculate("sum(10)", LAST_RESULT)
    assert success and value == "10"
    success, value, error = calculate("avg(1, 2, 3)", LAST_RESULT)
    assert success and value == "2"
    success, value, error = calculate("avg(10)", LAST_RESULT)
    assert success and value == "10"


def test_round_half_up() -> None:
    """Test that round uses half-up (ties away from zero)"""
    success, value, error = calculate("round(2.5)", LAST_RESULT)
    assert success and value == "3"
    success, value, error = calculate("round(-2.5)", LAST_RESULT)
    assert success and value == "-3"
    success, value, error = calculate("round(0.5)", LAST_RESULT)
    assert success and value == "1"
    success, value, error = calculate("round(2.25, 1)", LAST_RESULT)
    assert success and value == "2.3"
    success, value, error = calculate("round(-2.25, 1)", LAST_RESULT)
    assert success and value == "-2.3"


def test_roundeven() -> None:
    """Test that roundeven uses banker's rounding (ties to even)"""
    success, value, error = calculate("roundeven(2.5)", LAST_RESULT)
    assert success and value == "2"
    success, value, error = calculate("roundeven(3.5)", LAST_RESULT)
    assert success and value == "4"
    success, value, error = calculate("roundeven(-2.5)", LAST_RESULT)
    assert success and value == "-2"
    success, value, error = calculate("roundeven(2.25, 1)", LAST_RESULT)
    assert success and value == "2.2"
    success, value, error = calculate("roundeven(2.35, 1)", LAST_RESULT)
    assert success and value == "2.4"


def test_mathematical_constants() -> None:
    """Test mathematical constants pi and e"""
    success, value, error = calculate("pi", LAST_RESULT)
    assert success and value == "3.141592653589793"
    success, value, error = calculate("e", LAST_RESULT)
    assert success and value == "2.718281828459045"

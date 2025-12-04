from calc.__main__ import calculate

LAST_RESULT = "0"


def test_basic_operators() -> None:
    """Test basic mathematical operators"""
    success, value, error = calculate("10 - 3", LAST_RESULT)
    assert success and value == "7"
    success, value, error = calculate("12 / 4", LAST_RESULT)
    assert success and value == "3"
    success, value, error = calculate("7 % 3", LAST_RESULT)
    assert success and value == "1"
    success, value, error = calculate("2 ** 3", LAST_RESULT)
    assert success and value == "8"
    success, value, error = calculate("(2 + 3) * 4", LAST_RESULT)
    assert success and value == "20"
    success, value, error = calculate("-5 * -3", LAST_RESULT)
    assert success and value == "15"


def test_operator_aliases() -> None:
    """Test operator aliases"""
    success, value, error = calculate("10 ＋ 5", LAST_RESULT)
    assert success and value == "15"
    success, value, error = calculate("20 － 8", LAST_RESULT)
    assert success and value == "12"
    success, value, error = calculate("3 x 4", LAST_RESULT)
    assert success and value == "12"
    success, value, error = calculate("5 X 2", LAST_RESULT)
    assert success and value == "10"
    success, value, error = calculate("2x3", LAST_RESULT)
    assert success and value == "6"
    success, value, error = calculate("6 × 7", LAST_RESULT)
    assert success and value == "42"
    success, value, error = calculate("18 ÷ 3", LAST_RESULT)
    assert success and value == "6"
    success, value, error = calculate("2 ^ 3", LAST_RESULT)
    assert success and value == "8"


def test_decimal_precision() -> None:
    """Test that decimal calculations are precise"""
    success, value, error = calculate("0.1 + 0.2", LAST_RESULT)
    assert success and value == "0.3"
    success, value, error = calculate("1 / 3 * 3", LAST_RESULT)
    assert success and value == "1"


def test_comments() -> None:
    """Test that comments are ignored"""
    success, value, error = calculate("1 + 1 # This is a comment", LAST_RESULT)
    assert success and value == "2"
    success, value, error = calculate("# Just a comment", LAST_RESULT)
    assert success and value == LAST_RESULT


def test_input_formatting() -> None:
    """Test comma handling and number formatting"""
    success, value, error = calculate("1,000 + 2,000", LAST_RESULT)
    assert success and value == "3,000"
    success, value, error = calculate("1000000", LAST_RESULT)
    assert success and value == "1,000,000"


def test_no_exponential_notation() -> None:
    """Test that large numbers are not formatted in exponential notation"""
    success, value, error = calculate("26 * 1024 / 1.04", LAST_RESULT)
    assert success and value == "25,600"


def test_history_functionality() -> None:
    """Test history reference with ?"""
    success, value, error = calculate("5 + 3", LAST_RESULT)
    assert success and value == "8"
    success, value, error = calculate("? * 2", "8")
    assert success and value == "16"
    success, value, error = calculate("? + ?", "16")
    assert success and value == "32"


def test_unit_removal() -> None:
    """Test removal of non-time units from expressions"""
    success, value, error = calculate("1,024 GB / 4", LAST_RESULT)
    assert success and value == "256"

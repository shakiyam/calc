from calc.__main__ import calculate

LAST_RESULT = "0"


def test_time_formats() -> None:
    """Test various time format inputs"""
    # Basic formats
    success, value, error = calculate("01:30:45", LAST_RESULT)
    assert success and value == "01:30:45"
    success, value, error = calculate("00:01:30.500000", LAST_RESULT)
    assert success and value == "00:01:30.500000"
    success, value, error = calculate("60s", LAST_RESULT)
    assert success and value == "00:01:00"
    success, value, error = calculate("30min", LAST_RESULT)
    assert success and value == "00:30:00"
    success, value, error = calculate("5hr", LAST_RESULT)
    assert success and value == "05:00:00"
    success, value, error = calculate("1 day", LAST_RESULT)
    assert success and value == "1 day"
    success, value, error = calculate("2d", LAST_RESULT)
    assert success and value == "2 days"
    # Compact combinations
    success, value, error = calculate("1h 30m", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("1m 5s", LAST_RESULT)
    assert success and value == "00:01:05"
    # Day and combinations
    success, value, error = calculate("1 day and 10 hours", LAST_RESULT)
    assert success and value == "1 day and 10:00:00"
    success, value, error = calculate("1 day and 1 hour 2 min", LAST_RESULT)
    assert success and value == "1 day and 01:02:00"
    # Natural language
    success, value, error = calculate("1 day 2 hours 30 minutes", LAST_RESULT)
    assert success and value == "1 day and 02:30:00"
    success, value, error = calculate("2 hours and 30 minutes", LAST_RESULT)
    assert success and value == "02:30:00"
    # Days + minutes + seconds without hours
    success, value, error = calculate("1d 30m 15s", LAST_RESULT)
    assert success and value == "1 day and 00:30:15"
    success, value, error = calculate("1日30分15秒", LAST_RESULT)
    assert success and value == "1 day and 00:30:15"
    # "and" at any junction
    success, value, error = calculate("1 day and 2 hours 15 sec", LAST_RESULT)
    assert success and value == "1 day and 02:00:15"
    success, value, error = calculate(
        "1 day and 2 hours and 30 minutes and 15 seconds", LAST_RESULT
    )
    assert success and value == "1 day and 02:30:15"


def test_japanese_time_formats() -> None:
    """Test Japanese time format support"""
    # Basic formats
    success, value, error = calculate("1時間", LAST_RESULT)
    assert success and value == "01:00:00"
    success, value, error = calculate("30分", LAST_RESULT)
    assert success and value == "00:30:00"
    success, value, error = calculate("45秒", LAST_RESULT)
    assert success and value == "00:00:45"
    success, value, error = calculate("2日", LAST_RESULT)
    assert success and value == "2 days"
    # With 間
    success, value, error = calculate("30分間", LAST_RESULT)
    assert success and value == "00:30:00"
    success, value, error = calculate("45秒間", LAST_RESULT)
    assert success and value == "00:00:45"
    success, value, error = calculate("2日間", LAST_RESULT)
    assert success and value == "2 days"
    # Combinations with spaces
    success, value, error = calculate("1時間 30分", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("2日 3時間", LAST_RESULT)
    assert success and value == "2 days and 03:00:00"
    success, value, error = calculate("1日 2時間 30分", LAST_RESULT)
    assert success and value == "1 day and 02:30:00"
    # "と" at any junction
    success, value, error = calculate("1時間と30分", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("1日と2時間と30分と15秒", LAST_RESULT)
    assert success and value == "1 day and 02:30:15"
    # Combinations without spaces
    success, value, error = calculate("1時間30分", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("5分30秒", LAST_RESULT)
    assert success and value == "00:05:30"


def test_time_operations() -> None:
    """Test time arithmetic operations"""
    success, value, error = calculate("00:01:00 + 30s", LAST_RESULT)
    assert success and value == "00:01:30"
    success, value, error = calculate("01:00:00 - 30s", LAST_RESULT)
    assert success and value == "00:59:30"
    success, value, error = calculate("00:30:00 * 2", LAST_RESULT)
    assert success and value == "01:00:00"
    success, value, error = calculate("02:00:00 / 2", LAST_RESULT)
    assert success and value == "01:00:00"
    success, value, error = calculate("0.5 day and 06:00:00 + 30s", LAST_RESULT)
    assert success and value == "18:00:30"
    success, value, error = calculate("1h + 30min", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("30min - 5s", LAST_RESULT)
    assert success and value == "00:29:55"
    success, value, error = calculate("1時間 + 30分", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("2時間 - 15分", LAST_RESULT)
    assert success and value == "01:45:00"
    # Negative results round-trip through history reuse
    success, value, error = calculate("0:00:00 - 0:00:01", LAST_RESULT)
    assert success and value == "-00:00:01"
    success, value, error = calculate("? + 0:00:02", "-00:00:01")
    assert success and value == "00:00:01"


def test_time_with_thousands_separator() -> None:
    """Test time units with thousands separator in numbers"""
    success, value, error = calculate("1,234s", LAST_RESULT)
    assert success and value == "00:20:34"


def test_time_functions() -> None:
    """Test functions with time values"""
    success, value, error = calculate("ceil(0.1s)", LAST_RESULT)
    assert success and value == "00:00:01"
    success, value, error = calculate("floor(0.9s)", LAST_RESULT)
    assert success and value == "00:00:00"
    success, value, error = calculate("round(0.7s)", LAST_RESULT)
    assert success and value == "00:00:01"
    success, value, error = calculate("round(2.5s)", LAST_RESULT)
    assert success and value == "00:00:03"
    success, value, error = calculate("roundeven(2.5s)", LAST_RESULT)
    assert success and value == "00:00:02"
    success, value, error = calculate("max(1 day, 02:00:00)", LAST_RESULT)
    assert success and value == "1 day"
    success, value, error = calculate("min(01:00:00, 90s)", LAST_RESULT)
    assert success and value == "00:01:30"
    success, value, error = calculate("sum(1:00:00, 2:00:00)", LAST_RESULT)
    assert success and value == "03:00:00"
    success, value, error = calculate("avg(1:00:00, 3:00:00)", LAST_RESULT)
    assert success and value == "02:00:00"

from calc.__main__ import _extract_output_directive, calculate

LAST_RESULT = "0"


def test_extract_output_directive() -> None:
    """Test extraction of trailing output format directive"""
    # Trailing directive is extracted
    assert _extract_output_directive("1h30m as japanese") == ("1h30m", "japanese")
    assert _extract_output_directive("1h + 30min as min") == ("1h + 30min", "min")
    assert _extract_output_directive("? as jp") == ("?", "jp")

    # Unknown words are extracted as-is (validated later)
    assert _extract_output_directive("1h as MIN") == ("1h", "MIN")

    # No directive passes through unchanged
    assert _extract_output_directive("1h30m") == ("1h30m", None)
    assert _extract_output_directive("1 + 2") == ("1 + 2", None)

    # "as" not at the end is not a directive
    assert _extract_output_directive("1h as jp + 1h") == ("1h as jp + 1h", None)

    # "as" inside a word is not a directive
    assert _extract_output_directive("1 has 2") == ("1 has 2", None)

    # Dangling "as" without a word is not a directive
    assert _extract_output_directive("1h as") == ("1h as", None)


def test_style_formats() -> None:
    """Test style format directives (default/japanese/english)"""
    success, value, error = calculate("1h + 30min as japanese", LAST_RESULT)
    assert success and value == "1時間30分"
    success, value, error = calculate("1h30m as english", LAST_RESULT)
    assert success and value == "1h 30m"
    success, value, error = calculate("1h30m as default", LAST_RESULT)
    assert success and value == "01:30:00"
    success, value, error = calculate("1h30m as colon", LAST_RESULT)
    assert success and value == "01:30:00"
    # With days
    success, value, error = calculate("1d 2h 30m 15s as japanese", LAST_RESULT)
    assert success and value == "1日2時間30分15秒"
    success, value, error = calculate("1d 30m 15s as english", LAST_RESULT)
    assert success and value == "1d 30m 15s"
    # Fractional seconds
    success, value, error = calculate("1.5s as japanese", LAST_RESULT)
    assert success and value == "1.5秒"
    # Negative and zero
    success, value, error = calculate("0s - 30min as japanese", LAST_RESULT)
    assert success and value == "-30分"
    success, value, error = calculate("1h - 1h as english", LAST_RESULT)
    assert success and value == "0s"


def test_style_format_aliases() -> None:
    """Test format name aliases"""
    for alias in ["jp", "ja"]:
        success, value, error = calculate(f"1h30m as {alias}", LAST_RESULT)
        assert success and value == "1時間30分"
    success, value, error = calculate("1h30m as en", LAST_RESULT)
    assert success and value == "1h 30m"


def test_style_format_round_trip() -> None:
    """Test that formatted output re-parses to the same value"""
    for expression, fmt in [
        ("1d 30m 15s", "japanese"),
        ("1d 2h 30m 15s", "english"),
        ("0s - 30min", "japanese"),
        ("0s - 30min", "english"),
        ("1.5s", "japanese"),
        ("1h - 1h", "english"),
    ]:
        success, formatted, error = calculate(f"{expression} as {fmt}", LAST_RESULT)
        assert success
        success, reparsed, error = calculate(f"{formatted} as {fmt}", LAST_RESULT)
        assert success and reparsed == formatted


def test_unknown_format_error() -> None:
    """Test that an unknown format directive is an error"""
    success, value, error = calculate("2 + 3 as foo", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unknown format: 'foo'" in error
    # Format names are lowercase only
    success, value, error = calculate("1h30m as JAPANESE", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unknown format: 'JAPANESE'" in error


def test_directive_on_non_time_result() -> None:
    """Test that a directive on a plain number result is an error"""
    success, value, error = calculate("2 + 3 as japanese", LAST_RESULT)
    assert not success and value == LAST_RESULT
    assert "'japanese' format only applies to time values" in error
    # Plain number formatting is unaffected when no directive is given
    success, value, error = calculate("2 + 3", LAST_RESULT)
    assert success and value == "5"

from datetime import timedelta
from decimal import Decimal

from calc.time_utils import (
    convert_time_expressions,
    format_colon,
    format_english,
    format_japanese,
    to_scalar,
)


def test_convert_time_expressions() -> None:
    """Test conversion of natural language time to timedelta constructors"""
    # Basic units
    assert convert_time_expressions("60s") == "timedelta(seconds=60)"
    assert convert_time_expressions("30min") == "timedelta(minutes=30)"
    assert convert_time_expressions("5hr") == "timedelta(hours=5)"
    assert convert_time_expressions("1 day") == "timedelta(days=1)"

    # Japanese units
    assert convert_time_expressions("1時間") == "timedelta(hours=1)"
    assert convert_time_expressions("30分") == "timedelta(minutes=30)"
    assert convert_time_expressions("45秒") == "timedelta(seconds=45)"
    assert convert_time_expressions("2日") == "timedelta(days=2)"

    # Combinations
    assert convert_time_expressions("1h 30m") == "timedelta(hours=1, minutes=30)"
    assert convert_time_expressions("1 day and 10 hours") == "timedelta(days=1, hours=10)"
    assert convert_time_expressions("1時間30分") == "timedelta(hours=1, minutes=30)"
    assert convert_time_expressions("1d 30m 15s") == ("timedelta(days=1, minutes=30, seconds=15)")
    assert convert_time_expressions("1日30分15秒") == ("timedelta(days=1, minutes=30, seconds=15)")

    # "and" at any junction
    assert convert_time_expressions("1 day and 2 hours 15 sec") == (
        "timedelta(days=1, hours=2, seconds=15)"
    )
    assert convert_time_expressions("1 day and 30 min 15 sec") == (
        "timedelta(days=1, minutes=30, seconds=15)"
    )
    assert convert_time_expressions("1 day 2 hours and 30 min") == (
        "timedelta(days=1, hours=2, minutes=30)"
    )
    assert convert_time_expressions("2 hours and 30 min 15 sec") == (
        "timedelta(hours=2, minutes=30, seconds=15)"
    )
    assert convert_time_expressions("1 day and 2 hours and 30 minutes and 15 seconds") == (
        "timedelta(days=1, hours=2, minutes=30, seconds=15)"
    )

    # "と" at any junction (Japanese)
    assert convert_time_expressions("1時間と30分") == "timedelta(hours=1, minutes=30)"
    assert convert_time_expressions("1日と2時間と30分") == (
        "timedelta(days=1, hours=2, minutes=30)"
    )
    assert convert_time_expressions("1日と30分15秒") == (
        "timedelta(days=1, minutes=30, seconds=15)"
    )

    # HH:MM:SS format
    assert convert_time_expressions("01:30:45") == "timedelta(hours=1, minutes=30, seconds=45)"

    # HH:MM:SS with microseconds
    assert convert_time_expressions("00:01:30.500000") == (
        "timedelta(hours=0, minutes=1, seconds=30, microseconds=500000)"
    )

    # Days and time
    assert convert_time_expressions("1 day and 10:00:00") == (
        "timedelta(days=1, hours=10, minutes=0, seconds=0)"
    )


def test_format_colon() -> None:
    """Test formatting of timedelta to colon-separated display string"""
    # Basic time
    assert format_colon(timedelta(hours=1, minutes=30, seconds=45)) == "01:30:45"
    assert format_colon(timedelta(seconds=60)) == "00:01:00"
    assert format_colon(timedelta(hours=5)) == "05:00:00"

    # With microseconds
    assert format_colon(timedelta(minutes=1, seconds=30, microseconds=500000)) == "00:01:30.500000"

    # Days only
    assert format_colon(timedelta(days=1)) == "1 day"
    assert format_colon(timedelta(days=2)) == "2 days"
    assert format_colon(timedelta(days=-1)) == "-1 day"

    # Days and time
    assert format_colon(timedelta(days=1, hours=10)) == "1 day and 10:00:00"
    assert format_colon(timedelta(days=2, hours=3, minutes=30)) == "2 days and 03:30:00"
    assert format_colon(timedelta(days=1, hours=1, minutes=2)) == "1 day and 01:02:00"

    # Fractional days
    assert format_colon(timedelta(days=0.5, hours=6, seconds=30)) == "18:00:30"

    # Negative: sign first, absolute decomposition
    assert format_colon(timedelta(seconds=-1)) == "-00:00:01"
    assert format_colon(timedelta(microseconds=-500000)) == "-00:00:00.500000"
    assert format_colon(-timedelta(days=1, hours=1)) == "-1 day and 01:00:00"


def test_format_japanese() -> None:
    """Test formatting of timedelta to Japanese display string"""
    # Zero components are omitted
    assert format_japanese(timedelta(hours=1, minutes=30)) == "1時間30分"
    assert format_japanese(timedelta(days=2)) == "2日"
    assert format_japanese(timedelta(days=1, minutes=30, seconds=15)) == "1日30分15秒"
    assert format_japanese(timedelta(days=1, hours=2, minutes=30, seconds=15)) == "1日2時間30分15秒"

    # All-zero
    assert format_japanese(timedelta(0)) == "0秒"

    # Fractional seconds as decimal
    assert format_japanese(timedelta(seconds=1, microseconds=500000)) == "1.5秒"
    assert format_japanese(timedelta(microseconds=500000)) == "0.5秒"

    # Negative: sign first, absolute decomposition
    assert format_japanese(timedelta(minutes=-30)) == "-30分"
    assert format_japanese(-timedelta(days=1, hours=2)) == "-1日2時間"


def test_format_english() -> None:
    """Test formatting of timedelta to English display string"""
    # Zero components are omitted
    assert format_english(timedelta(hours=1, minutes=30)) == "1h 30m"
    assert format_english(timedelta(days=2)) == "2d"
    assert format_english(timedelta(days=1, minutes=30, seconds=15)) == "1d 30m 15s"
    assert format_english(timedelta(days=1, hours=2, minutes=30, seconds=15)) == "1d 2h 30m 15s"

    # All-zero
    assert format_english(timedelta(0)) == "0s"

    # Fractional seconds as decimal
    assert format_english(timedelta(seconds=1, microseconds=500000)) == "1.5s"
    assert format_english(timedelta(microseconds=500000)) == "0.5s"

    # Negative: sign first, absolute decomposition
    assert format_english(timedelta(minutes=-30)) == "-30m"
    assert format_english(-timedelta(days=1, hours=2)) == "-1d 2h"


def test_to_scalar() -> None:
    """Test conversion of timedelta to a Decimal value in a unit"""
    assert to_scalar(timedelta(hours=1, minutes=30), "sec") == Decimal("5400")
    assert to_scalar(timedelta(hours=1, minutes=30), "min") == Decimal("90")
    assert to_scalar(timedelta(hours=1, minutes=30), "hour") == Decimal("1.5")
    assert to_scalar(timedelta(hours=1, minutes=30), "day") == Decimal("0.0625")

    # Negative, zero, and sub-second values are exact
    assert to_scalar(timedelta(minutes=-90), "min") == Decimal("-90")
    assert to_scalar(timedelta(0), "sec") == Decimal("0")
    assert to_scalar(timedelta(microseconds=500000), "sec") == Decimal("0.5")

    # Repeating decimals match plain Decimal division
    assert to_scalar(timedelta(minutes=10), "hour") == Decimal(10) / Decimal(60)

from datetime import timedelta

from calc.time_utils import convert_time_expressions, format_time


def test_convert_time_expressions():
    """Test conversion of natural language time to timedelta constructors"""
    # Basic units
    assert convert_time_expressions('60s') == 'timedelta(seconds=60)'
    assert convert_time_expressions('30min') == 'timedelta(minutes=30)'
    assert convert_time_expressions('5hr') == 'timedelta(hours=5)'
    assert convert_time_expressions('1 day') == 'timedelta(days=1)'

    # Japanese units
    assert convert_time_expressions('1時間') == 'timedelta(hours=1)'
    assert convert_time_expressions('30分') == 'timedelta(minutes=30)'
    assert convert_time_expressions('45秒') == 'timedelta(seconds=45)'
    assert convert_time_expressions('2日') == 'timedelta(days=2)'

    # Combinations
    assert convert_time_expressions('1h 30m') == 'timedelta(hours=1, minutes=30)'
    assert convert_time_expressions('1 day and 10 hours') == 'timedelta(days=1, hours=10)'
    assert convert_time_expressions('1時間30分') == 'timedelta(hours=1, minutes=30)'

    # HH:MM:SS format
    assert convert_time_expressions('01:30:45') == 'timedelta(hours=1, minutes=30, seconds=45)'

    # HH:MM:SS with microseconds
    assert convert_time_expressions('00:01:30.500000') == (
        'timedelta(hours=0, minutes=1, seconds=30, microseconds=500000)'
    )

    # Days and time
    assert convert_time_expressions('1 day and 10:00:00') == (
        'timedelta(days=1, hours=10, minutes=0, seconds=0)'
    )


def test_format_time():
    """Test formatting of timedelta to display string"""
    # Basic time
    assert format_time(timedelta(hours=1, minutes=30, seconds=45)) == '01:30:45'
    assert format_time(timedelta(seconds=60)) == '00:01:00'
    assert format_time(timedelta(hours=5)) == '05:00:00'

    # With microseconds
    assert format_time(timedelta(minutes=1, seconds=30, microseconds=500000)) == '00:01:30.500000'

    # Days only
    assert format_time(timedelta(days=1)) == '1 day'
    assert format_time(timedelta(days=2)) == '2 days'
    assert format_time(timedelta(days=-1)) == '-1 day'

    # Days and time
    assert format_time(timedelta(days=1, hours=10)) == '1 day and 10:00:00'
    assert format_time(timedelta(days=2, hours=3, minutes=30)) == '2 days and 03:30:00'
    assert format_time(timedelta(days=1, hours=1, minutes=2)) == '1 day and 01:02:00'

    # Fractional days
    assert format_time(timedelta(days=0.5, hours=6, seconds=30)) == '18:00:30'

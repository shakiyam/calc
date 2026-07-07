import io
import sys

import pytest

from calc.__main__ import calculate, main

LAST_RESULT = "999"


def test_syntax_errors() -> None:
    """Test syntax error handling"""
    success, value, error = calculate("", LAST_RESULT)
    assert success and value == LAST_RESULT
    success, value, error = calculate("1 +", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Invalid syntax"
    success, value, error = calculate("(", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Invalid syntax"
    success, value, error = calculate("import os", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Invalid syntax"


def test_ambiguous_comma_errors() -> None:
    """Test that commas not matching thousands grouping are rejected with a clear message"""
    success, value, error = calculate("1,20", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Invalid comma" in error


def test_security_errors() -> None:
    """Test security-related error handling"""
    success, value, error = calculate('open("test.txt")', LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unsupported constant type: str" in error


def test_runtime_errors() -> None:
    """Test runtime error handling"""
    success, value, error = calculate("1 / 0", LAST_RESULT)
    assert not success and value == LAST_RESULT and error == "Division by zero"
    success, value, error = calculate("sqrt(-1)", LAST_RESULT)
    assert (
        not success
        and value == LAST_RESULT
        and ("math domain error" in error or "expected a nonnegative input" in error)
    )


def test_function_argument_errors() -> None:
    """Test function argument error handling"""
    success, value, error = calculate("min()", LAST_RESULT)
    assert (
        not success and value == LAST_RESULT and "min expected at least 1 argument, got 0" in error
    )
    success, value, error = calculate("max()", LAST_RESULT)
    assert (
        not success and value == LAST_RESULT and "max expected at least 1 argument, got 0" in error
    )
    success, value, error = calculate("avg()", LAST_RESULT)
    assert (
        not success and value == LAST_RESULT and "avg expected at least 1 argument, got 0" in error
    )


def test_keyword_unpacking_errors() -> None:
    """Test that ** argument unpacking is rejected instead of silently ignored"""
    success, value, error = calculate("sum(1, **2)", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unsupported" in error and "**" in error


def test_time_related_errors() -> None:
    """Test time-related error handling"""
    success, value, error = calculate("25:99:99", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Invalid time format" in error
    success, value, error = calculate("03:00:00 + 2", LAST_RESULT)
    assert not success and value == LAST_RESULT and "Unsupported operation" in error
    success, value, error = calculate("sum(1:00:00, 60)", LAST_RESULT)
    assert (
        not success and value == LAST_RESULT and "Cannot mix timedelta and Decimal in sum" in error
    )


def test_main_arg_mode_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an error in argument mode exits with code 1"""
    monkeypatch.setattr(sys, "argv", ["calc", "1/0"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_arg_mode_success_exits_0(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a successful calculation in argument mode exits with code 0"""
    monkeypatch.setattr(sys, "argv", ["calc", "1+1"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0


def test_main_piped_error_exits_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that piped input keeps processing all lines and exits with code 1 on any error"""
    monkeypatch.setattr(sys, "argv", ["calc"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("1+1\n1/0\n2+2\n"))
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
    out = capsys.readouterr().out
    assert "= 2" in out and "Error: Division by zero" in out and "= 4" in out


def test_main_piped_all_success_exits_0(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that piped input without errors exits with code 0"""
    monkeypatch.setattr(sys, "argv", ["calc"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("1+1\n2+2\n"))
    main()
    assert capsys.readouterr().out == "= 2\n= 4\n"


def test_main_piped_unknown_format_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an unknown format command in piped input exits with code 1"""
    monkeypatch.setattr(sys, "argv", ["calc"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("format banana\n"))
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_interactive_error_exits_0(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the interactive shell exits with code 0 even after errors"""
    monkeypatch.setattr(sys, "argv", ["calc"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("calc.__main__._input_lines", lambda: iter(["1/0", "exit"]))
    main()

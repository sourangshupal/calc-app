"""Unit tests for calculator arithmetic functions."""

import pytest

from calc_app.calculator import add, divide, multiply, sqrt, subtract


def test_add() -> None:
    assert add(10.0, 2.0) == 12.0


def test_subtract() -> None:
    assert subtract(10.0, 2.0) == 8.0


def test_multiply() -> None:
    assert multiply(10.0, 2.0) == 20.0


def test_divide() -> None:
    assert divide(10.0, 4.0) == 2.5


def test_divide_by_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        divide(10.0, 0.0)


def test_sqrt() -> None:
    assert sqrt(9.0) == 3.0
    assert sqrt(0.0) == 0.0
    assert sqrt(2.0) == pytest.approx(1.41421356237)


def test_sqrt_negative() -> None:
    with pytest.raises(ValueError, match="Square root of negative number"):
        sqrt(-1.0)

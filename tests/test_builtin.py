"""
Test suite for the error wrappers on as alternative to builtin primitives.

@date: 15.10.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from dataclasses import dataclass
import pytest
from exhausterr import (
    Ok,
    Err,
    safe_int_divide,
    safe_divide,
    safe_getattr,
    safe_getitem,
    ZeroDivision,
    BadKey,
    BadAttribute,
)


@pytest.mark.parametrize("a,b", [(5, 0), (5, 2)])
def test_safe_divide(a: float, b: float) -> None:
    match safe_divide(a, b):
        case Ok(value):
            assert b != 0
            assert value == a / b

        case Err(err):
            assert isinstance(err, ZeroDivision)


@pytest.mark.parametrize("a,b", [(5, 0), (5, 2)])
def test_safe_int_divide(a: int, b: int) -> None:
    match safe_int_divide(a, b):
        case Ok(value):
            assert b != 0
            assert value == a // b

        case Err(err):
            assert isinstance(err, ZeroDivision)


def test_safe_getattr() -> None:
    @dataclass
    class Dummy:
        a: int = 1
        b: int = 2

    dummy = Dummy()
    for attr in ["a", "b", "c"]:
        match safe_getattr(dummy, attr):
            case Ok(value):
                assert attr in ("a", "b")
                assert value == getattr(dummy, attr)

            case Err(err):
                assert attr == "c"
                assert isinstance(err, BadAttribute)


def test_safe_getitem() -> None:
    dummy = {"a": 1, "b": 2}
    for attr in ["a", "b", "c"]:
        match safe_getitem(dummy, attr):
            case Ok(value):
                assert attr in ("a", "b")
                assert value == dummy[attr]

            case Err(err):
                assert attr == "c"
                assert isinstance(err, BadKey)

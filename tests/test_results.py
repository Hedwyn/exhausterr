"""
Test suite for results objects.

@date: 16.08.2024
@author: Baptiste Pestourie
"""

from typing import assert_never

import pytest
from exhausterr import AbstractResult, Result, Ok, Err
from test_errors import BasicError


def fails_on_true(should_fail: bool) -> Result[bool, BasicError]:
    if should_fail:
        return Err(BasicError)
    return Ok(True)


def test_basic_result() -> None:
    """
    Test basic result.
    """
    result = fails_on_true(False)
    assert isinstance(result, AbstractResult)
    # checking __bool__
    assert result

    result = fails_on_true(True)
    assert isinstance(result, AbstractResult)
    assert isinstance(result.error, BasicError)
    assert not result, repr((result._ret, result.err))


@pytest.mark.parametrize("successful", [True, False])
def test_result_matching(successful: bool) -> None:
    """
    Test basic result.
    """
    result = fails_on_true(not successful)
    match result:
        case Ok(value):
            assert successful
            assert value is True
        case Err(error):
            assert not successful
            assert isinstance(error, BasicError)
        case _ as x:
            assert_never(x)
            assert False, "Unexpected result type"

    match result:
        case Ok(value):
            assert successful
            assert value is True
        case Err(error):
            assert not successful
            assert isinstance(error, BasicError)
        case _ as x:
            assert_never(x)
            assert False, "Unexpected result type"


def test_result_unwrap() -> None:
    """
    Checks that unwrap() raises an exception when the result is an error
    and returns the value when it is not.
    """
    fails = fails_on_true(True)
    with pytest.raises(Exception):
        fails.unwrap()

    assert fails_on_true(False).unwrap() is True
    fails = fails_on_true(True)
    with pytest.raises(Exception):
        fails.unwrap()

    assert fails_on_true(False).unwrap() is True

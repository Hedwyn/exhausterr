"""
Test suite for Result mapping primitives

@date: 14.10.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from functools import partial
from exhausterr import resultify, result_mapper, Ok, Error, Err, Result, result_reducer, chain_results


class ZeroDivision(Error):
    description = "Cannot divide by zero"


def test_resultify() -> None:
    """
    Sanity checks for resultify().
    """
    values = range(100)
    for result in resultify(values):
        assert isinstance(result, Ok)


# test primitives
def invert(value: float) -> Result[float, ZeroDivision]:
    if value == 0:
        return Err(ZeroDivision())
    return Ok(1 / value)


def subtract_to_one_and_invert(value: float) -> Result[float, ZeroDivision]:
    if value == 1.0:
        return Err(ZeroDivision())
    return Ok(1 / (1 - value))


def test_result_mapper_single_function() -> None:
    """
    Tests the result mapper with a single map function
    """
    values = range(5)
    mapped = list(result_mapper(values, invert))
    assert mapped[1:5] == [Ok(1.0), Ok(1 / 2), Ok(1 / 3), Ok(1 / 4)]
    assert not mapped[0]
    assert type(mapped[0].error) is ZeroDivision


def test_result_mapper_multiple_function() -> None:
    """
    Tests the result mapper with multiple functions composed
    """

    def expects(value: float) -> float:
        return 1 / (1 - (1 / value))

    values = range(5)
    mapped = list(result_mapper(values, invert, subtract_to_one_and_invert))
    assert mapped[2:5] == [Ok(expects(2)), Ok(expects(3)), Ok(expects(4))]
    assert not mapped[0]
    assert not mapped[1]
    assert type(mapped[0].error) is ZeroDivision
    assert type(mapped[1].error) is ZeroDivision

def test_result_reducer_ok_case() -> None:
    """
    Tests the result reducer
    """
    assert result_reducer(
        Ok(2), Ok(3), Ok(5),
        initializer=0,
        reducer=lambda a,b: a + b,
    ) ==  Ok(10)

    l = [1]
    assert result_reducer(
        Ok(2), Ok(3), Ok(5),
        initializer=l,
        reducer=lambda l, a: l + [a],
    ) ==  Ok([1, 2,3,5])

def test_result_reducer_err_case_case() -> None:
    """
    Tests the result reducer
    """
    assert result_reducer(
        Ok(2), Err(), Ok(5),
        initializer=0,
        reducer=lambda a,b: a + b,
    ) ==  Err()

def test_result_chain_ok_case() -> None:
    """
    Tests the result reducer
    """
    def get_number(number: int) -> Ok[int]:
        return Ok(number)

    assert chain_results(
        partial(get_number, 2),
        partial(get_number, 3), 
        partial(get_number, 5), 
        initializer=0,
        reducer=lambda a,b: a + b,
    ) ==  Ok(10)

    l = [1]

    assert chain_results(
        partial(get_number, 2),
        partial(get_number, 3), 
        partial(get_number, 5), 
        initializer=l,
        reducer=lambda l, a: l + [a],
    ) ==  Ok([1,2,3,5])

def test_result_chain_err_case() -> None:
    """
    Tests the result reducer
    """
    def get_number(number: int):
        return Ok(number)
    
    def do_err():
        return Err()
    
    # we want to make sure that panic is never run
    def panic():
        raise RuntimeError()

    assert chain_results(
        partial(get_number, 2),
        do_err,
        panic,
        initializer=0,
        reducer=lambda a,b: a + b,
    ) ==  Err()
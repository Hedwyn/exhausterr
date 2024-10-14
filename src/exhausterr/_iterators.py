"""
Some convenience iteration and composition tools around Results.

@date: 14.10.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from typing import Iterable, overload, Iterator, TypeVar, Callable, Any

from ._results import Ok, Result, Err
from ._errors import Error

R = TypeVar("R")

# --- Bunch of type variables for composition ---
_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")


def resultify(values: Iterable[R]) -> Iterator[Ok[R]]:
    """
    Maps bunch of values to Ok() results.
    """
    return map(Ok, values)


@overload
def result_mapper(
    collection: Iterable[_A], func1: Callable[[_A], Result[_B, Error]], /
) -> Iterable[Result[_B, Error]]: ...


@overload
def result_mapper(
    collection: Iterable[_A],
    func1: Callable[[_A], Result[_B, Error]],
    func2: Callable[[_B], Result[_C, Error]],
    /,
) -> Iterable[Result[_C, Error]]: ...


@overload
def result_mapper(
    collection: Iterable[_A],
    func1: Callable[[_A], Result[_B, Error]],
    func2: Callable[[_B], Result[_C, Error]],
    func3: Callable[[_C], Result[_D, Error]],
    /,
) -> Iterable[Result[_D, Error]]: ...


@overload
def result_mapper(
    collection: Iterable[_A],
    func1: Callable[[_A], Result[_B, Error]],
    func2: Callable[[_B], Result[_C, Error]],
    func3: Callable[[_C], Result[_D, Error]],
    func4: Callable[[_D], Result[_E, Error]],
    /,
) -> Iterable[Result[_E, Error]]: ...


def result_mapper(
    collection: Iterable[Any], *funcs: Callable[[Any], Result[Any, Error]]
) -> Iterable[Result[Any, Error]]:
    """
    Composes functions together and used the composed function to map values from a collection.

    Yields
    -------
    For every value `v` in `collection`
    (func_n => func_n-1 => ... => func_1)(v)
    (`=>` denoting composition), when all func return Ok.
    For any k in n for which func_n would return an Err(),
    skips all the next funcs and returns the Err for that k.

    Parameters
    ----------
    collection: Iterable[Any]
        The values to map.

    funcs: Iterable[Callable[[A], Result[B, Error]]]
        Functions to compose together
    """
    for item in collection:
        _result: Result[Any, Error] = Ok(item)
        _error: Error | None = None
        for func in funcs:
            match _result:
                case Ok(value):
                    _result = func(value)
                case Err(error):
                    _error = error
                    break

        if _error is not None:
            yield Err(_error)
        else:
            yield _result

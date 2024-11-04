"""
Some convenience iteration and composition tools around Results.

@date: 14.10.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from typing import (
    Iterable,
    cast,
    assert_never,
    overload,
    Iterator,
    TypeVar,
    Callable,
    Any,
    reveal_type,
)

from ._results import Ok, Result, Err, NoneOr
from ._errors import Error

R = TypeVar("R")

# --- Bunch of type variables for composition ---
_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
T = TypeVar("T")


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


@overload
def result_reducer(
    *results: Result[Any, Error],
    reducer: None,
    initializer: None,
) -> NoneOr[Error]: ...


@overload
def result_reducer(
    *results: Result[Any, Error],
    reducer: Callable[[T, Any], T],
    initializer: T,
) -> Result[T, Error]: ...


def result_reducer(
    *results: Result[Any, Error],
    reducer: Callable[[T, Any], T] | None = None,
    initializer: T | None = None,
) -> Result[Any, Error]:
    """
    Similar to functools.reduce, except it operates
    on Result objects and stops on the first error encountered.
    If getting any error while chaining, returns the error.
    Otherwise, reduces the value wrapped by `Ok`.
    Reduction is defined by:
    reduce(Seq[n + 1]) = reduce(reduce(Seq[0..n]), Seq[n + 1])
    with value for the first call being `initializer`.

    Examples
    --------
    >>> result_reducer(
        [Ok(2), Ok(3), Ok(5)],
        initializer=[],
        reducer=list.append
    )
    Ok([2,3,5])

    >>> result_reducer(
        [Ok(2), Ok(3), Ok(4)],
        initializer=0,
        reducer=sum
    )
    Ok(10)

    >>> result_reducer(
        [Ok(2), Err(3), Ok(4)],
        initializer=0,
        reducer=sum
    )
    Err(3)
    """
    reduced_value = cast(T, initializer)
    for r in results:
        match r:
            case Ok(val):
                if reducer is not None:
                    reduced_value = reducer(reduced_value, val)
            case Err(error):
                return Err(error)

            case _ as unreachable:
                assert_never(unreachable)

    return Ok(reduced_value)


@overload
def chain_results(
    *funcs: Callable[[], Result[Any, Error]],
    initializer: None,
    reducer: None,
) -> NoneOr[Error]: ...


@overload
def chain_results(
    *funcs: Callable[[], Result[T, Error]],
    initializer: T,
    reducer: Callable[[T, Any], T],
) -> Result[T, Error]: ...


def chain_results(
    *funcs: Callable[[], Result[Any, Error]],
    initializer: T | None = None,
    reducer: Callable[[T, Any], T] | None = None,
) -> Result[Any, Error]:
    """
    Similar to `result_reducer`, but takes a functions that returns
    results instead of results.
    Calls the function in `funcs` until an error is obtained
    or all or them are consumed.
    Output is the same as what `result_reducer` would
    give on the functions return values.

    See also
    --------
    result_reducer
    """
    reduced_value = cast(T, initializer)
    for f in funcs:
        res = f()
        match res:
            case Ok(val):
                if reducer:
                    reduced_value = reducer(reduced_value, val)
            case Err(error):
                return Err(error)

            case _ as unreachable:
                assert_never(unreachable)

    return Ok(reduced_value)

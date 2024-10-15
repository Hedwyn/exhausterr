"""
Some wrapper on builtin Python exceptions and primitives to allow using
them in a railway style.
Creates `Error` alter egos for some of the builtin Pythjn exceptions.
Provides equivalent primitives to some dunder-calling functions that return
`Result` instead of raising exceptions.
Note: due to Python using `Error` as suffix on builtin exceptions, we refrain from using
that keyword in the Error class names.


@date: 20.09.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from typing import ClassVar, Final, Mapping
from dataclasses import dataclass
from ._results import Result, Ok, Err
from ._errors import Error

_NO_DEFAULT: Final[object] = object()


@dataclass
class BadAttribute(Error):
    """
    The error equivalent of built-in exception AttributeError.
    Takes as parameter the object on which the attribute access failed
    as well as the attribute name.
    """

    exception_cls: ClassVar[type[Exception]] = AttributeError
    description: ClassVar[str | None] = "Object {obj} has no attribute {attr}"
    obj: object
    attr: str


@dataclass
class BadKey(Error):
    """
    The error equivalent of built-in exception KeyError.
    Takes as paramter the mapping on which the key access failed
    as well as the attribute name.
    """

    exception_cls: ClassVar[type[Exception]] = AttributeError
    description: ClassVar[str | None] = "Mapping {mapping} has no attribute {key}"
    mapping: Mapping[object, object]
    key: object


class ZeroDivision(Error):
    """
    The error equivalent of built-in exception KeyError.
    Takes as paramter the mapping on which the key access failed
    as well as the attribute name.
    """

    exception_cls: ClassVar[type[Exception]] = ZeroDivisionError
    description: ClassVar[str | None] = "Cannot divide by zero"


def safe_int_divide(a: int, b: int) -> Result[int, ZeroDivision]:
    """
    Railway variant for division for integers,
    returns  Ok(`a // b`) if `b != 0` else `Err(ZeroDivisionErr())`
    """
    if b == 0:
        return Err(ZeroDivision())
    return Ok(a // b)


def safe_divide(a: float, b: float) -> Result[float, ZeroDivision]:
    """
    Railway variant for `__truediv__` for integers,
    returns  Ok(`a // b`) if `b != 0` else `Err(ZeroDivisionErr())`
    """
    if b == 0:
        return Err(ZeroDivision())
    return Ok(a / b)


def safe_getattr(
    obj: object, attr: str, default: object = _NO_DEFAULT
) -> Result[object, BadAttribute]:
    """
    Railway variant for `getattr`.
    Unlike `getattr`, `default` can also be passed as keyword argument
    (instead of positional only).

    Returns
    -------
    Result[Any, AttributeErr]
        The attribute value if it exists.
        AttributeErr Otherwise.
    """

    found = getattr(obj, attr, default)
    if found != _NO_DEFAULT:
        return Ok(found)
    return Err(BadAttribute(obj, attr))


def safe_getitem(
    obj: Mapping[object, object], key: str, default: object = _NO_DEFAULT
) -> Result[object, BadKey]:
    """
    Railway variant for `__getitem__`, triggered by the subscript operator ([]).
    Supports default arguments as well.

    Returns
    -------
    Result[Any, KeyErr]
        The attribute value if it exists.
        AttributeErr Otherwise.
    """
    # Note: using contextlib.suppress is more elegant but slower
    try:
        return Ok(obj[key])
    except KeyError:
        if default != _NO_DEFAULT:
            return Ok(default)
        return Err(BadKey(obj, key))

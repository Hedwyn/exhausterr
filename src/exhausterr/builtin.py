"""
Maps built-in Python exceptions to dedicated error classes in this framework.
Note: due to built-in exceptions using `Error` as part of their naming convention,
error classes here use `Err` as suffix as part of their naming convention.

@date: 20.09.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from typing import Any, ClassVar, Final, Mapping
from dataclasses import dataclass
from exhausterr.results import Result, Ok, Err
from exhausterr.errors import Error

_NO_DEFAULT: Final[object] = object()


@dataclass
class AttributeErr(Error):
    """
    The error equivalent of built-in exception AttributeError.
    Takes as paramter the object on which the attribute access failed
    as well as the attribute name.
    """

    exception_cls: ClassVar[type[Exception]] = AttributeError
    description: ClassVar[str | None] = "Object {obj} has no attribute {attr}"
    obj: object
    attr: str


@dataclass
class KeyErr(Error):
    """
    The error equivalent of built-in exception KeyError.
    Takes as paramter the mapping on which the key access failed
    as well as the attribute name.
    """

    exception_cls: ClassVar[type[Exception]] = AttributeError
    description: ClassVar[str | None] = "Mapping {mapping} has no attribute {key}"
    mapping: Mapping
    key: str


def safe_getattr(
    obj: object, attr: str, default: object = _NO_DEFAULT
) -> Result[object, AttributeErr]:
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
    return Err(AttributeErr(obj, attr))


def safe_getitem(
    obj: Mapping, key: str, default: object = _NO_DEFAULT
) -> Result[object, KeyErr]:
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
        return Err(KeyErr(obj, key))

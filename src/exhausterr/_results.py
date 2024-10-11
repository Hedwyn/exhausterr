"""
An implementation of the Result object similar to Rust Results.
Result type annotations should be defined as Result[Ok_Type, Error_Type].
The error should always be a subclass of `exhausterr.errors.Error`.

Typical use case is the following:

>>> from exhausterr.result import Result, Ok, Err
>>> from exhausterr.error import Error

>>> class ZeroDivideErr(Error):
>>>     description: "Cannot divide by zero"
>>>     exception_cls = ZeroDivisionErro

>>> def divide(a: float, b: float) -> Result[float, ZeroDivideErr]:
>>>     if b == 0.:
>>>         return Err(ZeroDivideErr())
>>>     return Ok(a / b)

If your function can return multiple error types you can pass
them as normal unions, e.g., Result[float, ZeroDivideErr | OverflowErr]

If the happy path of your function returns None,
you can shorten Ok(None) to Ok(), and you may also use the
return annotation `NoneOr[YourErrorType]`,
which is equivalent to `Result[None, YourErrorType]`.


@date: 16.08.2024
@author: Baptiste Pestourie
"""

from __future__ import annotations
from typing import (
    Generic,
    TypeVar,
    Union,
    Optional,
    Final,
    Literal,
    overload,
)
from ._errors import Error
from enum import Enum, auto

V = TypeVar("V")


# -- Type Variables --- #
R = TypeVar("R")
E = TypeVar("E", bound=Union[Error, None])


class Sentinel(Enum):
    """
    Defining a Sentinel object to represent unset results
    None is not an option because it's a valid value, and
    should be differentiated from the result being unset.
    """

    NOTSET = auto()


NotsetT = Literal[Sentinel.NOTSET]

_NOTSET: Final = Sentinel.NOTSET


class AbstractResult(Generic[R, E]):
    """
    Base class for result objects Ok and Err.
    Abstract-ness is not enforced, you should however instanciate
    Results using Ok() and Err() unless you plan to extend functionalities.

    Part of the public interface for the following purposes:
        * Allow building custom classes
        * Use with isinstance() checks.

    For type hinting, use Result for Ok() and Err() objects
    rather than AbstractResult.
    """

    __match_args__ = ("value", "error")

    @overload
    def __init__(self: AbstractResult[NotsetT, E]) -> None: ...

    @overload
    def __init__(self: AbstractResult[R, None], value: R, error: None) -> None: ...

    @overload
    def __init__(self: AbstractResult[R, E], value: R, error: E) -> None: ...

    def __init__(
        self,
        value: R | NotsetT = _NOTSET,
        error: Optional[E] = None,
    ) -> None:
        """
        value: object
            Value returned by the function, if it did not error out.

        error: Error
            Error returned by the function
        """
        self.value = value
        self.error = error

    def __bool__(self) -> bool:
        """
        Returns
        -------
        bool
            False for a Result that contains an error,
            True otherwise
        """
        return self.error is None

    def unwrap(self) -> R:
        """
        Raises an exception ('panics') if this result
        is an error, otherwise, returns the result.
        """

        error = self.error

        if error is not None:
            # Note: mypy has a known issue with type narrowing
            # when using TypeVar to an optional type
            # See following mypy issue:
            # https://github.com/python/mypy/issues/12622
            # we have to forcefully ignore - mypy is incorrect in this case
            error.throw()  # type: ignore[union-attr]
        value = self.value
        if value == _NOTSET:
            raise RuntimeError(
                "This result object is empty and has never been set."
                "You should not call AbstractResult directly"
            )
        return value


class Ok(AbstractResult[R, None], Generic[R]):
    """
    A successful result.

    """

    __match_args__ = ("value",)
    error: None
    value: R

    @overload
    def __init__(self: Ok[None]) -> None: ...

    @overload
    def __init__(self: Ok[R], value: R) -> None: ...

    def __init__(self, value: R | None = None) -> None:
        """
        Parameters
        ----------
        value: R
            The returned value
        """
        super().__init__(value, None)  # type: ignore[arg-type]

    def __bool__(self) -> Literal[True]:
        """
        Returns
        -------
        bool
            False for a Result that contains an error,
            True otherwise
        """
        return True

    def __eq__(self, other: object) -> bool:
        """
        Makes the comparison of two `Ok` objects equivalent to
        compare their wrapped values.
        """
        if not isinstance(other, AbstractResult):
            return NotImplemented
        return other.error is None and self.value == other.value


class Err(AbstractResult[NotsetT, E], Generic[E]):
    """
    An error result.
    """

    __match_args__ = ("error",)

    result: NotsetT
    error: E

    def __init__(self, error: E) -> None:
        """
        Parameters
        ----------
        value: R
            The returned error
        """
        if isinstance(error, type):
            error = error()
        super().__init__(_NOTSET, error)

    def __eq__(self, other: object) -> bool:
        """
        Makes the comparison of two `Err` objects equivalent to
        compare their wrapped values.
        """
        if not isinstance(other, AbstractResult):
            return NotImplemented
        return other.error is not None and self.error == other.error

    def __bool__(self) -> Literal[False]:
        """
        Returns
        -------
        bool
            False for a Result that contains an error,
            True otherwise
        """
        return False


# --- Result type hints --- #
Result = Union[Ok[R], Err[E]]
NoneOr = Union[Ok[None], Err[E]]

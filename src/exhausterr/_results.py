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

from enum import Enum, auto
from typing import (
    Final,
    Generic,
    Literal,
    NoReturn,
    Optional,
    TypeVar,
    Union,
    cast,
)

from ._errors import Error

V = TypeVar("V")


# -- Type Variables --- #
R = TypeVar("R", bound=Optional[object])
E = TypeVar("E", bound=Optional[object], covariant=True)


class ExhausterrSentinel(Enum):
    """
    Defining a Sentinel object to represent unset results
    None is not an option because it's a valid value, and
    should be differentiated from the result being unset.
    """

    NOTSET = auto()


NotsetT = Literal[ExhausterrSentinel.NOTSET]

_NOTSET: Final = ExhausterrSentinel.NOTSET


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
    value: R | NotsetT
    error: E | NotsetT

    def __bool__(self) -> bool:
        """
        Returns
        -------
        bool
            False for a Result that contains an error,
            True otherwise
        """
        return self.error is ExhausterrSentinel.NOTSET

    def unwrap(self) -> R:
        """
        Raises an exception ('panics') if this result
        is an error, otherwise, returns the result.
        Overriden by the subclasses, Ok() and Err().
        """
        raise RuntimeError(
            "This result object is empty and has never been set."
            "You should not call AbstractResult directly"
        )


class Ok(AbstractResult[R, NotsetT], Generic[R]):
    """
    A successful result.

    """

    __match_args__ = ("value",)
    value: R

    def __init__(self, value: R = cast(R, None)) -> None:
        """
        Parameters
        ----------
        value: R
            The returned value
        """
        self.value = value
        self.error = _NOTSET

    def __repr__(self) -> str:
        """
        Shows only the internal value. Should rebuild the object when fed into eval().
        """
        return f"Ok({self.value!r})"

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
        return other.error is _NOTSET and self.value == other.value

    def unwrap(self) -> R:
        """
        Returns
        -------
        R
            Inner result value.
        """
        return self.value

    def __str__(self) -> str:
        """
        A human-friendly wrapper around the internal value __str__
        """
        return f"Ok({self.value})"

    @property
    def inner(self) -> R:
        """
        A method shared with `Err`. Returns the inner value, useful
        to iterate over multiple Results when one just wants the wrapped error or value
        regardless of whether it is an `Ok` or an `Err`.
        """
        return self.value


class Err(AbstractResult[NotsetT, E], Generic[E]):
    """
    An error result.
    """

    __match_args__ = ("error",)

    error: E

    def __init__(
        self,
        error: E = cast(E, None),
        *,
        exception_cls: type[Exception] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        value: R
            The returned error
        """
        self.error = error
        self.value = _NOTSET
        self._exception_cls = exception_cls

    def __repr__(self) -> str:
        """
        Shows only the internal error. Should rebuild the object when fed into eval().
        """
        return f"Err({self.error!r})"

    def __eq__(self, other: object) -> bool:
        """
        Makes the comparison of two `Err` objects equivalent to
        compare their wrapped values.
        """
        if not isinstance(other, AbstractResult):
            return NotImplemented
        return other.error is not _NOTSET and self.error == other.error

    def __bool__(self) -> Literal[False]:
        """
        Returns
        -------
        bool
            False for a Result that contains an error,
            True otherwise
        """
        return False

    def unwrap(self) -> NoReturn:
        """
        Returns
        -------
        R
            Inner result value.
        """
        err = self.error
        if isinstance(err, Error):
            err.throw()
        raise Exception(err)

    def __str__(self) -> str:
        """
        A human-friendly wrapper around the internal value __str__
        """
        return f"Err({self.error})"

    @property
    def inner(self) -> E:
        """
        A method shared with `Err`. Returns the inner value, useful
        to iterate over multiple Results when one just wants the wrapped error or value
        regardless of whether it is an `Ok` or an `Err`.
        """
        return self.error


# --- Result type hints --- #
Result = Union[Ok[R], Err[E]]
NoneOr = Union[Ok[None], Err[E]]

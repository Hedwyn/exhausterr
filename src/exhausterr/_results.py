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
    Iterable,
    Iterator,
    TypeVar,
    Union,
    Optional,
    Final,
    Literal,
    overload,
    NoReturn,
    Callable,
    Any,
)
from ._errors import Error
from enum import Enum, auto

V = TypeVar("V")


# -- Type Variables --- #
R = TypeVar("R")
MaybeE = TypeVar("MaybeE", bound=Union[Error, None], covariant=True)
E = TypeVar("E", bound=Error, covariant=True)


class Sentinel(Enum):
    """
    Defining a Sentinel object to represent unset results
    None is not an option because it's a valid value, and
    should be differentiated from the result being unset.
    """

    NOTSET = auto()


NotsetT = Literal[Sentinel.NOTSET]

_NOTSET: Final = Sentinel.NOTSET


class AbstractResult(Generic[R, MaybeE]):
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
    def __init__(self: AbstractResult[NotsetT, MaybeE]) -> None: ...

    @overload
    def __init__(self: AbstractResult[R, None], value: R, error: None) -> None: ...

    @overload
    def __init__(self: AbstractResult[R, MaybeE], value: R, error: MaybeE) -> None: ...

    def __init__(
        self,
        value: R | NotsetT = _NOTSET,
        error: Optional[MaybeE] = None,
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
            # Note for Python < 3.13: mypy has a known issue with type narrowing
            # when using TypeVar to an optional type
            # See following mypy issue:
            # https://github.com/python/mypy/issues/12622
            # For Python3.13+ this should be accepted without ignore comment
            error.throw()
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

    def __repr__(self) -> str:
        """
        A human-friendly wrapper around the internal value __repr__
        """
        return f"Result[Ok({repr(self.value)})]"

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

    result: NotsetT
    error: E

    def __init__(self, error: E | type[E]) -> None:
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

    def unwrap(self) -> NoReturn:
        """
        Returns
        -------
        R
            Inner result value.
        """
        self.error.throw()

    def __str__(self) -> str:
        """
        A human-friendly wrapper around the internal value __str__
        """
        return f"Err({self.error})"

    def __repr__(self) -> str:
        """
        A human-friendly wrapper around the internal value __repr__
        """
        return f"Result[Err({repr(self.error)})]"

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

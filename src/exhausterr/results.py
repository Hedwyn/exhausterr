"""
An implementation of the Result object similar to Rust Reuslts.

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
)
from exhausterr.errors import Error

V = TypeVar("V")

_NOTSET: Final[object] = object()

# -- Type Variables --- #
R = TypeVar("R")
E = TypeVar("E", bound=Error)

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

    def __init__(self, value: R = _NOTSET, error: Optional[E] = None) -> None:
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
            error.throw()
        return self.value

class Ok(AbstractResult, Generic[R]):
    """
    A successful result.

    """

    __match_args__ = ("value",)
    error: None

    def __init__(self, value: R) -> None:
        """
        Parameters
        ----------
        value: R
            The returned value
        """
        super().__init__(value, None)


class Err(AbstractResult, Generic[E]):
    """
    An error result.
    """

    __match_args__ = ("error",)
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

# --- Result type hints --- #
Result = Union[Ok[R], Err[E]]
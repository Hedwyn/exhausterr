"""
Base layer for error types.

@author: Baptiste Pestourie
@date: 16.08.2024
"""

from __future__ import annotations
from typing import (
    NoReturn,
    Any,
    ClassVar,
)
from functools import cached_property
from dataclasses import is_dataclass, dataclass, field, asdict


@dataclass
class Error:
    """
    Base representation for an error.

    If you want your error to support arguments, decorate it
    with @dataclass and declare your arguments as fields.
    Private variables (starting with '_') are excluded from
    args property.


    Class parameters
    ----------------
    description: str
        The description for the error, with optional format arguments.
        F-string arguments should match argument names.

    exception_cls: type[Exception]
        When raising that error as an execption,
        the exception class that will be used.
    """

    description: ClassVar[str | None] = None
    exception_cls: ClassVar[type[Exception]] = Exception
    _notes: list[str] = field(
        init=False, compare=False, hash=False, default_factory=list
    )

    @cached_property
    def _is_dataclass(self) -> bool:
        """
        Returns
        -------
        bool
            Whether this object is a dataclass
        """
        return is_dataclass(self)

    @property
    def args(self) -> dict[str, Any]:
        """
        Returns
        -------
        dict[str, Any]
            Dict containing the arguments and their current values
        """
        return {name: value for name, value in asdict(self).items() if name[0] != "_"}

    def add_notes(self, *notes: str) -> None:
        """
        Adds a note to give more details on this error object.
        """
        self._notes.extend(notes)

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            The complete error description
        """
        if self.description is None:
            return ""
        return self.description.format(**self.args)

    def throw(self) -> NoReturn:
        """
        Raises an exception from this error.
        Uses the exception class `exception_cls` defined at the class-level.
        """
        exc = self.exception_cls(self.description)
        for note in self._notes:
            exc.add_note(note)
        raise exc

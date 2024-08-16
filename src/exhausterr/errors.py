"""
Base layer for error types.

@author: Baptiste Pestourie
@date: 16.08.2024
"""

from __future__ import annotations
from typing import (
    Optional,
    NoReturn,
    Iterable,
    Any,
    TypedDict,
    ClassVar,
    Iterator,
)
import itertools

from exhausterr.type_utils import TypedDictDefinition


def order_typed_dict_keys(typed_dict: TypedDictDefinition) -> Iterator[str]:
    """
    Allows ordering the keys of a typed dict in declaration order,
    as __required_keys__ and __optional_keys__ are not ordered.

    Yields
    ------
    str
        Required keys in declaration order, followed by optional keys in declaration order.
        Note that this means that optional keys declared before required one will still
        be put after in this ordering.
    """
    required_keys = typed_dict.__required_keys__

    required_keys_ordered: list[str] = []
    optional_keys_ordered: list[str] = []

    for annotation in typed_dict.__annotations__.keys():
        container = (
            required_keys_ordered
            if annotation in required_keys
            else optional_keys_ordered
        )
        container.append(annotation)

    return itertools.chain(required_keys_ordered, optional_keys_ordered)


class ErrorDeclaration(TypedDict):
    """
    Fields expected from an  error class declaration
    """

    description_header: str
    description_prefix: str
    exception_cls: type[Exception]
    description: property


class _ErrorMeta(type):
    """
    Base metaclass for errors.
    """

    Arguments: Optional[TypedDictDefinition]

    def __new__(mcs, name: str, bases: tuple, namespace: dict[str, Any]) -> _ErrorMeta:
        """
        Builds the match arguments for errors
        """
        error_cls = super().__new__(mcs, name, bases, namespace)

        if "__match_args__" in namespace:
            return error_cls

        error_args = error_cls.Arguments
        extra_match_args = order_typed_dict_keys(error_args) if error_args else ()

        setattr(
            error_cls,
            "__match_args__",
            (
                "description",
                *extra_match_args,
            ),
        )
        return error_cls


class Error(metaclass=_ErrorMeta):
    """
    Base representation for an error.

    Class parameters
    ----------------
    default_description : Optional[str]
        If provided, instances of that class that do not provide a custom description
        will use this instead.
        Note that the default description will not be present at all in the message
        if a custom one is given.
        If you want a message that displayed regardless of what's provided in the instance,
        use description_header instead.

    description_header: str
        Is always prefixed before the error description.

    exception_cls: type[Exception]
        When raising that error as an execption,
        the exception class that will be used.
    """

    default_description: ClassVar[str] = ""
    description_header: ClassVar[str] = ""
    exception_cls: ClassVar[type[Exception]] = Exception
    Arguments: ClassVar[TypedDictDefinition | None] = None

    # match arguments are provided by metaclass
    __match_args__: ClassVar[tuple[str]]

    def __init__(  # pylint: disable=keyword-arg-before-vararg
        self,
        description: Optional[str] = None,
        *args,
        notes: Iterable[str] = (),
        **kwargs,
    ) -> None:
        """
        Error can be built from single description string,
        similar to exceptions

        Parameters
        ----------
        *notes: str
            Relevant messages to describe this error.
            If throwing as exception, note that the
            first one will be used as the exception body,
            while the other one will be used as exception annotations.
        """
        self._description: str = description or self.default_description
        self._notes: list[str] = list(notes)
        self._args: dict = {}
        if self.Arguments:
            self.set_arguments(*args, **kwargs)
        elif args or kwargs:
            raise AttributeError(
                f"{self.__class__.__name__} does not support arguments"
            )

    @property
    def args(self) -> dict[str, Any]:
        """
        Returns
        -------
        dict[str, Any]
            Dict containing the arguments and their current values
        """
        if self.Arguments is None:
            raise AttributeError(
                f"{self.__class__.__name__} does not support arguments"
            )
        return self._args

    def __getattr__(self, __attr: str) -> Any:
        """
        Delegates attribute access to the argument dictionary
        """
        try:
            return self._args[__attr]
        except AttributeError:
            raise AttributeError(  # pylint: disable=raise-missing-from
                f"'{self.__class__.__name__}' object has no attribute '{__attr}",
                " nor is it defined as a valid argument",
            )

    def set_argument(self, name: str, value: str) -> None:
        """
        Delegates attribute access to the argument dictionary
        """
        if name not in self.args:
            raise AttributeError(
                f"{name} is not a valid argument for {self.__class__.__name__}"
            )
        self.args[name] = value

    def set_arguments(self, *args, **kwargs) -> None:
        """
        Set multiple arguments at once.
        Arguments are consumed following the key declaration order
        of the Arguments dict.
        """
        args = self.args
        for arg_name, value in zip(order_typed_dict_keys(self.Arguments), args):
            args[arg_name] = value

        for arg_name, value in kwargs.items():
            args[arg_name] = value

    def add_notes(self, *notes: str):
        """
        Adds a note to give more details on this error object.
        """
        self._notes.extend(notes)

    @property
    def unformatted_description(self) -> str:
        """
        Returns
        -------
        str
            The complete error description
        """
        return self.description_header + self._description

    @property
    def description(self) -> str:
        """
        Returns
        -------
        str
            The complete error description
        """
        return self.unformatted_description.format(**self._args)

    def throw(self) -> NoReturn:
        """
        Raises an exception from this error.
        Named thorxw
        Uses the exception class defined at the class-level.
        """
        exc = self.exception_cls(self.description)
        for note in self._notes:
            exc.add_note(note)
        raise exc

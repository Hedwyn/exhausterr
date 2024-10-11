"""
Type definitions for better type annotations.

@date: 16.08.2024
@author: Baptiste Pestourie
"""

from typing import Protocol, Iterator
import itertools


class TypedDictDefinition(Protocol):
    """
    Patches the absence of public interface metaclass definition
    for TypedDict (_TypedDictMet being private).
    Functions taking a TypedDict definition as argument can simply not
    type properly their arguments.
    """

    __annotations__: dict[str, type]
    __optional_keys__: frozenset[str]
    __required_keys__: frozenset[str]


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
"""
Type definitions for better type annotations.

@date: 16.08.2024
@author: Baptiste Pestourie
"""

from typing import Protocol


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

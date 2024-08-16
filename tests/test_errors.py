"""
Test suite for error module.

@date: 16.08.2024
@author: Baptiste Pestourie
"""

from typing import TypedDict, NotRequired

import pytest
from exhausterr.errors import Error, order_typed_dict_keys


def test_order_typed_dict_keys():
    """
    Checks that TypedDict key ordering returns the correct output when
    only required keys are given.
    """

    class _TypedDictTest(TypedDict):
        a: str
        b: str
        c: str

    # Note: looping multiple times as ordering from TypedDict are random
    for _ in range(10):
        assert list(order_typed_dict_keys(_TypedDictTest)) == ["a", "b", "c"]


def test_order_typed_dict_keys_mixed():
    """
    Checks that TypedDict key ordering returns the correct output when
    oa mix of required and optional keys is given
    """

    class _TypedDictTest(TypedDict):
        a: NotRequired[str]
        b: str
        c: str

    # Note: looping multiple times as ordering from TypedDict are random
    for _ in range(10):
        assert list(order_typed_dict_keys(_TypedDictTest)) == ["b", "c", "a"]


def test_order_typed_dict_keys_inherited():
    """
    Checks that TypedDict key ordering returns the correct output when
    the TypedDict inherits from another one.
    """

    class _BaseDict(TypedDict):
        a: NotRequired[str]
        b: str

    class _ChildDict(_BaseDict):
        c: NotRequired[str]
        d: str

    # Note: looping multiple times as ordering from TypedDict are random
    for _ in range(10):
        assert list(order_typed_dict_keys(_ChildDict)) == ["b", "d", "a", "c"]


class BasicError(Error):
    """
    A basic error that does not introduce any additional
    feature compared to a raw Error
    """

    description_fmt = "A basic error"
    exception_cls = ValueError


def test_error_parent_cls():
    """
    Checks that Error can be instanciated properly
    """
    err = Error()
    assert err.description == ""


def test_error_default_description():
    """
    Checks that description for errors that do not provide a custom
    one is properly formatted.
    """
    err = BasicError()
    assert err.description == "A basic error"


def test_error_throw():
    """
    Checks that Error.throw() raises the correct exception
    """
    err = BasicError()
    with pytest.raises(ValueError):
        err.throw()
    try:
        err.throw()
    except ValueError as e:
        assert str(e) == "A basic error"


@pytest.mark.parametrize("notes", (["note1", "note2"],))
def test_error_notes(notes: list[str]):
    """
    Checks that Error.notes() returns the correct notes
    """
    err = BasicError()
    err.add_notes(*notes)
    for note in notes:
        assert note in err._notes

    try:
        err.throw()
    except ValueError as e:
        for note in notes:
            assert note in e.__notes__


class ErrorWithArgs(Error):
    """
    A basic error that does not introduce any additional
    feature compared to a raw Error
    """

    description_fmt = "a: {a}, b: {b}"
    exception_cls = ValueError

    # Issue: seems that TypedDict, unlike dicts, are not ordered ?
    class Arguments(TypedDict):
        """
        Argument definition for this error
        """

        a: int
        b: float


def test_error_meta_creates_match_args():
    """
    Checks that the matcha rguments are propely formatted
    by the metaclass when defining custom arguments
    """
    assert ErrorWithArgs.__match_args__ == ("a", "b")


def test_error_with_arguments_matching():
    """
    Checks that the match arguments are propely formatted
    by the metaclass when defining custom arguments
    """
    err = ErrorWithArgs(a=1, b=2.0)

    match err:
        case BasicError():
            assert False, "Matched wrongly as BasicError"

        case ErrorWithArgs(a, b):
            assert a == 1
            assert b == 2.0

        case _:
            assert False, "Error did not match"

    # now matching with keyword args
    match err:
        case BasicError():
            assert False, "Matched wrongly as BasicError"

        case ErrorWithArgs(a=a, b=b):
            assert a == 1
            assert b == 2.0

        case _:
            assert False, "Error did not match"


class ErrorWihFormatting(ErrorWithArgs):
    """
    A basic error that does not introduce any additional
    feature compared to a raw Error
    """

    default_description = "defaulted"
    description_header = "{a},{b}:"
    exception_cls = ValueError


def test_error_formatting():
    """
    Checks that errors using string expected format arguments
    are formatted properly
    """
    err = ErrorWihFormatting(a=1, b=2.0)
    assert err.description == ("a: 1, b: 2.0")

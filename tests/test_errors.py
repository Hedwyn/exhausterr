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

    default_description = "defaulted"
    description_header = "BasicError:"
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
    assert err.description == "BasicError:defaulted"


def test_error_custom_description():
    """
    Checks that description for errors that do provide a custom
    one is properly formatted.
    """
    err = BasicError("custom")
    assert err.description == "BasicError:custom"


def test_error_throw():
    """
    Checks that Error.throw() raises the correct exception
    """
    err = BasicError("custom")
    with pytest.raises(ValueError):
        err.throw()
    try:
        err.throw()
    except ValueError as e:
        assert str(e) == "BasicError:custom"


@pytest.mark.parametrize("at_init", (True, False))
@pytest.mark.parametrize("notes", (["note1", "note2"],))
def test_error_notes(at_init: bool, notes: list[str]):
    """
    Checks that Error.notes() returns the correct notes
    """
    if at_init:
        err = BasicError("custom", notes=notes)
    else:
        err = BasicError("custom")
        err.add_notes(*notes)
    for note in notes:
        assert note in err._notes

    try:
        err.throw()
    except ValueError as e:
        for note in notes:
            assert note in e.__notes__


def test_error_match():
    """
    Check that the match statement is captuing the error
    and its description propely
    """
    err = BasicError("custom")

    match err:
        case BasicError(desc):
            assert desc == "BasicError:custom"
        case _:
            assert False, "Error did not match"


class ErrorWithArgs(Error):
    """
    A basic error that does not introduce any additional
    feature compared to a raw Error
    """

    default_description = "defaulted"
    description_header = "BasicError:"
    exception_cls = ValueError

    # Issue: seems that TypedDict, unlike dicts, are not ordered ?
    class Arguments(TypedDict):
        """
        Argument definition for this error
        """

        a: int
        b: float


def test_error_with_arguments_match_args():
    """
    Checks that the matcha rguments are propely formatted
    by the metaclass when defining custom arguments
    """
    assert len(ErrorWithArgs.__match_args__) == 3


def test_error_with_arguments_matching():
    """
    Checks that the match arguments are propely formatted
    by the metaclass when defining custom arguments
    """
    err = ErrorWithArgs(a=1, b=2.0)

    match err:
        case BasicError(_):
            assert False, "Matched wrongly as BasicError"

        case ErrorWithArgs(_, a, b):
            assert a == 1
            assert b == 2.0

        case _:
            assert False, "Error did not match"

    # now matching with keyword args
    match err:
        case BasicError(_):
            assert False, "Matched wrongly as BasicError"

        case ErrorWithArgs(_, a=a, b=b):
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
    assert err.description.startswith("1,2.0")

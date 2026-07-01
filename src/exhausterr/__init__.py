# SPDX-FileCopyrightText: 2024-present Hedwyn <bpestourie@gmail.com>
#
# SPDX-License-Identifier: MIT
from ._builtin import (
    BadAttribute,
    BadKey,
    ZeroDivision,
    safe_divide,
    safe_getattr,
    safe_getitem,
    safe_int_divide,
)
from ._errors import Error
from ._iterators import chain_results, result_mapper, result_reducer, resultify
from ._results import AbstractResult, Err, NoneOr, Ok, Result, err, err_if, is_error

__all__ = [
    "AbstractResult",
    "BadAttribute",
    "BadKey",
    "Err",
    "Error",
    "NoneOr",
    "Ok",
    "Result",
    "ZeroDivision",
    "chain_results",
    "err",
    "err_if",
    "is_error",
    "result_mapper",
    "result_reducer",
    "resultify",
    "safe_divide",
    "safe_getattr",
    "safe_getitem",
    "safe_int_divide",
]

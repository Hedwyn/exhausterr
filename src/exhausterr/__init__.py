# SPDX-FileCopyrightText: 2024-present Hedwyn <bpestourie@gmail.com>
#
# SPDX-License-Identifier: MIT
from ._results import Result, Ok, Err, NoneOr, AbstractResult
from ._errors import Error
from ._iterators import resultify, result_mapper, result_reducer, chain_results
from ._builtin import (
    safe_int_divide,
    safe_divide,
    safe_getattr,
    safe_getitem,
    ZeroDivision,
    BadKey,
    BadAttribute,
)

__all__ = [
    "AbstractResult",
    "Result",
    "Ok",
    "Err",
    "NoneOr",
    "Error",
    "resultify",
    "result_mapper",
    "result_reducer",
    "chain_results",
    "safe_int_divide",
    "safe_divide",
    "safe_getattr",
    "safe_getitem",
    "ZeroDivision",
    "BadKey",
    "BadAttribute",
]

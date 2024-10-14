# SPDX-FileCopyrightText: 2024-present Hedwyn <bpestourie@gmail.com>
#
# SPDX-License-Identifier: MIT
from ._results import Result, Ok, Err, NoneOr, AbstractResult
from ._errors import Error
from ._iterators import resultify, result_mapper

__all__ = [
    "AbstractResult",
    "Result",
    "Ok",
    "Err",
    "NoneOr",
    "Error",
    "resultify",
    "result_mapper",
]

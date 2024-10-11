# SPDX-FileCopyrightText: 2024-present Hedwyn <bpestourie@gmail.com>
#
# SPDX-License-Identifier: MIT
from ._results import Result, Ok, Err, NoneOr, AbstractResult
from ._errors import Error

__all__ = ["AbstractResult", "Result", "Ok", "Err", "NoneOr", "Error"]

from exhausterr import Result, Error
from typing import reveal_type

def check_result(result: Result[int, Error]) -> None:
    """
    Demonstrates that type narrowing is properly performed
    when using `if` statements instead of `match`.
    Running 'if result: ...' will narrow the result to Ok(...)
    wihin `if` scope and to Err(...) in the `else` scope.
    """
    if result:
        # revealed type is Ok[int]
        reveal_type(result)
    else:
        # revealed type is Err[Error]
        reveal_type(result)


print("Note: this example is meant to be run by mypy, not to be executed")

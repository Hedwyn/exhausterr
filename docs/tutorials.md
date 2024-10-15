# Usage

## A simple example
Have a look at the `examples` folder. <br>
If we look at `examples/results.py`:
```python
"""
A naive example on how to use Result and Error
"""

import random
from enum import Enum, auto
from typing import assert_never
from exhausterr import Error
from exhausterr import Result, Ok, Err


class CoinTossResult(Enum):
    HEADS = auto()
    TAILS = auto()


class LandedOnEdge(Error):
    pass


class DownTheGutter(Error):
    pass


def toss_a_coin() -> Result[CoinTossResult, LandedOnEdge | DownTheGutter]:
    """
    Plays heads or tails... with a few twists !
    """
    rng = random.random()
    if rng < 0.1:
        return Err(DownTheGutter())

    if rng < 0.2:
        # jeez, we landed on an edge
        return Err(LandedOnEdge())

    result = CoinTossResult.HEADS if rng < 0.6 else CoinTossResult.TAILS
    return Ok(result)


def play() -> None:
    """
    Tosses a coin and informs the player about the result
    """
    res = toss_a_coin()
    match res:
        case Ok(coin):
            print(
                f"Got {coin.name.lower()}, you {'won' if coin == CoinTossResult.HEADS else 'lost'} !"
            )

        case Err(err):
            # Something went wrong.. but what
            match err:
                case LandedOnEdge():
                    print("You landed on an edge ! Let's flip the coin again.")

                case DownTheGutter():
                    print("Ops, you lost a coin, let's get another one !")

                case _ as unreachable:
                    assert_never(unreachable)

        case _ as unreachable:
            assert_never(unreachable)


for _ in range(100):
    play()

```
The first thing to pay attention is the return type of `toss_a_coin`, which is `Result[CoinTossResult, LandedOnEdge | DownTheGutter]`. If you are familiar with Rust syntax, this should be fairly transparent already. This reads as this function provides a `CoinTossResult` on success, and an error on failure which can be either `LandedOnEdge` or `DownTheGutter`. The `Result` annotation is simply the union of `Ok` and `Err` under the hood, which you can see in action in the function body itself:
```python
def toss_a_coin() -> Result[CoinTossResult, LandedOnEdge | DownTheGutter]:
    """
    Plays heads or tails... with a few twists !
    """
    rng = random.random()
    if rng < 0.1:
        return Err(DownTheGutter())

    if rng < 0.2:
        # jeez, we landed on an edge
        return Err(LandedOnEdge())

    result = CoinTossResult.HEADS if rng < 0.6 else CoinTossResult.TAILS
    return Ok(result)
```
In a nutshell: if your function succeeds, return `Ok(your_return_value)`, otherwise return `Err(the_error_that_occured)`.

Then, callers can examine the result thourgh pattern matching:
```python
def play() -> None:
    """
    Tosses a coin and informs the player about the result
    """
    res = toss_a_coin()
    match res:
        case Ok(coin):
            print(
                f"Got {coin.name.lower()}, you {'won' if coin == CoinTossResult.HEADS else 'lost'} !"
            )

        case Err(err):
            # Something went wrong.. but what
            match err:
                case LandedOnEdge():
                    print("You landed on an edge ! Let's flip the coin again.")

                case DownTheGutter():
                    print("Ops, you lost a coin, let's get another one !")

                case _ as unreachable:
                    assert_never(unreachable)

        case _ as unreachable:
            assert_never(unreachable)
```
At this point, you might want to run mypy on this example (`mypy examples/results.py --strict`). It should not detect any errors:
```console
Success: no issues found in 1 source file
```
You might have noticed the `case _ as unreachable: ...`; this is the idomatic way in Python to check that a path is not reachable, or more precisely here, that a match statement is actually exhaustive. <br>
Try now commenting out the `case DownTheGutter` arm, or the entire `case Err(err)` arm entirely. You should now get errors when type checking:
```
results.py:62: error: Argument 1 to "assert_never" has incompatible type "DownTheGutter"; expected "NoReturn"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```
`mypy` now spots that we are now covering one possible error path - `DownTheGutter`, in that case.
<br><br>
This is obviously a silly example, but this should demonstrate the spirit of exhaustive error handling. Typical error flow with exceptions do not allow this type of static verification on code coverage and exhaustiveness.<br>
Note that you may also use `if / else` logic and still benefit from type narrowing. Running `if result: ...` gives you always True for `Ok` results and always False for `Err`. See the following example (`examples/results_with_if.py`):

```python
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
```

## Standard patterns
There are about three idiomatic patterns you can use with `Result`: `match` statement, `if` / `else` and `unwrap()`. We already covered the pattern matching style above, which as a reminder is as follows:
```python
match my_result:
    case Ok(some_value):
        # ... do something with the value
    
    case Err(an_error):
        # do something with the error
```

Sometimes `match` statements might feel like an overkill. If you do not need the pattern matching (that is, if you only want to know if it's an error or a success and you do not need to match the *inner* value), `if` / `else` is a perfectly acceptable and supports construct (snippet below is taken from `examples/results_with_if.py`):

```python
def check_result(result: Result[int, Error]) -> None:
    if result:
        # revealed type is Ok[int]
        reveal_type(result)
    else:
        # revealed type is Err[Error]
        reveal_type(result)
```
Type narrowing will be performed correctly by your type checker: within the `if` scope, the type of your `Result` will be narrowed to `Ok`, while in the scope of `else` it will be narrowed to `Err`. Thus, you gets the same verifiability benefits as the `match` statement - without the actual pattern matching. This is quite useful for Results that carry a `None` value, or for logic that only considers one of the two cases.<br>
The last construct is `unwrap()`, which in the Rust world means "give the the result or panic". Calling `unwrap()` will give you the inner value for an `Ok` result, and will `throw` (*raise*) the error for `Err` (Note: all errors have a class-defined exception class to use when they're raised). Unlike Rust that panics in case of errors, you program can still recover by catching the exception, but the error will now be hidden from your control flow type-wise. Thus, that's a pattern that you should use with caution; it is however quite useful in the following cases:

* script-like code, that does not require to be polished
* Internal control flows for which you know that the error case has been checked previously due to the execution order.
* In places where you know nothing can handle the error locally anyway and you would rather use standard exception-based propagation (i.e. to convert errors "back" to exception-style).

## Derived patterns
A useful pattern for defaulting is `my_variable = some_result or default_value` - this reads as "give me the result value if `Ok`  or use the if `Err`". This is directly derived from the implementation of `__bool__` in Results, which was also used in the `if` / `else` examples above. `Ok` will always evaluate to `True` in boolean operations, and `Err` to `False`.

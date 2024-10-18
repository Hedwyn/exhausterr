# Differences compared to 'results' library
If are familiar with the great [returns](https://pypi.org/project/returns/) library for Python you might have noticed that the functionality in this package is very similar. This section explains the core differences.

## Size and goals
`exhausterr` is focused on a very narrow domain which is error as values and exhaustive error handling. `returns` on the other hand, is an implementation of common monad patterns that you would find in functional programming languages like Haskell (e.g., IO, Env, Maybe, etc.). As a consequence its scope is significantly wider than this package. If you are willing to integrate common monad patterns in your Python code you should definitely use `returns`, which does it very well and is most likely the most solid Python implementation available currently. The ambition of `exhausterr` is **not** to implement monadic patterns, and there is no plan to integrate monad-like objects other than Results for now.<br>
Now that this is cleared up, the next sections cover the differences when it comes to the functionalities that are actually shared by the two libraries.

## Design philosophy
The main difference between the two packages is, arguably, the design philosophy. The goal of `exhausterr` is to squeeze the full potential out of type checkers, without requiring any custom plugins. This means that whenever possible it will favor static analysis over runtime checks. It is basically aiming to get similar semantic verification from the type checker as Rust or Zig code would get from their respective compilers - when it comes to error handling, obviously. As a consequence, there is a very deliberate choice to **not** add runtime logic for something that can be formally checked at type checking time.<br>
`Results` on in `returns` are one of many monad(-like) objects that supports the general monad *protocol* (think bind / compose). If you do not need about these monad-flavors and is simply want solid error-as-values it gives sightly less assets at type checking time compared to `exhausterr`:

* **Exhaustiveness**: when using the returns' Result, the type checker won't be able to infer that checking both the Ok and Error case (called `Success` and `Failure`) is exhaustive. For example this fails with myp:

```python
from returns.result import Result

def show_result(Result[float, float]) -> None:
    match only_positive(i):
        case Success(x):
            print("Success ! ", x)
        case Failure(y):    
            print("Failure ! ", y)
        case _ as never:
            assert_never(never)
```

* **Type narrowing with if**: returns' Result do not support `__bool__` at all, where as an `exhausterr` will allow you to call `if result` for a success-condition and the type will be narrowed to `Ok` within the scope (and vice-versa). This by extension also prevents stream-lined boolean logic (e.g. `all`, `any` on a bunch of results).

The other big differnece is the definition of errors. Results from returns accept arbitrary types - but the package is mainly designed to work around exceptions as the error type. `exhausterr` on the other hand uses deliberately a base class for errors that is *not* an exception, and does not allow non-errors as the error return of Results.

## Implementation of errors
On top of the `Result` implementation `exhausterr` provides a custom error tyope, which is intended to be clearly differentiated from exceptions. You can still come back and forth between the two worlds (`Error` has an `exception_cls` attribute pointing to the exception type to use and you can `throw` them); however, the error-as-values objects are clearly separted from the exception system. Part of the motivation is to clear any possible confusion on how these objects are supposed to be used; the other part is to avoid creating complex and bloated objects. Exception is a built-in object of Python with special handling, and although it can pretty much be used like any normal class, there something a bit dangerous about adding complex functionalities on top of it, which ends up being kind of an anti-pattern. It might also not evolve well with the current evolution of Python, as the last versions have introduced new advanced exception-related features such as exception groups. As these continue to grow one should not exclude that a custom class on top of exceptions might become conflictual eventually.<br>
`Error` in `exhausterr` are designed for arguments carrying and pattern matching. They support primitives to format them into exceptions and throw them, but there are still isolated in their own space.

## Summary
If you want to get a full package for functional programming experience, and/or are specifically looking for monad patterns, you should use `returns`. If you mainly care about error-as-values, exhaustiveness, and railway programming, `exhausterr` is worth considering, as a more focused and minimal library. It should provide more semantic assets type checking-wise, and has a more formal (and arguably more restrictive) error model.


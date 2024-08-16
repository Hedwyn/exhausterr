# exhausterr: Exhautive Error Handling in Python

A library implementing error as values in Python with exhaustiveness verifiability, type safety and pattern matching. Brings flavors of Zig and Rust error handling to Python towars higher reliability in critical Python programs.<br>
Integrate errors as part of you control flow and leverage the full potential of type checkers to assert code behavior.

-----

**Table of Contents**

- [Installation](#installation)
- [Motivation](#motivation)
- [License](#license)



# Installation
Requires Python>=3.11. Based on hatch as the build system.

```console
pip install exhausterr
```

Or if using hatch frontend:
```
hatch shell
```

# Manifesto

## What does "error as values" mean ?
You might not know it yet, but when programming sometimes shit goes wrong. When writing a function that can fail, one needs a way to inform the function caller that something went wrong. **"Error as values"** simply means that the return value of the function itself will tell whether the call was successful or failed, and was the historical and for a long time only way to deal with errors. In C typically, function that can error typically return an integer encoding either success or an error type, while the actual payload procuced by the function woud typically by passed by giving a pointer to memory location where it should be written.
Exceptions are the main alternative (or complement...as we will discuss later) to error-as-values, and have been popularized by languages like Java. Languages with exception support provide them as a way to interrupt a function early on and navigate backward in the call stack -until finding a caller that knows how to deal with it. From the programmer's perspective, they are usually kept out of the type system, and in a way isolated from the main control flow, which then is kept centered on the *happy path*.

## Why using exceptions ?
Philosophy of exceptions is to simplify the main control flow ('happy path') by isolating (some would dare to say hiding) errors from it. The idea behind is that you only care about errors if you know how to deal wih them, otherwise it's fine to not even know about them. <br>
To achieve that, one key property of exceptions is that it gets implicitly forwarded through
the call stack until it hits something that can deal with it (typically through some `try...catch` syntax, where `catch` allows you to specify what type of error(s) you are able to deal with). <br>
Thus, some of the main difference between error-as-values and exceptions are the following:
* Exceptions will not allow you to delay the error handling. Either you catch and deal with the problem, or your function will be interrupted and the exceptyion will go one step up in the call stack. With error as values, you can go farther in the function body and deal with the error later.
* Exceptions travel *implicitly* through the call stack, while error-as-values have to be explictly forwarded.
* Exceptions are *usually* not integrated in the type system. (Java checked exceptions is one exception - sorry for the pun). Modern languages using aerror-as-values are typically able to integrate errors in the type system, allowing the errors that a given function could produce to be exposed clearly in the type system. 

## The issue with exceptions

Exceptions also have some major drawbacks and are definitely not loved by everyone, leading to some modern languages do not implement them on purpose. In particular:
* In their primary form, they basically break all formal verifiability of programs in typed languages, due to the fact they are out of the type system. Checked exceptions are an attempt to solve that (notably in Java), but they end upm often being the worst of both worlds instead of the best. 
* It's extremly difficult to deal with all possible failure modes in an exhaustive manner,
since the exceptions are inherently hiding the error flow compared to a naïve "return code as error"
C-like approach. The fact that exceptions travel implicitly through the calls makes them very difficult if not impossible to integrate them in a verifiable system..
* They need special mecanisms to handle them in asynchronous contexts. Remember, exceptions by definition do not allow delaying the error handling - while asynchronous code is all about delaying stuff. This introduces further complexity in code coloring, and prevents from dealing with the "good" and "bad" path in a symmetric way in asynchronous contexts. Also, if something like `asyncio` already bundles this type of mecanisms, for concurrent code based on thread this boilerpalte has to be written manually.<br><br>

In real-time, safety critical systems where reliability is extremly critical, exceptions are often counter-productive. Asserting code behaviour is crucial in these contexts,
and exceptions are pretty bad for that, being too opaque. The whole "you don't need to know about errors if you can't deal with it" idea does not scale very well in safety critical systems. The whole concept of being potentially hit by an error coming from a depth-5 callee in the calls stack is also far from being an asset. Errors travelling implictly by more than one call in the stack in a completely opaque way is particularly bad in that context.

Exceptions simplify the business logic as long as the program won't kill anyone if there's a bug - in that latter case, one would usually better pay the price of dealing with errors as part of the control flow- because it's much less bug-prone.
There are reasons for which Rust is considered as one of the most powerful programming language for high-reliability application, and the error handling is one of them.

## So, should one refrain from using exceptions ?
In a language like Python, definitely not. The idiomatic way to deal with errors in Python is to use exceptions - and going against what's idomatic is rarely a good idea.
In the end, whether to use exceptions or error as values is basically a tradeoff between simplified control flow and verifiability. In the context of enteprise software for which Java was and still is extremly popular, errors are typically not life threatening and one might see why exceptions got so popular. In programming contexts where the most of the worload is put toward maximizing robustness and relibaility, they are sort of a footgun.

## Using both: exceptions as a soft panic
The heart of the problem is that errors and exceptions are *not* supposed to be the same. Although some languages made idomatic to use exception for any type of error (Python included !), exceptions are supposed to be for... *exceptional* errors. <br>
Although what should be considered *exceptional* is highly subjective, application-dependant and might evolve other time, there are for sure tons of errors out there that are definitely not exceptional. A user making a typo in a form for example is hardly something that should be deemed *exceptional*. Having this case encoded in the type system makes much easier to verify that the software handles every possible situation exhaustively. <br>
On the other end, it's impossible to deal with every single possible error out there. Typically, a lot of programs would not consider the case of a failure when allocating a memory, even though any memory allocation is susceptible to failure (if memory is full, for example). First, because checking every single memory allocation quickly gets annoying, and also simply if your memory is full there are probably already so many things broken that your program not working is the least of the user's worries.
<br> Think about it: running pretty much anything in Python can technically raise `MemoryError` - yet there's very little you could do about it if it happens. Cluttering the control flow with memory errors would be non sense. This sorts of fall into the `exceptional` category, a type of situation in which you would typically *panic* in a low-level lanugage, i.e. crash early and try to provide some context on what happens. From that regard, one can look at exception as a *soft panic* mecanism. Unlike a true panic, you give a chance to the program to recover it it catches it somewhere, while simplifying your control flow from the type system perspective.<br>

# License

`exhausterr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
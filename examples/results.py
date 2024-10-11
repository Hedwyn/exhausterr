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

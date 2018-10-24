"""FIXME."""

import math

def log_plus(first, second):
    """FIXME: replace with scipy.special.logsumexp ? Test it."""
    if first is None:
        return second
    if second is None:
        return first
    if second > first:
        return second + math.log(1.0 + math.exp(first - second))
    else:
        return first + math.log(1.0 + math.exp(second - first))

def log_minus(first, second):
    """FIXME: replace with scipy.special.logsumexp ? Test it."""
    if first is None:
        raise RuntimeError("log_minus: does not suport None first")
    if second is None:
        return first
    if second >= first:
        raise RuntimeError("log_minus: first has to be bigger than second")
    factor = -math.expm1(second - first)
    if factor <= 0.0:
        raise RuntimeError("log_minus: non-positive number to log")
    else:
        return first + math.log(factor)

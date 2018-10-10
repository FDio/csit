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

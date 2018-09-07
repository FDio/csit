# This is to test approaches on how to make Monte Carlo generator
# focus on region of non-negligible weight.

import math
import random

def log_plus(first, second):
    """FIXME."""
    if first is None:
        return second
    if second is None:
        return first
    if second > first:
        return second + math.log(1.0 + math.exp(first - second))
    else:
        return first + math.log(1.0 + math.exp(second - first))

def f(x, y):
    return 100*((10 - x)**2 + (y - x**2)**2)

def g(x, y):
    return -math.log(1.0 + f(x,y)**2)

sum_1 = 0.0
lim = 0.0
sum_w = None
m2_w = None
while 1:
    x = 200.0 * random.random() - 100.0
    y = 200.0 * random.random() - 100.0
    sum_1 += 1
    sum_w = log_plus(sum_w, g(x,y))
    ls1 = math.log(sum_1)
    if ls1 > lim:
        lim = ls1 + 0.3
        print "sum_1", sum_1, "sum_w", sum_w,
        print "log_avg", sum_w - math.log(sum_1)

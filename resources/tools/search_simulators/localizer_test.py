# This is to test approaches on how to make Monte Carlo generator
# focus on region of non-negligible weight.

import math
from Integrator import integrate_2d

def f(x, y):
    return 100*((10 - x)**2 + (y - x**2)**2)

def g(x, y):
    return -100 * f(x,y)

def value_lweight_f(x, y):
    lw = g(x * 100.0, y * 100.0)
    v = math.exp(lw)
    return v, lw

print repr(integrate_2d(value_lweight_f, 1, 6.0))

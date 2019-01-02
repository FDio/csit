# This is to test approaches on how to make Monte Carlo generator
# focus on region of non-negligible weight.

import math
from Integrator import integrate_nd

def f(x, y):
    return x**2 + y**2
#    return 100*((10 - x)**2 + (y - x**2)**2)

def g(x, y):
#    return -f(x,y)
    return -1000000 * f(x,y)

def value_lweight_f(x, y):
    lw = g(x, y)
#    lw = g(x * 100.0, y * 100.0)
    v = math.exp(lw)
    return v, lw

print repr(integrate_nd(2, value_lweight_f, 1))

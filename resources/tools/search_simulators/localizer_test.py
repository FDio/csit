# This is to test approaches on how to make Monte Carlo generator
# focus on region of non-negligible weight.

import math
import random
from solve import solve

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
lsum_w = None
x_avg = 0.0
y_avg = 0.0
Axx = 0.0
Axy = 0.0
Ayy = 0.0
# Without weight scaling for now.
#best12 = list()
#w_coef = 1.0
while 1:
    # Tracking the fit quadric without affecting generation.
    x = 200.0 * random.random() - 100.0
    y = 200.0 * random.random() - 100.0
    sum_1 += 1.0
    lvalue = g(x,y)
    value = math.exp(lvalue)
    lsw_old = lsum_w
    lsum_w = log_plus(lsw_old, lvalue)
    if lsw_old is None:
        x_avg = x
        y_avg = y
    else:
        rw_old = math.exp(lsw_old - lsum_w)
        rw_new = math.exp(lvalue - lsum_w)
        dx = x - x_avg
        dy = y - y_avg
        x_avg += dx * rw_new
        y_avg += dy * rw_new
        Axx += dx * dx * rw_new
        Axy += dx * dy * rw_new
        Ayy += dy * dy * rw_new
        Axx *= rw_old
        Axy *= rw_old
        Ayy *= rw_old
    ls1 = math.log(sum_1)
    if ls1 > lim:
        lim = ls1 + 0.3
        print "sum_1", sum_1, "lsum_w", lsum_w,
        print "log_avg", lsum_w - math.log(sum_1)
        saw = math.exp(lsum_w)
        print "saw", saw
        print "x_avg", x_avg, "y_avg", y_avg
        print "Axx", Axx, "Axy", Axy, "Ayy", Ayy
        #b = [sawv, sawxv, sawyv, sawxxv, sawxyv, sawyyv]
        #A = [[saw, sawx, sawy, sawxx, sawxy, sawyy],
        #     [sawx, sawxx, sawxy, sawxxx, sawxxy, sawxyy],
        #     [sawy, sawxy, sawyy, sawxxy, sawxyy, sawyyy],
        #     [sawxx, sawxxx, sawxxy, sawxxxx, sawxxxy, sawxxyy],
        #     [sawxy, sawxxy, sawxyy, sawxxxy, sawxxyy, sawxyyy],
        #     [sawyy, sawxyy, sawyyy, sawxxyy, sawxyyy, sawyyyy]]
        #r = solve(A, b)
        #print "[A,B,C,D,E,F]", r
        #b = [-r[1], -r[2]]
        #A = [[2*r[3], r[4]], [r[4], 2*r[5]]]
        #m = solve(A, b)
        #v = (r[0] + r[1] * m[0] + r[2] * m[1] + r[3] * m[0] * m[0]
        #     + r[4] * m[0] * m[1] + r[5] * m[1] * m[1])
        #print "[xm, ym]", m, "v", v

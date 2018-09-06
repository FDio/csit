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
m2_w = None
srwx = 0.0
srwy = 0.0
srwxx = 0.0
srwxy = 0.0
srwyy = 0.0
srwxxx = 0.0
srwxxy = 0.0
srwxyy = 0.0
srwyyy = 0.0
srwxxxx = 0.0
srwxxxy = 0.0
srwxxyy = 0.0
srwxyyy = 0.0
srwyyyy = 0.0
srwv = 0.0
srwxv = 0.0
srwyv = 0.0
srwxxv = 0.0
srwxyv = 0.0
srwyyv = 0.0
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
    xx = x * x
    xy = x * y
    yy = y * y
    if lsw_old is None:
        srwx = x
        srwy = y
        srwxx = xx
        srwxy = xy
        srwyy = yy
        srwxxx = x * xx
        srwxxy = x * xy
        srwxyy = x * yy
        srwyyy = y * yy
        srwxxxx = xx * xx
        srwxxxy = xx * xy
        srwxxyy = xx * yy
        srwxyyy = xy * yy
        srwyyyy = yy * yy
        srwv = value
        srwxv = x * value
        srwyv = y * value
        srwxxv = xx * value
        srwxyv = xy * value
        srwyyv = yy * value
    else:
        o_scale = math.exp(lsw_old - lsum_w)
        srwx *= o_scale
        srwy *= o_scale
        srwxx *= o_scale
        srwxy *= o_scale
        srwyy *= o_scale
        srwxxx *= o_scale
        srwxxy *= o_scale
        srwxyy *= o_scale
        srwyyy *= o_scale
        srwxxxx *= o_scale
        srwxxxy *= o_scale
        srwxxyy *= o_scale
        srwxyyy *= o_scale
        srwyyyy *= o_scale
        srwv *= o_scale
        srwxv *= o_scale
        srwyv *= o_scale
        srwxxv *= o_scale
        srwxyv *= o_scale
        srwyyv *= o_scale
        n_scale = math.exp(lvalue - lsum_w)
        srwx += x * n_scale
        srwy += y * n_scale
        srwxx += xx * n_scale
        srwxy += xy * n_scale
        srwyy += yy * n_scale
        srwxxx += x * xx * n_scale
        srwxxy += x * xy * n_scale
        srwxyy += x * yy * n_scale
        srwyyy += y * yy * n_scale
        srwxxxx += xx * xx * n_scale
        srwxxxy += xx * xy * n_scale
        srwxxyy += xx * yy * n_scale
        srwxyyy += xy * yy * n_scale
        srwyyyy += yy * yy * n_scale
        srwv += value * n_scale
        srwxv += x * value * n_scale
        srwyv += y * value * n_scale
        srwxxv += xx * value * n_scale
        srwxyv += xy * value * n_scale
        srwyyv += yy * value * n_scale

#    best12.append(lvalue)
#    if len(best12) > 12:
#        sort(best12, reverse=True)
#        best12 = best12[:12]
#        w_coef = 100 / (best12[0] - best12[-1])
    ls1 = math.log(sum_1)
    if ls1 > lim:
        lim = ls1 + 0.3
        print "sum_1", sum_1, "lsum_w", lsum_w,
        print "log_avg", lsum_w - math.log(sum_1)
        saw = math.exp(lsum_w)
        sawx = srwx * saw
        sawy = srwy * saw
        sawxx = srwxx * saw
        sawxy = srwxy * saw
        sawyy = srwyy * saw
        sawxxx = srwxxx * saw
        sawxxy = srwxxy * saw
        sawxyy = srwxyy * saw
        sawyyy = srwyyy * saw
        sawxxxx = srwxxxx * saw
        sawxxxy = srwxxxy * saw
        sawxxyy = srwxxyy * saw
        sawxyyy = srwxyyy * saw
        sawyyyy = srwyyyy * saw
        sawv = srwv * saw
        sawxv = srwxv * saw
        sawyv = srwyv * saw
        sawxxv = srwxxv * saw
        sawxyv = srwxyv * saw
        sawyyv = srwyyv * saw
        print "saw", saw
        print "srwx", srwx, "sawx", sawx
        print "srwy", srwy, "sawy", sawy
        print "srwxx", srwxx, "sawxx", sawxx
        print "srwxy", srwxy, "sawxy", sawxy
        print "srwyy", srwyy, "sawyy", sawyy
        print "srwxxx", srwxxx, "sawxxx", sawxxx
        print "srwxxy", srwxxy, "sawxxy", sawxxy
        print "srwxyy", srwxyy, "sawxyy", sawxyy
        print "srwyyy", srwyyy, "sawyyy", sawyyy
        print "srwxxxx", srwxxxx, "sawxxxx", sawxxxx
        print "srwxxxy", srwxxxy, "sawxxxy", sawxxxy
        print "srwxxyy", srwxxyy, "sawxxyy", sawxxyy
        print "srwxyyy", srwxyyy, "sawxyyy", sawxyyy
        print "srwyyyy", srwyyyy, "sawyyyy", sawyyyy
        print "srwv", srwv, "sawv", sawv
        print "srwxv", srwxv, "sawxv", sawxv
        print "srwyv", srwyv, "sawyv", sawyv
        print "srwxxv", srwxxv, "sawxxv", sawxxv
        print "srwxyv", srwxyv, "sawxyv", sawxyv
        print "srwyyv", srwyyv, "sawyyv", sawyyv
        b = [sawv, sawxv, sawyv, sawxxv, sawxyv, sawyyv]
        A = [[saw, sawx, sawy, sawxx, sawxy, sawyy],
             [sawx, sawxx, sawxy, sawxxx, sawxxy, sawxyy],
             [sawy, sawxy, sawyy, sawxxy, sawxyy, sawyyy],
             [sawxx, sawxxx, sawxxy, sawxxxx, sawxxxy, sawxxyy],
             [sawxy, sawxxy, sawxyy, sawxxxy, sawxxyy, sawxyyy],
             [sawyy, sawxyy, sawyyy, sawxxyy, sawxyyy, sawyyyy]]
        r = solve(A, b)
        print "[A,B,C,D,E,F]", r
        b = [-r[1], -r[2]]
        A = [[2*r[3], r[4]], [r[4], 2*r[5]]]
        m = solve(A, b)
        v = (r[0] + r[1] * m[0] + r[2] * m[1] + r[3] * m[0] * m[0]
             + r[4] * m[0] * m[1] + r[5] * m[1] * m[1])
        print "[xm, ym]", m, "v", v

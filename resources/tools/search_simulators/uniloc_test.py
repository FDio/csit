# This is to test approaches on how to make Monte Carlo generator
# focus on region of non-negligible weight.

import math
import random
#from solve import solve
import sys

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
    return -100 * f(x,y)

sum_1 = 0.0
lim = 0.0
lsum_w = None
lsum_rar = None
x_avg = 0.0
y_avg = 0.0
Axx = 0.0
Axy = 0.0
Ayy = 0.0
bias_xa = 0.0
bias_ya = 0.0
bias_Axx = 1.0
bias_Axy = 0.0
bias_Ayy = 1.0
bias_lw = 0.0
half_pi = math.asin(1)
double_pi = 4 * half_pi
scale_factor = 1.0
# Without weight scaling for now.
#best12 = list()
#w_coef = 1.0
while 1:
    # Compute biased values.
    blw = bias_lw - sum_1
    lw = log_plus(lsum_w, blw)
    rw = 0.0 if lsum_w is None else math.exp(lsum_w - lw)
    rb = 0.0 if blw is None else math.exp(blw - lw)
    xa = rw * x_avg + rb * bias_xa
    ya = rw * y_avg + rb * bias_ya
    axx = rw * Axx + rb * bias_Axx
    axy = rw * Axy + rb * bias_Axy
    ayy = rw * Ayy + rb * bias_Ayy
#    print "xa", xa, "ya", ya, "axx", axx, "axy", axy, "ayy", ayy
    c = math.sqrt(ayy)
    b = axy / c
    a = math.sqrt(axx - b * b)
#    print "a", a, "b", b, "c", c
    while 1:
        T = math.tan(half_pi * random.random())
        r = math.sqrt(T)
        phi = double_pi * random.random()
        Y = r * math.sin(phi)
        y = scale_factor * c * Y
        if y >= 100.0 or y <= -100.0:
            continue
        X = r * math.cos(phi)
        x = scale_factor * (a * X + b * Y)
        if x >= 100.0 or x <= -100.0:
            continue
        break
#    print "x", x, "y", y
    lrarity = 0.0  # log_plus(0.0, 2 * math.log(T))
    #rarity = math.exp(lrarity)
    x = 200.0 * random.random() - 100.0
    y = 200.0 * random.random() - 100.0
    sum_1 += 1.0
#    if sum_1 >= 1000:
#        sys.exit(0)
    lsum_rar = log_plus(lsum_rar, lrarity)
    lvalue = g(x,y)
#    print "lvalue", lvalue
    value = math.exp(lvalue)
    corrected_lw = lvalue + lrarity
    lsw_old = lsum_w
    lsum_w = log_plus(lsw_old, corrected_lw)
    if lsw_old is None:
        x_avg = x
        y_avg = y
    else:
        rw_old = math.exp(lsw_old - lsum_w)
        rw_new = math.exp(corrected_lw - lsum_w)
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
        print "sum_1", sum_1, "lsum_w", lsum_w, "lsum_rar", lsum_rar
        print "log_avg", lsum_w - lsum_rar
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

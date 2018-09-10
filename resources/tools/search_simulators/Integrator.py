"""FIXME."""

import math
import random
import time

from .log_plus import log_plus


Integrator__HALF_PI = math.asin(1)
Integrator__DOUBLE_PI = 4 * Integrator__HALF_PI


def integrate_2d(value_lweight_f, duration=1.0, scale_factor=20.0):
    """FIXME."""

    sum_1 = 0.0
    lsum_w = None
    x_avg = 0.0
    y_avg = 0.0
    v_avg = 0.0
    v_lrm2 = None
    Axx = 0.0
    Axy = 0.0
    Ayy = 0.0
    bias_xa = 0.0
    bias_ya = 0.0
    bias_Axx = 1.0
    bias_Axy = 0.0
    bias_Ayy = 1.0
    bias_lw = 0.0
    time_stop = time.time() + duration
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
            T = math.tan(Integrator__HALF_PI * random.random())
            r = math.sqrt(T)
            phi = Integrator__DOUBLE_PI * random.random()
            Y = r * math.sin(phi)
            y = ya + scale_factor * c * Y
            if y >= 1.0 or y <= -1.0:
                continue
            X = r * math.cos(phi)
            x = xa + scale_factor * (a * X + b * Y)
            if x >= 1.0 or x <= -1.0:
                continue
            break
    #    print "x", x, "y", y
        lrarity = log_plus(0.0, 2 * math.log(T))
        sum_1 += 1.0
        value, lweight = value_lweight_f(x, y)
        lsw_old = lsum_w
        lsum_w = log_plus(lsw_old, lweight)
        if lsw_old is None:
            x_avg = x
            y_avg = y
            v_avg = value
        else:
            rw_old = math.exp(lsw_old - lsum_w)
            rw_new = math.exp(lweight - lsum_w)
            dx = x - x_avg
            dy = y - y_avg
            dv = value - v_avg
            x_avg += dx * rw_new
            y_avg += dy * rw_new
            v_avg += dv * rw_new
            Axx += dx * dx * rw_new
            Axy += dx * dy * rw_new
            Ayy += dy * dy * rw_new
            Axx *= rw_old
            Axy *= rw_old
            Ayy *= rw_old
            ad = abs(dv)
            if ad > 0.0:
                v_lrm2 = log_plus(v_lrm2, 2 * math.log(ad) + lweight - lsum_w)
            v_lrm2 += lsw_old - lsum_w
        if time.time() >= time_stop:
            stdev = math.exp(v_lrm2 / 2.0)
            return v_avg, stdev

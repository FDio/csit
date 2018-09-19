"""FIXME."""

import copy
import math
import random
import time

import numpy

from log_plus import log_plus


Integrator__HALF_PI = math.asin(1)
Integrator__DOUBLE_PI = 4 * Integrator__HALF_PI

def integrate_nd(n, value_lweight_f, duration=1.0, scale_coeff=10.0):
    """FIXME."""

    len_top = (n + 1) * n
    top = list()
    sum_1 = 0.0
    lsum_w = None
    x_avg = [0.0 for first in range(n)]
    v_avg = 0.0
    v_lrm2 = None
    # TODO: Examine whether we can gain speed by tracking triangle only.
    A = [[0.0 for first in range(n)] for second in range(n)]
    bias_xa = [0.0  for first in range(n)]
    bias_A = [[1.0 if first == second else 0.0 for first in range(n)]
              for second in range(n)]
    time_stop = time.time() + duration
    while 1:
        # Compute biased values.
        if len(top) < len_top:
            a = copy.deepcopy(bias_A)
            xa = list(x_avg)
        else:
            bias_lw = top[0][0]
            lw = log_plus(lsum_w, bias_lw)
            rb = math.exp(bias_lw - lw)
            rw = math.exp(lsum_w - lw)
#            print "bias_lw", bias_lw, "lsum_w", lsum_w, "rb", rb, "rw", rw
            xa = [rw * x_avg[first] + rb * bias_xa[first]  for first in range(n)]
            a = [[(rw * A[first][second] + rb * bias_A[first][second]) * scale_coeff
                  for first in range(n)] for second in range(n)]
        while 1:
            x = numpy.random.multivariate_normal(xa, a, 1)[0]
            for first in range(n):
                xf = x[first]
                if xf <= -1.0 or xf >= 1.0:
                    break
            else:  # These two breaks implement "level two continue".
                break
#        print "DEBUG x", repr(x)
        dx = [x[first] - xa[first] for first in range(n)]
        dy = numpy.linalg.solve(a, dx)
        vdot = numpy.vdot(dx, dy)
        lrarity = vdot / 2.0 * scale_coeff
#        print "lrarity", lrarity
        sum_1 += 1.0
        value, lweight = value_lweight_f(*x)
#        print "value", value, "lweight", lweight
        if len(top) < len_top:
            top.append((lweight, x))
        # Hack: top[-1] is either smallest, or just appended to len_top-1 item list.
        if len(top) >= len_top and lweight >= top[-1][0]:
            top = top[:-1]
            top.append((lweight, x))
            top.sort(key=lambda item: -item[0])
#            print "DEBUG top", repr(top)
            # top has changed, recompute biases
            bias_xa = top[0][1]
            bias_A = [[0.0 for first in range(n)] for second in range(n)]
            bias_lsw = 0.0
            for vv, xx in top[1:]:
                lsw_old = bias_lsw
                bias_lsw = log_plus(lsw_old, 0.0)
                rw_old = math.exp(lsw_old - bias_lsw)
                rw_new = math.exp(0.0 - bias_lsw)
                dx = [xx[first] - bias_xa[first] for first in range(n)]
                # Do not move center from biggest point
                for second in range(n):
                    for first in range(n):
                        bias_A[first][second] += dx[first] * dx[second] * rw_new
                        bias_A[first][second] *= rw_old
        lsw_old = lsum_w
        lsum_w = log_plus(lsw_old, lweight)
#        print "new lsum_w", lsum_w
        if lsw_old is None:
            x_avg = list(x)
            v_avg = value
        else:
            rw_old = math.exp(lsw_old - lsum_w)
            rw_new = math.exp(lweight - lsum_w)
            dx = [x[first] - x_avg[first] for first in range(n)]
            dv = value - v_avg
            for first in range(n):
                x_avg[first] += dx[first] * rw_new
            v_avg += dv * rw_new
            for second in range(n):
                for first in range(n):
                    A[first][second] += dx[first] * dx[second] * rw_new
                    A[first][second] *= rw_old
            ad = abs(dv)
            if ad > 0.0:
                v_lrm2 = log_plus(v_lrm2, 2 * math.log(ad) + lweight - lsum_w)
            if v_lrm2 is not None:
                v_lrm2 += lsw_old - lsum_w
        if time.time() >= time_stop:
            stdev = math.exp(v_lrm2 / 2.0)
#            print "Integrated v_avg", v_avg, "stdev", stdev
            print "DEBUG integrator used", sum_1, "samples"
            print "DEBUG x_avg", repr(x_avg)
            return v_avg, stdev

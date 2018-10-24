"""FIXME."""

import copy
import logging
import math
import random
import time

import numpy

from log_plus import log_plus


Integrator__HALF_PI = math.acos(0)
Integrator__DOUBLE_PI = 4 * Integrator__HALF_PI

def integrate_nd(control_q, result_q, scale_coeff=10.0):
    """FIXME."""

    n, value_lweight_f, bias_xa, bias_A = control_q.get()
    len_top = (n + 2) * (n + 1) / 2
    top = list()
    sum_1 = 0.0
    lsum_w = None
    lcsum_w = None
    lcsum_wc = None
    x_avg = [0.0 for first in range(n)]
    v_avg = 0.0
    v_lrm2 = None
    lcw_best = None
    v_lrm2c = None
    # TODO: Examine whether we can gain speed by tracking triangle only.
    A = [[0.0 for first in range(n)] for second in range(n)]
    if not (bias_xa and bias_A):
        bias_xa = [0.0  for first in range(n)]
        bias_A = [[1.0 if first == second else 0.0 for first in range(n)]
                  for second in range(n)]
    while control_q.empty():
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
#        print "xa", repr(xa), "a", repr(a)
        while 1:
            x = numpy.random.multivariate_normal(xa, a, 1)[0]
            for first in range(n):
                xf = x[first]
                if xf <= -1.0 or xf >= 1.0:
                    break
            else:  # These two breaks implement "level two continue".
                break
#        print "DEBUG x", repr(x)
        sum_1 += 1.0
        dx = [x[first] - xa[first] for first in range(n)]
        dy = numpy.linalg.solve(a, dx)
        vdot = numpy.vdot(dx, dy)
        lrarity = vdot / 2.0
#        print "lrarity", lrarity, "sum_1", sum_1
        value, lweight = value_lweight_f(*x)
#        print "value", value, "lweight", lweight
        if len(top) < len_top:
            top.append((lweight, x))
        # Hack: top[-1] is either smallest, or just appended to len_top-1 item list.
        if len(top) >= len_top and lweight >= top[-1][0]:
#            if n == 2 and lweight > top[0][0]:
#                srA = numpy.linalg.cholesky(bias_A)
#                z = numpy.linalg.solve(srA, dx)
#                angle = math.atan2(z[0], z[1])
#                print "New best, angle", angle
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
#            print "bias_xa", repr(bias_xa), "bias_A", repr(bias_A)
        lcweight = lweight + lrarity
#        print "lcweight", lcweight
        lcsw_old = lcsum_w
        lcsum_w = log_plus(lcsw_old, lcweight)
        lsum_w = log_plus(lsum_w, lweight)
#        print "new lsum_w", lsum_w, "lcsum_w", lcsum_w
        if lcsw_old is None:
            x_avg = list(x)
            v_avg = value
        else:
            rw_old = math.exp(lcsw_old - lcsum_w)
            rw_new = math.exp(lcweight - lcsum_w)
            dx = [x[first] - x_avg[first] for first in range(n)]
            dv = value - v_avg
            for first in range(n):
                x_avg[first] += dx[first] * rw_new
            v_avg += dv * rw_new
            for second in range(n):
                for first in range(n):
                    A[first][second] += dx[first] * dx[second] * rw_new
                    A[first][second] *= rw_old
#            print "x_avg", repr(x_avg), "A", repr(A)
            ad = abs(dv)
            update_c = True
            if lcw_best is None or lcweight > lcw_best:
                lcw_best = lcweight
                v_lrm2c = v_lrm2
                lcsum_wc = lcsw_old
                update_c = False
            if ad > 0.0:
                v_lrm2 = log_plus(v_lrm2, 2 * math.log(ad) + lcweight - lcsum_w)
                if update_c:
                    lcsw_oldc = lcsum_wc
                    lcsum_wc = log_plus(lcsw_oldc, lcweight)
                    v_lrm2c = log_plus(v_lrm2c, 2 * math.log(ad) + lcweight - lcsum_wc)
                    if v_lrm2c is not None:
                        v_lrm2c += lcsw_oldc - lcsum_wc
            if v_lrm2 is not None:
                v_lrm2 += lcsw_old - lcsum_w
    logging.debug("integrator used " + str(sum_1) + " samples")
    logging.debug(
        "v_avg " + str(v_avg) + " x_avg " + repr(x_avg) + " A " + repr(A)
        + " v_lrm2 " + str(v_lrm2) + " v_lrm2c " + str(v_lrm2c))
    stdev = math.exp((2 * v_lrm2 - v_lrm2c) / 2.0)
    logging.debug("top[0] " + repr(top[0]))
    # Intentionally returning xa,a instead of hyper-focused bias.
    result_q.put((v_avg, stdev, xa, a))
    return True

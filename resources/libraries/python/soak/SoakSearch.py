# Copyright (c) 2018 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import Queue
import logging
import math
import random
from scipy.special import erfcx, erfc
import time
import threading

import Integrator
from log_plus import log_plus, log_minus


class SoakSearch(object):
    """FIXME."""

    xerfcx_limit = math.pow(math.acos(0), -0.5)
    log_xerfcx_10 = math.log(xerfcx_limit - math.exp(10) * erfcx(math.exp(10)))

    def __init__(self, measurer, tdpt, lps_target, initial_count=0, timeout=60.0):
        """Store rate measurer and additional parameters."""
        self.measurer = measurer
        """The measurer to use when searching."""
        self.tdpt = tdpt
        """Trial measurement will be performed at this times trial number."""
        self.lps_target = lps_target
        """Target average number of lost packets per second."""
        self.initial_count = initial_count
        """FIXME."""
        self.timeout = timeout
        """FIXME."""

    def search(self, min_rate, max_rate):
        """FIXME."""
        min_rate = float(min_rate)
        max_rate = float(max_rate)
        stop_time = time.time() + self.timeout
        transmit_rate = max_rate
        trial_result_list = list()
        trial_count = self.initial_count
#        mrm = None  # Most Relevant Measurement.
#        mrm_le = None  # MRM loss excess.
#        zeros = 0
        integrator_data = (None, None, None, None)
        log_msg = "Trial {count} computed avg {avg} stdev {stdev}"
        log_msg += " stretch {a1} erf {a2} difference {d}"
        while 1:
            trial_count += 1
            trial_duration = trial_count * self.tdpt
            # TODO: Do the calculations concurrently.
            results = self.measure_and_compute(
                trial_duration, transmit_rate, trial_result_list, max_rate,
                integrator_data)
            measurement, average, stdev, avg1, avg2, integrator_data = results
            logging.info(log_msg.format(
                count=trial_count, avg=average, stdev=stdev,
                a1=avg1, a2=avg2, d=avg2-avg1))
            if stop_time <= time.time():
                return average, stdev
#            if (trial_count - self.initial_count) > 2:
            trial_result_list.append(measurement)
#            if (trial_count - self.initial_count) % 4 == 0:
#                trial_result_list.sort(key=lambda result: result.target_tr)
#                trial_result_list = trial_result_list[:-1]
#            le = measurement.loss_rate - self.lps_target
#            if le > 0.0:
#                #if mrm is None or mrm_le > le:
#                mrm = measurement
#                mrm_le = le
            if (trial_count - self.initial_count) <= 3:
                average = measurement.receive_rate + self.lps_target
#            elif measurement.loss_count == 0 and mrm is not None:
#                zeros += 1
#                if zeros % 2 == 0:
#                    average = max(average, mrm.target_tr - mrm_le)
            else:
                average = avg1 if trial_count % 2 else avg2
            transmit_rate = min(max_rate, max(min_rate, average))

    @staticmethod
    def lfit_stretch(load, mrr, a):
        """FIXME."""
        x = (load - mrr) / a
#        print "load", load, "mrr", mrr, "a", a, "x", x
        if x > 0:
            loga = math.log(
                load - mrr + (log_plus(0, -x) - log_plus(0, -mrr / a)) * a)
#            print "big loss loga", loga
        else:
            sa = (math.exp(x) - math.exp(2 * x) / 2) * a
            if sa == 0.0:
                loga = x
#                print "small loss crude loga", loga
                return loga
            third = math.exp(3 * x) / 3 * a
            if sa + third != sa + 2 * third:
                loga = math.log((log_plus(0, x) - log_plus(0, -mrr / a)) * a)
#                print "small loss direct loga", loga
            else:
                loga = math.log(
                    sa - (math.exp(-mrr / a) - math.exp(-2 * mrr / a)) * a)
#                print "small loss approx loga", loga
        return loga

    @staticmethod
    def lfit_erf(load, mrr, a):
        """FIXME."""
        x = (mrr - load) / a
        x0 = mrr / a
#        print "load", load, "mrr", mrr, "a", a, "x", x, "x0", x0
        if x >= -1.0:
#            print "positive, b ~> m"
            if x > math.exp(10):
                first = SoakSearch.log_xerfcx_10 + 2 * (math.log(x) - 10)
#                print "approximated"
            else:
                first = math.log(SoakSearch.xerfcx_limit - x * erfcx(x))
#                print "exact"
            first -= x * x
            second = math.log(SoakSearch.xerfcx_limit - x * erfcx(x0))
            second -= x0 * x0
            intermediate = log_minus(first, second)
#            print "first", first, "second", second, "intermediate", intermediate
        else:
#            print "negative, b ~< m"
            exp_first = SoakSearch.xerfcx_limit + x * erfcx(-x)
            exp_first *= math.exp(-x * x)
            exp_first -= 2 * x
            second = math.log(SoakSearch.xerfcx_limit - x * erfcx(x0))
            second -= x0 * x0
            intermediate = math.log(exp_first - math.exp(second))
#            print "exp_first", exp_first, "second", second, "intermediate", intermediate
        result = intermediate + math.log(a) - math.log(erfc(-x0))
#        print "lfit result", result
        return result

    @staticmethod
    def find_critical_rate(lfit, llps, *args, **kwargs):
        """FIXME."""
        rate = 10000000.0
        log_loss = lfit(rate, *args, **kwargs)
        if log_loss == llps:
            return rate
        if log_loss > llps:
            rate_hi = rate
            while 1:
                rate_lo = rate_hi / 2.0
                log_loss = lfit(rate_lo, *args, **kwargs)
                if log_loss > llps:
                    rate_hi = rate_lo
                    continue
                if log_loss == llps:
                    return rate_lo
                break
        else:
            rate_lo = rate
            while 1:
                rate_hi = rate_lo * 2.0
                log_loss = lfit(rate_hi, *args, **kwargs)
                if log_loss < llps:
                    rate_lo = rate_hi
                    continue
                if log_loss == llps:
                    return rate_hi
                break
        while rate_hi != rate_lo:
            rate = (rate_hi + rate_lo) / 2.0
            log_loss = lfit(rate, *args, **kwargs)
            if rate == rate_hi or rate == rate_lo or log_loss == llps:
#                print "found", rate
                return rate
            if log_loss > llps:
                rate_hi = rate
            else:
                rate_lo = rate

    @staticmethod
    def lprob(lfit, trial_result_list, *args, **kwargs):
        """FIXME."""
        log_weight = 0.0
        for result in trial_result_list:
#            print "DEBUG for tr", result.target_tr, "lc", result.loss_count, "d", result.duration
            lalps = lfit(result.target_tr, *args, **kwargs)
            lalpt = lalps + math.log(result.duration)
            log_p = result.loss_count * lalpt - math.exp(lalpt)
            log_p -= math.lgamma(1 + result.loss_count)
            c_log_p = log_p  # * math.pow(1.0 + result.loss_count, -1.0/2)
            log_weight += c_log_p
#            print "lalps", lalps
#            print "lalpt", lalpt
#            print "alpt", math.exp(lalpt)
#            print "log_p", log_p
#            print "c_log_p", c_log_p
#            print "log_weight", log_weight
#        print "returning log_weight", log_weight
        return log_weight

    def measure_and_compute(
            self, trial_duration, transmit_rate,
            trial_result_list, max_rate, integrator_data):
        """FIXME."""
        # TODO: Implement safe rate limit.
        n = 2
        b_avg_1, b_avg_2, b_a_1, b_a_2 = integrator_data
        def generate_function(lfit):
            """FIXME."""
            def value_lweight_f(*x):
                """FIXME."""
                X = [(x[first] + 1.0) / 2.0 for first in range(n)]
                mrr = 1.0 + max_rate * math.tan(
                    X[0] * Integrator.Integrator__HALF_PI)
                a = math.exp(X[1] * math.log(mrr))
#                   print "mrr", mrr, "a", a
                lweight = self.lprob(lfit, trial_result_list, mrr, a)
                value = math.log(self.find_critical_rate(
                    lfit, math.log(self.lps_target), mrr, a))
                return value, lweight
            return value_lweight_f
        random.seed(0)
        stretch_control_q = Queue.Queue(1)
        erf_control_q = Queue.Queue(1)
        stretch_result_q = Queue.Queue(1)
        erf_result_q = Queue.Queue(1)
        stretch_worker = threading.Thread(
            target=Integrator.integrate_nd, args=(
                stretch_control_q, stretch_result_q))
        erf_worker = threading.Thread(
            target=Integrator.integrate_nd, args=(
                erf_control_q, erf_result_q))
        stretch_worker.setDaemon(True)
        erf_worker.setDaemon(True)
        stretch_worker.start()
        erf_worker.start()
        stretch_control_q.put(
            (n, generate_function(self.lfit_stretch), b_avg_1, b_a_1))
        erf_control_q.put(
            (n, generate_function(self.lfit_erf), b_avg_2, b_a_2))
        measurement = self.measurer.measure(trial_duration, transmit_rate)
        stretch_control_q.put(None)
        erf_control_q.put(None)
        avg1, stdev1, b_avg_1, b_a_1 = stretch_result_q.get(True, 1.0)
        avg2, stdev2, b_avg_2, b_a_2 = erf_result_q.get(True, 1.0)
        avg = math.exp((avg1 + avg2) / 2.0)
        var = (stdev1 * stdev1 + stdev2 * stdev2) / 2.0
        var += (avg1 - avg2) * (avg1 - avg2) / 4.0
        stdev = avg * math.sqrt(var)
        integrator_data = b_avg_1, b_avg_2, b_a_1, b_a_2
        return measurement, avg, stdev, math.exp(avg1), math.exp(avg2), integrator_data

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

import logging
import math
import random
from scipy.special import erfcx, erfc
import time

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
        stdev_mult = 0.0
        stop_time = time.time() + self.timeout
        transmit_rate = max_rate
        trial_result_list = list()
        trial_count = self.initial_count
        mrm = None  # Most Relevant Measurement.
        mrm_le = None  # MRM loss excess.
        zeros = 0
        while 1:
            trial_count += 1
            trial_duration = trial_count * self.tdpt
            # TODO: Do the calculations concurrently.
            average, stdev = self.compute(
                trial_result_list, max_rate, trial_duration)
            logging.info("Trial {count} got avg {avg} stdev {stdev}".format(
                count=trial_count, avg=average, stdev=stdev))
            measurement = self.measurer.measure(
                trial_duration, transmit_rate)
            if stop_time <= time.time():
                return
            trial_result_list.append(measurement)
#            if (trial_count - self.initial_count) % 4 == 0:
#                trial_result_list.sort(key=lambda result: result.target_tr)
#                trial_result_list = trial_result_list[:-1]
            le = measurement.loss_rate - self.lps_target
            if le > 0.0:
                #if mrm is None or mrm_le > le:
                mrm = measurement
                mrm_le = le
            average += stdev_mult * stdev
            if (trial_count - self.initial_count) <= 2:
                average = measurement.receive_rate + self.lps_target
#            elif measurement.loss_count == 0 and mrm is not None:
#                zeros += 1
#                if zeros % 2 == 0:
#                    average = max(average, mrm.target_tr - mrm_le)
            else:
                zeros = 0
            transmit_rate = min(max_rate, max(min_rate, average))

    @staticmethod
    def lfit(load, mrr, a):
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
    def find_critical_rate(llps, *args, **kwargs):
        """FIXME."""
        rate = 10000000.0
        log_loss = SoakSearch.lfit(rate, *args, **kwargs)
        if log_loss == llps:
            return rate
        if log_loss > llps:
            rate_hi = rate
            while 1:
                rate_lo = rate_hi / 2.0
                log_loss = SoakSearch.lfit(rate_lo, *args, **kwargs)
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
                log_loss = SoakSearch.lfit(rate_hi, *args, **kwargs)
                if log_loss < llps:
                    rate_lo = rate_hi
                    continue
                if log_loss == llps:
                    return rate_hi
                break
        while rate_hi != rate_lo:
            rate = (rate_hi + rate_lo) / 2.0
            log_loss = SoakSearch.lfit(rate, *args, **kwargs)
            if rate == rate_hi or rate == rate_lo or log_loss == llps:
#                print "found", rate
                return rate
            if log_loss > llps:
                rate_hi = rate
            else:
                rate_lo = rate

    def lprob(self, trial_result_list, *args, **kwargs):
        """FIXME."""
        log_weight = 0.0
        for result in trial_result_list:
#            print "DEBUG for tr", result.target_tr, "lc", result.loss_count, "d", result.duration
            lalps = self.lfit(result.target_tr, *args, **kwargs)
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

    def compute(self, trial_result_list, max_rate, trial_duration):
        """FIXME."""
        # TODO: Implement safe rate limit.
        duration = 0.5 + trial_duration
        n = 2
        def value_lweight_f(*x):
            """FIXME."""
            X = [(x[first] + 1.0) / 2.0 for first in range(n)]
            mrr = 1.0 + max_rate * math.tan(X[0] * Integrator.Integrator__HALF_PI)
            a = math.exp(X[1] * math.log(mrr))
#            print "mrr", mrr, "a", a
            lweight = self.lprob(trial_result_list, mrr, a)
            value = math.log(self.find_critical_rate(
                math.log(self.lps_target), mrr, a))
            return value, lweight
        random.seed(0)
        avg, stdev = Integrator.integrate_nd(n, value_lweight_f, duration)
        avg = math.exp(avg)
        stdev *= avg
        return avg, stdev

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
import time

import Integrator
from log_plus import log_plus


class SoakSearch(object):
    """FIXME."""

    def __init__(self, measurer, tdpt, lps_target, timeout):
        """Store rate measurer and additional parameters."""
        self.measurer = measurer
        """The measurer to use when searching."""
        self.tdpt = tdpt
        """Trial measurement will be performed at this times trial number."""
        self.lps_target = lps_target
        """Target average number of lost packets per second."""
        self.timeout = timeout
        """FIXME."""

    def search(self, min_rate, max_rate):
        min_rate = float(min_rate)
        max_rate = float(max_rate)
        """FIXME."""
        stop_time = time.time() + self.timeout
        transmit_rate = max_rate
        trial_result_list = list()
        trial_count = 0
        mrm = None  # Most Relevant Measurement.
        mrm_le = None  # MRM loss excess.
        while 1:
            trial_count += 1
            trial_duration = trial_count * self.tdpt
            # TODO: Do the calculations concurrently.
            laverage, lstdev = self.compute(
                trial_result_list, max_rate, trial_duration)
            average = math.exp(laverage)
            stdev = average * lstdev
            logging.info("Trial {count} got avg {avg} stdev {stdev}".format(
                count=trial_count, avg=average, stdev=stdev))
            measurement = self.measurer.measure(
                trial_duration, transmit_rate)
            if stop_time <= time.time():
                return
            trial_result_list.append(measurement)
#            if trial_count % 4 == 0:
#                trial_result_list.sort(key=lambda result: result.target_tr)
#                trial_result_list = trial_result_list[:-1]
            le = measurement.loss_rate - self.lps_target
            if le > 0.0:
                #if mrm is None or mrm_le > le:
                mrm = measurement
                mrm_le = le
            if measurement.loss_count == 0 and mrm is not None:
                average = max(average, mrm.target_tr - mrm_le)
            else:
                average += 1 * stdev
            transmit_rate = min(max_rate, max(min_rate, average))

    @staticmethod
    def lfit(load, mrr, a):
        """FIXME."""
        x = (load - mrr) * a
#        print "load", load, "mrr", mrr, "a", a, "x", x
        if x > 0:
            loga = math.log(
                load - mrr + (log_plus(0, -x) - log_plus(0, -mrr * a)) / a)
#            print "big loss loga", loga
        else:
            sa = (math.exp(x) - math.exp(2 * x) / 2) / a
            if sa == 0.0:
                loga = x
#                print "small loss crude loga", loga
                return loga
            third = math.exp(3 * x) / 3 / a
            if sa + third != sa + 2 * third:
                loga = math.log((log_plus(0, x) - log_plus(0, -mrr * a)) / a)
#                print "small loss direct loga", loga
            else:
                loga = math.log(
                    sa - (math.exp(-mrr * a) - math.exp(-2 * mrr * a)) / a)
#                print "small loss approx loga", loga
        return loga

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
            log_weight += log_p  # * math.exp(result.lsup)
#            print "lalps", lalps
#            print "lalpt", lalpt
#            print "alpt", math.exp(lalpt)
#            print "log_p", log_p
#            print "log_weight", log_weight
#        print "log_weight", log_weight
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
            a = 1.0 / (1.0 + mrr * (X[1] ** 4))
#            print "mrr", mrr, "a", a
            lweight = self.lprob(trial_result_list, mrr, a)
            value = math.log(self.find_critical_rate(
                math.log(self.lps_target), mrr, a))
            return value, lweight
        avg, stdev = Integrator.integrate_nd(n, value_lweight_f, duration)
        return avg, stdev

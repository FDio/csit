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

import Integrator
from log_plus import log_plus

import math
import random
import scipy
import time


class SoakSearch(object):
    """FIXME."""

    def __init__(self, measurer, trial_duration, lps_target, rel_width):
        """Store rate measurer and additional parameters."""
        self.measurer = measurer
        """The measurer to use when searching."""
        self.trial_duration = trial_duration
        """Each trial measurement will be performed at this duration."""
        self.lps_target = lps_target
        """Target average number of lost packets per second."""
        self.rel_width = rel_width
        """FIXME."""

    def search(self, min_rate, max_rate):
        """FIXME."""
        transmit_rate = max_rate / 2.0
        #rate_distance = max_rate / 2.0
        trial_result_list = list()
        while 1:
            # TODO: Do the calculations concurrently.
            measurement = self.measurer.measure(
                self.trial_duration, transmit_rate)
            average, stdev = self.compute(trial_result_list, max_rate)
            if ((average - stdev >= max_rate)
                or (average + stdev <= min_rate)
                or (stdev / average <= self.rel_width)):
                return average, stdev
            trial_result_list.append(measurement)
#            transmit_rate = min(max_rate, max(min_rate, average))
            transmit_rate = average
            #rate_distance = stdev

    @staticmethod
    def lfit(mrr, koeff, load):
        """FIXME."""
#        print "fitting mrr", mrr, "koeff", koeff, "load", load
        log_lpsa = math.log(load) - mrr / load
        log_lpsa -= mrr * mrr * koeff / 2.0 / load / load
#        print "log of fitted loss average", log_lpsa
        return log_lpsa

    @staticmethod
    def find_critical_rate(mrr, koeff, llps):
        """FIXME."""
#        print "finding for mrr", mrr, "koeff", koeff, "llps", llps
        rate = mrr
        log_loss = SoakSearch.lfit(mrr, koeff, rate)
        if log_loss == llps:
            return rate
        if log_loss > llps:
            rate_hi = rate
            while 1:
                rate_lo = rate_hi / 2.0
                log_loss = SoakSearch.lfit(mrr, koeff, rate_lo)
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
                log_loss = SoakSearch.lfit(mrr, koeff, rate_hi)
                if log_loss < llps:
                    rate_lo = rate_hi
                    continue
                if log_loss == llps:
                    return rate_hi
                break
        while rate_hi != rate_lo:
            rate = (rate_hi + rate_lo) / 2.0
            log_loss = SoakSearch.lfit(mrr, koeff, rate)
            if rate == rate_hi or rate == rate_lo or log_loss == llps:
#                print "found", rate
                return rate
            if log_loss > llps:
                rate_hi = rate
            else:
                rate_lo = rate

    def lprob(self, mrr, koeff, trial_result_list):
        """FIXME."""
        log_weight = 0.0
        for result in trial_result_list:
            lalps = self.lfit(mrr, koeff, result.target_tr)
            lalpt = lalps + math.log(self.trial_duration)
#            print "DEBUG lalpt", lalpt
            log_p = result.loss_count * lalpt - math.exp(lalpt)
            log_p -= math.lgamma(1 + result.loss_count)
            log_weight += log_p
#            if debug:
#                print "DEBUG for tr", result.target_tr, "lc", result.loss_count
#                print "alps", alps
#                print "alpt", alpt
#                print "log_p", log_p
#                print "log_weight", log_weight
        return log_weight

    def compute(self, trial_result_list, max_rate):
        """FIXME."""
        # TODO: Implement safe rate limit.
        duration = 0.5 + self.trial_duration
        def value_lweight_f(x, y):
            """FIXME."""
            X = (x + 1.0) / 2
            mrr = max_rate * math.tan(X * Integrator.Integrator__HALF_PI)
            koeff = (x + 1.0) / 2
            lweight = self.lprob(mrr, koeff, trial_result_list)
            value = self.find_critical_rate(mrr, koeff, self.lps_target)
            return value, lweight
        avg, stdev = Integrator.integrate_2d(value_lweight_f, duration)
        return avg, stdev

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
            measurement.lsup = 0.0
            trial_result_list.append(measurement)
            trial_result_list.sort(key=lambda result: result.target_tr)
            for index, result in enumerate(trial_result_list):
                sup = 4 * (index + 1) * (trial_count - index)
                sup /= (trial_count + 1.0) ** 2
#                result.lsup += math.log(sup) / trial_count / 1000.0
            if stop_time <= time.time():
                return
            ## Zero trials computation usually leads to too high crit rate.
            #optimistic_tr = mplrm.receive_rate + self.lps_target
            #average = min(average, optimistic_tr)
            transmit_rate = min(max_rate, max(min_rate, average + 0 * stdev))

    @staticmethod
    def lfit(load, mrr, a):
        """FIXME."""
        print "load", load, "mrr", mrr, "a", a
        lep = (1.0 - mrr / load) * a
        loga = math.log(load) - math.log(log_plus(0.0, a))
        print "m/b", mrr / load, "lep", lep, "loga", loga
        direct = True
        if lep < 0:
            sloga = loga + lep - math.exp(lep)/2
            if sloga + math.exp(2 * lep) * 8 / 11 <= sloga:
                loga = sloga
                print "simplified loga", loga
                direct = False
        if direct:
            loga += math.log(lep + log_plus(0, -lep))
            print "direct loga", loga
#        print "loga", loga
        return loga

    @staticmethod
    def find_critical_rate(llps, *args, **kwargs):
        """FIXME."""
        rate = 1.0
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
        for count, result in enumerate(trial_result_list):
            lalps = self.lfit(result.target_tr, *args, **kwargs)
            lalpt = lalps + math.log((count + 1) * self.tdpt)
            log_p = result.loss_count * lalpt - math.exp(lalpt)
            log_p -= math.lgamma(1 + result.loss_count)
            log_weight += log_p  # * math.exp(result.lsup)
#            print "DEBUG for tr", result.target_tr, "lc", result.loss_count
#            print "lalps", lalps
#            print "lalpt", lalpt
#            print "log_p", log_p
#            print "lsup", result.lsup
#            print "log_weight", log_weight
        print "log_weight", log_weight
        return log_weight

    def compute(self, trial_result_list, max_rate, trial_duration):
        """FIXME."""
        # TODO: Implement safe rate limit.
        duration = 0.5 + trial_duration
        n = 2
        def value_lweight_f(*x):
            """FIXME."""
            X = [(x[first] + 1.0) / 2.0 for first in range(n)]
            mrr = max_rate * math.tan(X[1] * Integrator.Integrator__HALF_PI)
            a = math.pow(max_rate, x[0])
            print "mrr/mr", mrr / max_rate, "a", a
            lweight = self.lprob(trial_result_list, mrr, a)
            value = self.find_critical_rate(
                math.log(self.lps_target), mrr, a)
            return value, lweight
        avg, stdev = Integrator.integrate_nd(n, value_lweight_f, duration)
        return avg, stdev

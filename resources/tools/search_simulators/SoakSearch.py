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
        rate_distance = max_rate / 2.0
        trial_result_list = list()
        while 1:
            print "Iteration with interval [{a}, {b}]".format(
                a=transmit_rate - rate_distance, b=transmit_rate + rate_distance)
            # TODO: Do the calculations concurrently.
            measurement = self.measurer.measure(
                self.trial_duration, transmit_rate)
            min_limit = transmit_rate - rate_distance
            max_limit = transmit_rate + rate_distance
            sup_rate = None
            inf_rate = None
            for result in trial_result_list:
                rate = result.target_tr
                if rate < min_limit and (sup_rate is None or rate > sup_rate):
                    sup_rate = rate
                if rate > max_limit and (inf_rate is None or rate < inf_rate):
                    inf_rate = rate
            if sup_rate is None:
                sup_rate = min_limit
            if inf_rate is None:
                inf_rate = max_limit
            print "selecting [{min}, {max}]".format(min=sup_rate, max=inf_rate)
            relevant_list = list()
            for result in trial_result_list:
                rate = result.target_tr
#                print "debug rate {rate}".format(rate=rate)
                if rate >= sup_rate and rate <= inf_rate:
                    relevant_list.append(result)
#                else:
#                    print "discarded rate {rate}".format(rate=rate)
            average, stdev = self.compute(
                relevant_list, max_rate, 0.5 + self.trial_duration)
            if ((average - stdev >= max_rate)
                or (average + stdev <= min_rate)
                or (stdev / average <= self.rel_width)):
                return average, stdev
            trial_result_list.append(measurement)
            transmit_rate = min(max_rate, max(min_rate, average))
            rate_distance = stdev

    @staticmethod
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

    def lprob(self, safe_rate, excess_ratio, relevant_list):
        """FIXME."""
        log_weight = 0.0
        for result in relevant_list:
            alps = max(0.0, excess_ratio * (result.target_tr - safe_rate))
            if alps <= 0.0:
#                print "safe_rate={sr} has weight zero".format(sr=safe_rate)
                return None
            alpt = self.trial_duration * alps
            log_p = result.loss_count * math.log(alpt) - alpt
            log_p -= math.lgamma(1 + result.loss_count)
            log_weight += log_p
        return log_weight

    def compute(self, relevant_list, max_rate, compute_duration):
        """FIXME."""
        # TODO: Implement safe rate limit.
        time_stop = time.time() + compute_duration
        samples = 0
        nonzero_samples = 0
        log_weight_sum = None  # 0.0  # to avoid artifacts of too low weight sum
        crit_avg = max_rate / 2
        crit_m2 = None  # 2 * math.log(crit_avg)
        while 1:
            if time.time() >= time_stop:
                break
#            if samples == 0:
#                def function(argument):
#                    safe_rate, excess_ratio = argument
#                    lp = self.lprob(safe_rate, excess_ratio, relevant_list)
#                    return -math.exp(lp) if lp is not None else 0.0
#                result = scipy.optimize.fmin(
#                    function, x0=(1000, 0.5), maxiter=99999)
#                safe_rate, excess_ratio = result
#            else:
            safe_rate = random.random() * max_rate
            excess_ratio = random.random()
            log_weight = self.lprob(safe_rate, excess_ratio, relevant_list)
            samples += 1
            if log_weight is None:
#                print "continuing on weight zero"
                continue
            nonzero_samples += 1
            crit = min(max_rate, safe_rate + self.lps_target / excess_ratio)
            old_lwsum = log_weight_sum
            delta = crit - crit_avg
            log_weight_sum = self.log_plus(log_weight_sum, log_weight)
            rel_lweight = log_weight - log_weight_sum
            crit_avg += delta * math.exp(rel_lweight)
            if old_lwsum is not None and delta > 0.0:
                m2_plus = 2 * math.log(delta) + old_lwsum
                m2_plus += log_weight - log_weight_sum
                crit_m2 = self.log_plus(crit_m2, m2_plus)
        weight_sum = math.exp(log_weight_sum)
        print "samples {s}".format(s=samples)
        print "nonzero samples {ns}".format(ns=nonzero_samples)
        print "weight sum {ws}".format(ws=weight_sum)
        log_stdev = (crit_m2 - log_weight_sum) / 2
        print "log_stdev {ls}".format(ls=log_stdev)
        stdev = math.exp(log_stdev)
        print "returning avg={avg}, stdev={std}".format(
            avg=crit_avg, std=stdev)
        return crit_avg, stdev

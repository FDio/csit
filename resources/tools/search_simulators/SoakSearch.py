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
            limit_rate = max_rate
            for result in trial_result_list:
                loss = result.loss_count
                if result.loss_count <= 0:
                    continue
                limit_rate = min(
                    limit_rate, result.target_tr - loss / self.trial_duration)
            print "limit_rate", limit_rate
            average, stdev = self.compute(
                trial_result_list, max_rate, limit_rate,
                transmit_rate, rate_distance)
            if ((average - stdev >= max_rate)
#                or (average + stdev <= min_rate)
                or (stdev / average <= self.rel_width)):
                return average, stdev
            trial_result_list.append(measurement)
#            transmit_rate = min(max_rate, max(min_rate, average))
            transmit_rate = average
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

    def lprob(
            self, safe_rate, excess_ratio, trial_result_list,
            transmit_rate, rate_distance):
        """FIXME."""
        log_weight = 0.0
#        debug = True if transmit_rate < 4500000 else False
#        if debug:
#            print "DEBUG computing for transmit_rate", transmit_rate
#            print "safe_rate", safe_rate, "excess_ratio", excess_ratio
        for result in trial_result_list:
            alps = max(0.0, excess_ratio * (result.target_tr - safe_rate))
            if alps <= 0.0 and result.loss_count > 0:
                print "safe_rate={sr} has weight zero".format(sr=safe_rate)
                return None
            alpt = self.trial_duration * alps
            if alpt > 0.0:
                log_p = result.loss_count * math.log(alpt) - alpt
            else:
                log_p = 0.0
            log_p -= math.lgamma(1 + result.loss_count)
#            sigmas = (result.target_tr - transmit_rate) / (0.5 + rate_distance)
            sigmas = 0.0
            supressed = log_p / (1.0 + sigmas * sigmas)
            log_weight += supressed
#            if debug:
#                print "DEBUG for tr", result.target_tr, "lc", result.loss_count
#                print "alps", alps
#                print "alpt", alpt
#                print "log_p", log_p
#                print "sigmas", sigmas
#                print "supressed", supressed
#                print "log_weight", log_weight
        return log_weight

    def compute(
            self, trial_result_list, max_rate, limit_rate,
            transmit_rate, rate_distance):
        """FIXME."""
        # TODO: Implement safe rate limit.
        time_stop = time.time() + 0.5 + self.trial_duration
        samples = 0
        nonzero_samples = 0
        log_weight_sum = None  # 0.0  # to avoid artifacts of too low weight sum
        crit_avg = max_rate / 2.0
        crit_m2 = None  # 2 * math.log(crit_avg)
        safe_avg = limit_rate / 2.0
        elr_avg = 0.5
        while 1:
            if time.time() >= time_stop:
                break
            safe_rate = random.random() * limit_rate
            excess_ratio = random.random()
            log_weight = self.lprob(
                safe_rate, excess_ratio, trial_result_list,
                transmit_rate, rate_distance)
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
            rel_weight = math.exp(rel_lweight)
            crit_avg += delta * rel_weight
            safe_avg += (safe_rate - safe_avg) * rel_weight
            elr_avg += (excess_ratio - elr_avg) * rel_weight
            abs_delta = abs(delta)
            if old_lwsum is not None and abs_delta > 0.0:
                m2_plus = 2 * math.log(abs_delta) + old_lwsum
                m2_plus += log_weight - log_weight_sum
                crit_m2 = self.log_plus(crit_m2, m2_plus)
        weight_sum = math.exp(log_weight_sum)
        print "samples", samples
        print "nonzero samples", nonzero_samples
        print "weight sum", weight_sum
        log_stdev = (crit_m2 - log_weight_sum) / 2
        print "log_stdev", log_stdev
        stdev = math.exp(log_stdev)
        print "returning avg", crit_avg, "stdev", stdev
        print "safe_avg", safe_avg, "elr_avg", elr_avg
        return crit_avg, stdev

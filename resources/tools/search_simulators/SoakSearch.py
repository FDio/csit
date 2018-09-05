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
        transmit_rate = max_rate
        rate_distance = max_rate
        trial_result_list = list()
        while 1:
            print "Iteration with interval [{a}, {b}]".format(
                a=transmit_rate - rate_distance, b=transmit_rate + rate_distance)
            # TODO: Do the calculations concurrently.
            measurement = self.measurer.measure(
                self.trial_duration, transmit_rate)
            relevant_list = [
                result for result in trial_result_list
                if abs(result.target_tr - transmit_rate) <= rate_distance]
            average, stdev = self.compute(relevant_list, max_rate, 1.5)
            if ((average - stdev >= max_rate)
                or (average + stdev <= min_rate)
                or (stdev / average <= self.rel_width)):
                return average, stdev
            trial_result_list.append(measurement)
            transmit_rate = min(max_rate, max(min_rate, average))
            rate_distance = stdev

    def compute(self, relevant_list, max_rate, compute_duration):
        """FIXME."""
        # TODO: Implement safe rate limit.
        time_stop = time.time() + compute_duration
        samples = 0
        nonzero_samples = 0
        weight_sum = 1.0  # to avoid artifacts of too low weight sum
        crit_avg = max_rate
        crit_m2 = max_rate * max_rate
        while 1:
            safe_rate = random.random() * max_rate
            excess_ratio = random.random()
            weight = 1.0
            for result in relevant_list:
                alps = max(0.0, excess_ratio * (result.target_tr - safe_rate))
                if alps <= 0.0:
                    weight = 0.0
#                    print "safe_rate={sr} has probability zero".format(sr=safe_rate)
                    break
                alpt = self.trial_duration * alps
                log_p = result.loss_count * math.log(alpt) - alpt
                log_p -= math.lgamma(1 + result.loss_count)
                weight *= math.exp(log_p)
                if weight <= 0.0:
#                    print "accumulated weight zero"
                    break
            samples += 1
#            if weight_sum >= 1.0 and time.time() >= time_stop:
            if time.time() >= time_stop:
                break
            if weight <= 0.0:
#                print "continuing on weight zero"
                continue
            nonzero_samples += 1
            crit = min(max_rate, safe_rate + self.lps_target / excess_ratio)
            old_wsum = weight_sum
            delta = crit - crit_avg
            weight_sum += weight
            rel_weight = weight / weight_sum
            crit_avg += delta * rel_weight
            crit_m2 += delta * delta * old_wsum * rel_weight
        print "samples {s}".format(s=samples)
        print "nonzero samples {ns}".format(ns=nonzero_samples)
        print "weight sum {ws}".format(ws=weight_sum)
        stdev = math.sqrt(crit_m2 / weight_sum)
        print "returning avg={avg}, stdev={stdev}".format(avg=crit_avg, stdev=stdev)
        return crit_avg, stdev

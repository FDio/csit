# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Drop rate search algorithms"""

from abc import ABCMeta, abstractmethod
from enum import Enum, unique

@unique
class SearchDirection(Enum):
    top_down = 1
    bottom_up = 2

@unique
class SearchResults(Enum):
    SUCCESS = 1
    FAILED = 2
    SUSPICIOUS = 3

@unique
class RateType(Enum):
    percentage = 1
    pps = 2
    bps = 3

@unique
class LossAcceptanceType(Enum):
    frames = 1
    percentage = 2

class DropRateSearch(object):
    """Abstract class with search algorithm implemented"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self._duration = 60
        self._rate_start = 100
        self._rate_linear_step = 10
        self._rate_max = 100
        self._rate_min = 1
        self._rate_type = RateType.percentage
        self._loss_acceptance = 0
        self._loss_acceptance_type = LossAcceptanceType.frames
        self._duration = 60
        self._frame_size = "64"
        #binary convergence criterium type is self._rate_type
        self._binary_convergence_threshhold = "0.01"
        self._max_attempts = 1

    @abstractmethod
    def measure_loss(self, rate, frame_size, loss_acceptance,
                     loss_acceptance_type, duration):
        """Send traffic from TG and measure count of dropped frames
        :param TODO:
        :type TODO:
        :return (drop threshhold exceeded: True/False, statistics)
        :rtype int str
        """
        pass

    def set_search_rate_boundaries(self, max_rate, min_rate):
        if min_rate < 0:
            raise Exception("min_rate must be higher than 0")
        elif min_rate > max_rate:
            raise Exception("min_rate must be lower than max_rate")
        else:
            self._rate_max = max_rate
            self._rate_min = min_rate

    def set_search_linear_step(self, step_rate):
        self._rate_linear_step = step_rate

    def set_search_rate_type(self, rate_type):
        self._rate_type = rate_type

    def set_search_frame_size(self, frame_size):
        self._frame_size = frame_size

    def linear_search(self, start_rate, search_direction):

        if not self._rate_min < start_rate < self._rate_max:
            raise Exception("Start rate is not in min,max range")

        rate = start_rate
        #the last but one step
        prev_rate = None

        #linear search
        while True:
            res, stats = self.measure_loss(rate, self._frame_size,
                                           self._loss_acceptance,
                                           self._loss_acceptance_type,
                                           self._duration)
            if search_direction == SearchDirection.bottom_up:
                #loss occured and it was above acceptance criteria
                if res == False:
                    #if this is first run then we didn't find drop rate
                    if prev_rate == None:
                        return SearchResults.FAILED, None
                    # else we found the rate, which is value from previous run
                    else:
                        return SearchResults.SUCCESS, prev_rate
                #there was no loss / loss below acceptance criteria
                elif res == True:
                    prev_rate = rate
                    rate += self._rate_linear_step
                    if rate > self._rate_max:
                        if prev_rate != self._rate_max:
                            #one last step with rate set to max_rate
                            rate = self._rate_max
                            continue
                        else:
                            return SearchResults.SUCCESS, prev_rate
                    else:
                        continue
                else:
                    raise RuntimeError("Unknown search result")

            elif search_direction == SearchDirection.top_down:
                #loss occured, decrease rate
                if res == False:
                    prev_rate = rate
                    rate -= self._rate_linear_step
                    if rate < self._rate_min:
                        return SearchResults.FAILED, None
                    else:
                        continue
                #no loss => non/partial drop rate found
                elif res == True:
                    return SearchResults.SUCCESS, rate
                else:
                    raise RuntimeError("Unknown search result")
            else:
                raise Exception("Unknown search direction")

        raise Exception("Wrong codepath")

    def binary_search(self):
        raise NotImplementedError

    def combined_search(self):
        raise NotImplementedError

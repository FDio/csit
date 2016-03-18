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
    """Direction of linear search"""

    TOP_DOWN = 1
    BOTTOM_UP = 2

@unique
class SearchResults(Enum):
    """Result of the drop rate search"""

    SUCCESS = 1
    FAILURE = 2
    SUSPICIOUS = 3

@unique
class RateType(Enum):
    """Type of rate units"""

    PERCENTAGE = 1
    PACKETS_PER_SECOND = 2
    BITS_PER_SECOND = 3

@unique
class LossAcceptanceType(Enum):
    """Type of the loss acceptance criteria"""

    FRAMES = 1
    PERCENTAGE = 2

class DropRateSearch(object):
    """Abstract class with search algorithm implementation"""

    __metaclass__ = ABCMeta

    def __init__(self):
        #duration of traffic run (binary, linear)
        self._duration = 60
        #initial start rate (binary, linear)
        self._rate_start = 100
        #step of the linear search, unit: RateType (self._rate_type)
        self._rate_linear_step = 10
        #last rate of the binary search, unit: RateType (self._rate_type)
        self._last_binary_rate = 0
        #linear search direction, permitted values: SearchDirection
        self._search_linear_direction = SearchDirection.TOP_DOWN
        #upper limit of search, unit: RateType (self._rate_type)
        self._rate_max = 100
        #lower limit of search, unit: RateType (self._rate_type)
        self._rate_min = 1
        #permitted values: RateType
        self._rate_type = RateType.PERCENTAGE
        #accepted loss during search, units: LossAcceptanceType
        self._loss_acceptance = 0
        #permitted values: LossAcceptanceType
        self._loss_acceptance_type = LossAcceptanceType.FRAMES
        #size of frames to send
        self._frame_size = "64"
        #binary convergence criterium type is self._rate_type
        self._binary_convergence_threshold = 100000
        #numbers of traffic runs during one rate step
        self._max_attempts = 1

        #result of search
        self._search_result = None
        self._search_result_rate = None

    @abstractmethod
    def measure_loss(self, rate, frame_size, loss_acceptance,
                     loss_acceptance_type, traffic_type):
        """Send traffic from TG and measure count of dropped frames

        :param rate: offered traffic load
        :param frame_size: size of frame
        :param loss_acceptance: permitted drop ratio or frames count
        :param loss_acceptance_type: type of permitted loss
        :param traffic_type: traffic profile ([2,3]-node-L[2,3], ...)
        :type rate: int
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_type: str
        :return: drop threshold exceeded? (True/False)
        :rtype bool
        """
        pass

    def set_search_rate_boundaries(self, max_rate, min_rate):
        """Set search boundaries: min,max

        :param max_rate: upper value of search boundaries
        :param min_rate: lower value of search boundaries
        :type max_rate: float
        :type min_rate: float
        :return: nothing
        """
        if float(min_rate) <= 0:
            raise ValueError("min_rate must be higher than 0")
        elif float(min_rate) > float(max_rate):
            raise ValueError("min_rate must be lower than max_rate")
        else:
            self._rate_max = float(max_rate)
            self._rate_min = float(min_rate)

    def set_search_linear_step(self, step_rate):
        """Set step size for linear search

        :param step_rate: linear search step size
        :type step_rate: float
        :return: nothing
        """
        self._rate_linear_step = float(step_rate)

    def set_search_rate_type_percentage(self):
        """Set rate type to percentage of linerate

        :return: nothing
        """
        self._set_search_rate_type(RateType.PERCENTAGE)

    def set_search_rate_type_bps(self):
        """Set rate type to bits per second

        :return: nothing
        """
        self._set_search_rate_type(RateType.BITS_PER_SECOND)

    def set_search_rate_type_pps(self):
        """Set rate type to packets per second

        :return: nothing
        """
        self._set_search_rate_type(RateType.PACKETS_PER_SECOND)

    def _set_search_rate_type(self, rate_type):
        """Set rate type to one of RateType-s

        :param rate_type: type of rate to set
        :type rate_type: RateType
        :return: nothing
        """
        if rate_type not in RateType:
            raise Exception("rate_type unknown: {}".format(rate_type))
        else:
            self._rate_type = rate_type

    def set_search_frame_size(self, frame_size):
        """Set size of frames to send

        :param frame_size: size of frames
        :type frame_size: str
        :return: nothing
        """
        self._frame_size = frame_size

    def set_duration(self, duration):
        """Set the duration of single traffic run

        :param duration: number of seconds for traffic to run
        :type duration: int
        :return: nothing
        """
        self._duration = int(duration)

    def get_duration(self):
        """Return configured duration of single traffic run

        :return: number of seconds for traffic to run
        :rtype: int
        """
        return self._duration

    def set_binary_convergence_threshold(self, convergence):
        """Set convergence for binary search

        :param convergence: treshold value number
        :type convergence: float
        :return: nothing
        """
        self._binary_convergence_threshold = float(convergence)

    def get_binary_convergence_threshold(self):
        """Get convergence for binary search

        :return: treshold value number
        :rtype: float
        """
        return self._binary_convergence_threshold

    def get_rate_type_str(self):
        """Return rate type representation

        :return: string representation of rate type
        :rtype: str
        """
        if self._rate_type == RateType.PERCENTAGE:
            return "%"
        elif self._rate_type == RateType.BITS_PER_SECOND:
            return "bps"
        elif self._rate_type == RateType.PACKETS_PER_SECOND:
            return "pps"
        else:
            raise ValueError("RateType unknown")

    def linear_search(self, start_rate, traffic_type):
        """Linear search of rate with loss below acceptance criteria

        :param start_rate: initial rate
        :param traffic_type: traffic profile
        :type start_rate: float
        :param traffic_type: str
        :return: nothing
        """

        if not self._rate_min <= float(start_rate) <= self._rate_max:
            raise ValueError("Start rate is not in min,max range")

        rate = float(start_rate)
        #the last but one step
        prev_rate = None

        #linear search
        while True:
            res = self.measure_loss(rate, self._frame_size,
                                    self._loss_acceptance,
                                    self._loss_acceptance_type,
                                    traffic_type)
            if self._search_linear_direction == SearchDirection.BOTTOM_UP:
                #loss occured and it was above acceptance criteria
                if res == False:
                    #if this is first run then we didn't find drop rate
                    if prev_rate == None:
                        self._search_result = SearchResults.FAILURE
                        self._search_result_rate = None
                        return
                    # else we found the rate, which is value from previous run
                    else:
                        self._search_result = SearchResults.SUCCESS
                        self._search_result_rate = prev_rate
                        return
                #there was no loss / loss below acceptance criteria
                elif res == True:
                    prev_rate = rate
                    rate += self._rate_linear_step
                    if rate > self._rate_max:
                        if prev_rate != self._rate_max:
                            #one last step with rate set to _rate_max
                            rate = self._rate_max
                            continue
                        else:
                            self._search_result = SearchResults.SUCCESS
                            self._search_result_rate = prev_rate
                            return
                    else:
                        continue
                else:
                    raise RuntimeError("Unknown search result")

            elif self._search_linear_direction == SearchDirection.TOP_DOWN:
                #loss occured, decrease rate
                if res == False:
                    prev_rate = rate
                    rate -= self._rate_linear_step
                    if rate < self._rate_min:
                        if prev_rate != self._rate_min:
                            #one last step with rate set to _rate_min
                            rate = self._rate_min
                            continue
                        else:
                            self._search_result = SearchResults.FAILURE
                            self._search_result_rate = None
                            return
                    else:
                        continue
                #no loss => non/partial drop rate found
                elif res == True:
                    self._search_result = SearchResults.SUCCESS
                    self._search_result_rate = rate
                    return
                else:
                    raise RuntimeError("Unknown search result")
            else:
                raise Exception("Unknown search direction")

        raise Exception("Wrong codepath")

    def verify_search_result(self):
        """Fail if search was not successful

        :return: result rate
        :rtype: float
        """
        if self._search_result == SearchResults.FAILURE:
            raise Exception('Search FAILED')
        elif self._search_result in [SearchResults.SUCCESS, SearchResults.SUSPICIOUS]:
            return self._search_result_rate

    def binary_search(self, b_min, b_max, traffic_type):
        """Binary search of rate with loss below acceptance criteria

        :param b_min: min range rate
        :param b_max: max range rate
        :param traffic_type: traffic profile
        :type b_min: float
        :type b_max: float
        :type traffic_type: str
        :return: nothing
        """

        if not self._rate_min <= float(b_min) <= self._rate_max:
            raise ValueError("Min rate is not in min,max range")
        if not self._rate_min <= float(b_max) <= self._rate_max:
            raise ValueError("Max rate is not in min,max range")
        if float(b_max) < float(b_min):
            raise ValueError("Min rate is greater then max rate")

        #binary search
        #rate is half of interval + start of interval
        rate = ((float(b_max) - float(b_min)) / 2) + float(b_min)
        #rate diff with previous run
        rate_diff = abs(self._last_binary_rate - rate)

        #convergence criterium
        if float(rate_diff) < float(self._binary_convergence_threshold):
            if not self._search_result_rate:
                self._search_result = SearchResults.FAILURE
            else:
                self._search_result = SearchResults.SUCCESS
            return

        self._last_binary_rate = rate

        res = self.measure_loss(rate, self._frame_size,
                                self._loss_acceptance,
                                self._loss_acceptance_type,
                                traffic_type)
        #loss occured and it was above acceptance criteria
        if res == False:
            self.binary_search(b_min, rate, traffic_type)
        #there was no loss / loss below acceptance criteria
        elif res == True:
            self._search_result_rate = rate
            self.binary_search(rate, b_max, traffic_type)
        else:
            raise RuntimeError("Unknown search result")

    def combined_search(self):
        raise NotImplementedError

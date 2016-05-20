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
    """Direction of linear search."""

    TOP_DOWN = 1
    BOTTOM_UP = 2


@unique
class SearchResults(Enum):
    """Result of the drop rate search."""

    SUCCESS = 1
    FAILURE = 2
    SUSPICIOUS = 3


@unique
class RateType(Enum):
    """Type of rate units."""

    PERCENTAGE = 1
    PACKETS_PER_SECOND = 2
    BITS_PER_SECOND = 3


@unique
class LossAcceptanceType(Enum):
    """Type of the loss acceptance criteria."""

    FRAMES = 1
    PERCENTAGE = 2


@unique
class SearchResultType(Enum):
    """Type of search result evaluation."""

    BEST_OF_N = 1
    WORST_OF_N = 2


class DropRateSearch(object):
    """Abstract class with search algorithm implementation."""

    __metaclass__ = ABCMeta

    def __init__(self):
        # duration of traffic run (binary, linear)
        self._duration = 60
        # initial start rate (binary, linear)
        self._rate_start = 100
        # step of the linear search, unit: RateType (self._rate_type)
        self._rate_linear_step = 10
        # last rate of the binary search, unit: RateType (self._rate_type)
        self._last_binary_rate = 0
        # linear search direction, permitted values: SearchDirection
        self._search_linear_direction = SearchDirection.TOP_DOWN
        # upper limit of search, unit: RateType (self._rate_type)
        self._rate_max = 100
        # lower limit of search, unit: RateType (self._rate_type)
        self._rate_min = 1
        # permitted values: RateType
        self._rate_type = RateType.PERCENTAGE
        # accepted loss during search, units: LossAcceptanceType
        self._loss_acceptance = 0
        # permitted values: LossAcceptanceType
        self._loss_acceptance_type = LossAcceptanceType.FRAMES
        # size of frames to send
        self._frame_size = "64"
        # binary convergence criterium type is self._rate_type
        self._binary_convergence_threshold = 5000
        # numbers of traffic runs during one rate step
        self._max_attempts = 1
        # type of search result evaluation, unit: SearchResultType
        self._search_result_type = SearchResultType.BEST_OF_N

        # result of search
        self._search_result = None
        self._search_result_rate = None

    @abstractmethod
    def measure_loss(self, rate, frame_size, loss_acceptance,
                     loss_acceptance_type, traffic_type):
        """Send traffic from TG and measure count of dropped frames.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_type: Traffic profile ([2,3]-node-L[2,3], ...).
        :type rate: int
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_type: str
        :return: Drop threshold exceeded? (True/False)
        :rtype bool
        """
        pass

    def set_search_rate_boundaries(self, max_rate, min_rate):
        """Set search boundaries: min,max.

        :param max_rate: Upper value of search boundaries.
        :param min_rate: Lower value of search boundaries.
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

    def set_loss_acceptance(self, loss_acceptance):
        """Set loss acceptance treshold for PDR search.

        :param loss_acceptance: Loss acceptance treshold for PDR search.
        :type loss_acceptance: str
        :return: nothing
        """
        if float(loss_acceptance) < 0:
            raise ValueError("Loss acceptance must be higher or equal 0")
        else:
            self._loss_acceptance = float(loss_acceptance)

    def get_loss_acceptance(self):
        """Return configured loss acceptance treshold.

        :return: Loss acceptance treshold.
        :rtype: float
        """
        return self._loss_acceptance

    def set_loss_acceptance_type_percentage(self):
        """Set loss acceptance treshold type to percentage.

        :return: nothing
        """
        self._loss_acceptance_type = LossAcceptanceType.PERCENTAGE

    def set_loss_acceptance_type_frames(self):
        """Set loss acceptance treshold type to frames.

        :return: nothing
        """
        self._loss_acceptance_type = LossAcceptanceType.FRAMES

    def loss_acceptance_type_is_percentage(self):
        """Return true if loss acceptance treshold type is percentage,
           false otherwise.

        :return: True if loss acceptance treshold type is percentage.
        :rtype: boolean
        """
        return self._loss_acceptance_type == LossAcceptanceType.PERCENTAGE

    def set_search_linear_step(self, step_rate):
        """Set step size for linear search.

        :param step_rate: Linear search step size.
        :type step_rate: float
        :return: nothing
        """
        self._rate_linear_step = float(step_rate)

    def set_search_rate_type_percentage(self):
        """Set rate type to percentage of linerate.

        :return: nothing
        """
        self._set_search_rate_type(RateType.PERCENTAGE)

    def set_search_rate_type_bps(self):
        """Set rate type to bits per second.

        :return: nothing
        """
        self._set_search_rate_type(RateType.BITS_PER_SECOND)

    def set_search_rate_type_pps(self):
        """Set rate type to packets per second.

        :return: nothing
        """
        self._set_search_rate_type(RateType.PACKETS_PER_SECOND)

    def _set_search_rate_type(self, rate_type):
        """Set rate type to one of RateType-s.

        :param rate_type: Type of rate to set.
        :type rate_type: RateType
        :return: nothing
        """
        if rate_type not in RateType:
            raise Exception("rate_type unknown: {}".format(rate_type))
        else:
            self._rate_type = rate_type

    def set_search_frame_size(self, frame_size):
        """Set size of frames to send.

        :param frame_size: Size of frames.
        :type frame_size: str
        :return: nothing
        """
        self._frame_size = frame_size

    def set_duration(self, duration):
        """Set the duration of single traffic run.

        :param duration: Number of seconds for traffic to run.
        :type duration: int
        :return: nothing
        """
        self._duration = int(duration)

    def get_duration(self):
        """Return configured duration of single traffic run.

        :return: Number of seconds for traffic to run.
        :rtype: int
        """
        return self._duration

    def set_binary_convergence_threshold(self, convergence):
        """Set convergence for binary search.

        :param convergence: Treshold value number.
        :type convergence: float
        :return: nothing
        """
        self._binary_convergence_threshold = float(convergence)

    def get_binary_convergence_threshold(self):
        """Get convergence for binary search.

        :return: Treshold value number.
        :rtype: float
        """
        return self._binary_convergence_threshold

    def get_rate_type_str(self):
        """Return rate type representation.

        :return: String representation of rate type.
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

    def set_max_attempts(self, max_attempts):
        """Set maximum number of traffic runs during one rate step.

        :param max_attempts: Number of traffic runs.
        :type max_attempts: int
        :return: nothing
        """
        if int(max_attempts) > 0:
            self._max_attempts = int(max_attempts)
        else:
            raise ValueError("Max attempt must by greater then zero")

    def get_max_attempts(self):
        """Return maximum number of traffic runs during one rate step.

        :return: Number of traffic runs.
        :rtype: int
        """
        return self._max_attempts

    def set_search_result_type_best_of_n(self):
        """Set type of search result evaluation to Best of N.

        :return: nothing
        """
        self._set_search_result_type(SearchResultType.BEST_OF_N)

    def set_search_result_type_worst_of_n(self):
        """Set type of search result evaluation to Worst of N.

        :return: nothing
        """
        self._set_search_result_type(SearchResultType.WORST_OF_N)

    def _set_search_result_type(self, search_type):
        """Set type of search result evaluation to one of SearchResultType.

        :param search_type: Type of search result evaluation to set.
        :type search_type: SearchResultType
        :return: nothing
        """
        if search_type not in SearchResultType:
            raise ValueError("search_type unknown: {}".format(search_type))
        else:
            self._search_result_type = search_type

    @staticmethod
    def _get_best_of_n(res_list):
        """Return best result of N traffic runs.

        :param res_list: List of return values from all runs at one rate step.
        :type res_list: list
        :return: True if at least one run is True, False otherwise.
        :rtype: boolean
        """
        # Return True if any element of the iterable is True.
        return any(res_list)

    @staticmethod
    def _get_worst_of_n(res_list):
        """Return worst result of N traffic runs.

        :param res_list: List of return values from all runs at one rate step.
        :type res_list: list
        :return: False if at least one run is False, True otherwise.
        :rtype: boolean
        """
        # Return False if not all elements of the iterable are True.
        return not all(res_list)

    def _get_res_based_on_search_type(self, res_list):
        """Return result of search based on search evaluation type.

        :param res_list: List of return values from all runs at one rate step.
        :type res_list: list
        :return: Boolean based on search result type.
        :rtype: boolean
        """
        if self._search_result_type == SearchResultType.BEST_OF_N:
            return self._get_best_of_n(res_list)
        elif self._search_result_type == SearchResultType.WORST_OF_N:
            return self._get_worst_of_n(res_list)
        else:
            raise ValueError("Unknown search result type")

    def linear_search(self, start_rate, traffic_type):
        """Linear search of rate with loss below acceptance criteria.

        :param start_rate: Initial rate.
        :param traffic_type: Traffic profile.
        :type start_rate: float
        :type traffic_type: str
        :return: nothing
        """

        if not self._rate_min <= float(start_rate) <= self._rate_max:
            raise ValueError("Start rate is not in min,max range")

        rate = float(start_rate)
        # the last but one step
        prev_rate = None

        # linear search
        while True:
            res = []
            for dummy in range(self._max_attempts):
                res.append(self.measure_loss(rate, self._frame_size,
                                             self._loss_acceptance,
                                             self._loss_acceptance_type,
                                             traffic_type))

            res = self._get_res_based_on_search_type(res)

            if self._search_linear_direction == SearchDirection.BOTTOM_UP:
                # loss occurred and it was above acceptance criteria
                if not res:
                    # if this is first run then we didn't find drop rate
                    if prev_rate is None:
                        self._search_result = SearchResults.FAILURE
                        self._search_result_rate = None
                        return
                    # else we found the rate, which is value from previous run
                    else:
                        self._search_result = SearchResults.SUCCESS
                        self._search_result_rate = prev_rate
                        return
                # there was no loss / loss below acceptance criteria
                elif res:
                    prev_rate = rate
                    rate += self._rate_linear_step
                    if rate > self._rate_max:
                        if prev_rate != self._rate_max:
                            # one last step with rate set to _rate_max
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
                # loss occurred, decrease rate
                if not res:
                    prev_rate = rate
                    rate -= self._rate_linear_step
                    if rate < self._rate_min:
                        if prev_rate != self._rate_min:
                            # one last step with rate set to _rate_min
                            rate = self._rate_min
                            continue
                        else:
                            self._search_result = SearchResults.FAILURE
                            self._search_result_rate = None
                            return
                    else:
                        continue
                # no loss => non/partial drop rate found
                elif res:
                    self._search_result = SearchResults.SUCCESS
                    self._search_result_rate = rate
                    return
                else:
                    raise RuntimeError("Unknown search result")
            else:
                raise Exception("Unknown search direction")

        raise Exception("Wrong codepath")

    def verify_search_result(self):
        """Fail if search was not successful.

        :return: Result rate.
        :rtype: float
        """
        if self._search_result == SearchResults.FAILURE:
            raise Exception('Search FAILED')
        elif self._search_result in [SearchResults.SUCCESS,
                                     SearchResults.SUSPICIOUS]:
            return self._search_result_rate, self._latency_stats

    def binary_search(self, b_min, b_max, traffic_type, skip_max_rate=False):
        """Binary search of rate with loss below acceptance criteria.

        :param b_min: Min range rate.
        :param b_max: Max range rate.
        :param traffic_type: Traffic profile.
        :param skip_max_rate: Start with max rate first
        :type b_min: float
        :type b_max: float
        :type traffic_type: str
        :type skip_max_rate: bool
        :return: nothing
        """

        if not self._rate_min <= float(b_min) <= self._rate_max:
            raise ValueError("Min rate is not in min,max range")
        if not self._rate_min <= float(b_max) <= self._rate_max:
            raise ValueError("Max rate is not in min,max range")
        if float(b_max) < float(b_min):
            raise ValueError("Min rate is greater than max rate")

        # binary search
        if skip_max_rate:
            # rate is half of interval + start of interval
            rate = ((float(b_max) - float(b_min)) / 2) + float(b_min)
        else:
            # rate is max of interval
            rate =  float(b_max)
        # rate diff with previous run
        rate_diff = abs(self._last_binary_rate - rate)

        # convergence criterium
        if float(rate_diff) < float(self._binary_convergence_threshold):
            if not self._search_result_rate:
                self._search_result = SearchResults.FAILURE
            else:
                self._search_result = SearchResults.SUCCESS
            return

        self._last_binary_rate = rate

        res = []
        for dummy in range(self._max_attempts):
            res.append(self.measure_loss(rate, self._frame_size,
                                         self._loss_acceptance,
                                         self._loss_acceptance_type,
                                         traffic_type))

        res = self._get_res_based_on_search_type(res)

        # loss occurred and it was above acceptance criteria
        if not res:
            self.binary_search(b_min, rate, traffic_type, True)
        # there was no loss / loss below acceptance criteria
        else:
            self._search_result_rate = rate
            self.binary_search(rate, b_max, traffic_type, True)

    def combined_search(self, start_rate, traffic_type):
        """Combined search of rate with loss below acceptance criteria.

        :param start_rate: Initial rate.
        :param traffic_type: Traffic profile.
        :type start_rate: float
        :type traffic_type: str
        :return: nothing
        """

        self.linear_search(start_rate, traffic_type)

        if self._search_result in [SearchResults.SUCCESS,
                                   SearchResults.SUSPICIOUS]:
            b_min = self._search_result_rate
            b_max = self._search_result_rate + self._rate_linear_step

            # we found max rate by linear search
            if self.floats_are_close_equal(float(b_min), self._rate_max):
                return

            # limiting binary range max value into max range
            if float(b_max) > self._rate_max:
                b_max = self._rate_max

            # reset result rate
            temp_rate = self._search_result_rate
            self._search_result_rate = None

            # we will use binary search to refine search in one linear step
            self.binary_search(b_min, b_max, traffic_type, True)

            # linear and binary search succeed
            if self._search_result == SearchResults.SUCCESS:
                return
            # linear search succeed but binary failed or suspicious
            else:
                self._search_result = SearchResults.SUSPICIOUS
                self._search_result_rate = temp_rate
        else:
            raise RuntimeError("Linear search FAILED")

    @staticmethod
    def floats_are_close_equal(num_a, num_b, rel_tol=1e-9, abs_tol=0.0):
        """Compares two float numbers for close equality.

        :param num_a: First number to compare.
        :param num_b: Second number to compare.
        :param rel_tol=1e-9: The relative tolerance.
        :param abs_tol=0.0: The minimum absolute tolerance level.
        :type num_a: float
        :type num_b: float
        :type rel_tol: float
        :type abs_tol: float
        :return: Returns True if num_a is close in value to num_b or equal.
                 False otherwise.
        :rtype: boolean
        """

        if num_a == num_b:
            return True

        if rel_tol < 0.0 or abs_tol < 0.0:
            raise ValueError('Error tolerances must be non-negative')

        return abs(num_b - num_a) <= max(rel_tol * max(abs(num_a), abs(num_b)),
                                         abs_tol)


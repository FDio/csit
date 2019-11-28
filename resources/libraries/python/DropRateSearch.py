# Copyright (c) 2019 Cisco and/or its affiliates.
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


class DropRateSearch(metaclass=ABCMeta):
    """Abstract class with search algorithm implementation."""

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
        self._frame_size = u"64"
        # binary convergence criterion type is self._rate_type
        self._binary_convergence_threshold = 5000
        # numbers of traffic runs during one rate step
        self._max_attempts = 1
        # type of search result evaluation, unit: SearchResultType
        self._search_result_type = SearchResultType.BEST_OF_N

        # result of search
        self._search_result = None
        self._search_result_rate = None

    @abstractmethod
    def get_latency(self):
        """Return min/avg/max latency.

        :returns: Latency stats.
        :rtype: list
        """

    @abstractmethod
    def measure_loss(
            self, rate, frame_size, loss_acceptance, loss_acceptance_type,
            traffic_profile, skip_warmup=False):
        """Send traffic from TG and measure count of dropped frames.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_profile: Module name to use for traffic generation.
        :param skip_warmup: Start TRex without warmup traffic if true.
        :type rate: float
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_profile: str
        :type skip_warmup: bool
        :returns: Drop threshold exceeded? (True/False)
        :rtype: bool
        """

    def set_search_rate_boundaries(self, max_rate, min_rate):
        """Set search boundaries: min,max.

        :param max_rate: Upper value of search boundaries.
        :param min_rate: Lower value of search boundaries.
        :type max_rate: float
        :type min_rate: float
        :returns: nothing
        :raises ValueError: If min rate is lower than 0 or higher than max rate.
        """
        if float(min_rate) <= 0:
            msg = u"min_rate must be higher than 0"
        elif float(min_rate) > float(max_rate):
            msg = u"min_rate must be lower than max_rate"
        else:
            self._rate_max = float(max_rate)
            self._rate_min = float(min_rate)
            return
        raise ValueError(msg)

    def set_loss_acceptance(self, loss_acceptance):
        """Set loss acceptance threshold for PDR search.

        :param loss_acceptance: Loss acceptance threshold for PDR search.
        :type loss_acceptance: str
        :returns: nothing
        :raises ValueError: If loss acceptance is lower than zero.
        """
        if float(loss_acceptance) >= 0:
            self._loss_acceptance = float(loss_acceptance)
        else:
            raise ValueError(u"Loss acceptance must be higher or equal 0")

    def get_loss_acceptance(self):
        """Return configured loss acceptance threshold.

        :returns: Loss acceptance threshold.
        :rtype: float
        """
        return self._loss_acceptance

    def set_loss_acceptance_type_percentage(self):
        """Set loss acceptance threshold type to percentage.

        :returns: nothing
        """
        self._loss_acceptance_type = LossAcceptanceType.PERCENTAGE

    def set_loss_acceptance_type_frames(self):
        """Set loss acceptance threshold type to frames.

        :returns: nothing
        """
        self._loss_acceptance_type = LossAcceptanceType.FRAMES

    def loss_acceptance_type_is_percentage(self):
        """Return true if loss acceptance threshold type is percentage,
           false otherwise.

        :returns: True if loss acceptance threshold type is percentage.
        :rtype: boolean
        """
        return self._loss_acceptance_type == LossAcceptanceType.PERCENTAGE

    def set_search_linear_step(self, step_rate):
        """Set step size for linear search.

        :param step_rate: Linear search step size.
        :type step_rate: float
        :returns: nothing
        """
        self._rate_linear_step = float(step_rate)

    def set_search_rate_type_percentage(self):
        """Set rate type to percentage of linerate.

        :returns: nothing
        """
        self._set_search_rate_type(RateType.PERCENTAGE)

    def set_search_rate_type_bps(self):
        """Set rate type to bits per second.

        :returns: nothing
        """
        self._set_search_rate_type(RateType.BITS_PER_SECOND)

    def set_search_rate_type_pps(self):
        """Set rate type to packets per second.

        :returns: nothing
        """
        self._set_search_rate_type(RateType.PACKETS_PER_SECOND)

    def _set_search_rate_type(self, rate_type):
        """Set rate type to one of RateType-s.

        :param rate_type: Type of rate to set.
        :type rate_type: RateType
        :returns: nothing
        :raises Exception: If rate type is unknown.
        """
        if rate_type in RateType:
            self._rate_type = rate_type
        else:
            raise Exception(f"rate_type unknown: {rate_type}")

    def set_search_frame_size(self, frame_size):
        """Set size of frames to send.

        :param frame_size: Size of frames.
        :type frame_size: str
        :returns: nothing
        """
        self._frame_size = frame_size

    def set_duration(self, duration):
        """Set the duration of single traffic run.

        :param duration: Number of seconds for traffic to run.
        :type duration: int
        :returns: nothing
        """
        self._duration = int(duration)

    def get_duration(self):
        """Return configured duration of single traffic run.

        :returns: Number of seconds for traffic to run.
        :rtype: int
        """
        return self._duration

    def set_binary_convergence_threshold(self, convergence):
        """Set convergence for binary search.

        :param convergence: Threshold value number.
        :type convergence: float
        :returns: nothing
        """
        self._binary_convergence_threshold = float(convergence)

    def get_binary_convergence_threshold(self):
        """Get convergence for binary search.

        :returns: Threshold value number.
        :rtype: float
        """
        return self._binary_convergence_threshold

    def get_rate_type_str(self):
        """Return rate type representation.

        :returns: String representation of rate type.
        :rtype: str
        :raises ValueError: If rate type is unknown.
        """
        if self._rate_type == RateType.PERCENTAGE:
            retval = u"%"
        elif self._rate_type == RateType.BITS_PER_SECOND:
            retval = u"bps"
        elif self._rate_type == RateType.PACKETS_PER_SECOND:
            retval = u"pps"
        else:
            raise ValueError(u"RateType unknown")
        return retval

    def set_max_attempts(self, max_attempts):
        """Set maximum number of traffic runs during one rate step.

        :param max_attempts: Number of traffic runs.
        :type max_attempts: int
        :returns: nothing
        :raises ValueError: If max attempts is lower than zero.
        """
        if int(max_attempts) > 0:
            self._max_attempts = int(max_attempts)
        else:
            raise ValueError(u"Max attempt must by greater than zero")

    def get_max_attempts(self):
        """Return maximum number of traffic runs during one rate step.

        :returns: Number of traffic runs.
        :rtype: int
        """
        return self._max_attempts

    def set_search_result_type_best_of_n(self):
        """Set type of search result evaluation to Best of N.

        :returns: nothing
        """
        self._set_search_result_type(SearchResultType.BEST_OF_N)

    def set_search_result_type_worst_of_n(self):
        """Set type of search result evaluation to Worst of N.

        :returns: nothing
        """
        self._set_search_result_type(SearchResultType.WORST_OF_N)

    def _set_search_result_type(self, search_type):
        """Set type of search result evaluation to one of SearchResultType.

        :param search_type: Type of search result evaluation to set.
        :type search_type: SearchResultType
        :returns: nothing
        :raises ValueError: If search type is unknown.
        """
        if search_type in SearchResultType:
            self._search_result_type = search_type
        else:
            raise ValueError(f"search_type unknown: {search_type}")

    @staticmethod
    def _get_best_of_n(res_list):
        """Return best result of N traffic runs.

        :param res_list: List of return values from all runs at one rate step.
        :type res_list: list
        :returns: True if at least one run is True, False otherwise.
        :rtype: boolean
        """
        # Return True if any element of the iterable is True.
        return any(res_list)

    @staticmethod
    def _get_worst_of_n(res_list):
        """Return worst result of N traffic runs.

        :param res_list: List of return values from all runs at one rate step.
        :type res_list: list
        :returns: False if at least one run is False, True otherwise.
        :rtype: boolean
        """
        # Return False if not all elements of the iterable are True.
        return all(res_list)

    def _get_res_based_on_search_type(self, res_list):
        """Return result of search based on search evaluation type.

        :param res_list: List of return values from all runs at one rate step.
        :type res_list: list
        :returns: Boolean based on search result type.
        :rtype: boolean
        :raises ValueError: If search result type is unknown.
        """
        if self._search_result_type == SearchResultType.BEST_OF_N:
            retval = self._get_best_of_n(res_list)
        elif self._search_result_type == SearchResultType.WORST_OF_N:
            retval = self._get_worst_of_n(res_list)
        else:
            raise ValueError(u"Unknown search result type")
        return retval

    def linear_search(self, start_rate, traffic_profile):
        """Linear search of rate with loss below acceptance criteria.

        :param start_rate: Initial rate.
        :param traffic_profile: Module name to use for traffic generation.
        :type start_rate: float
        :type traffic_profile: str
        :returns: nothing
        :raises ValueError: If start rate is not in range.
        """
        if not self._rate_min <= float(start_rate) <= self._rate_max:
            raise ValueError(u"Start rate is not in min,max range")

        rate = float(start_rate)
        # the last but one step
        prev_rate = None

        # linear search
        while True:
            res = []
            for dummy in range(self._max_attempts):
                res.append(
                    self.measure_loss(
                        rate, self._frame_size, self._loss_acceptance,
                        self._loss_acceptance_type, traffic_profile
                    )
                )

            res = self._get_res_based_on_search_type(res)

            if self._search_linear_direction == SearchDirection.TOP_DOWN:
                # loss occurred, decrease rate
                if not res:
                    prev_rate = rate
                    rate -= self._rate_linear_step
                    if rate < self._rate_min:
                        if prev_rate != self._rate_min:
                            # one last step with rate set to _rate_min
                            rate = self._rate_min
                            continue
                        self._search_result = SearchResults.FAILURE
                        self._search_result_rate = None
                        return
                    continue
                # no loss => non/partial drop rate found
                elif res:
                    self._search_result = SearchResults.SUCCESS
                    self._search_result_rate = rate
                    return
                else:
                    raise RuntimeError(u"Unknown search result")
            else:
                raise Exception(u"Unknown search direction")

    def verify_search_result(self):
        """Fail if search was not successful.

        :returns: Result rate and latency stats.
        :rtype: tuple
        :raises Exception: If search failed.
        """
        if self._search_result in \
                [SearchResults.SUCCESS, SearchResults.SUSPICIOUS]:
            return self._search_result_rate, self.get_latency()
        raise Exception(u"Search FAILED")

    def binary_search(
            self, b_min, b_max, traffic_profile, skip_max_rate=False,
            skip_warmup=False):
        """Binary search of rate with loss below acceptance criteria.

        :param b_min: Min range rate.
        :param b_max: Max range rate.
        :param traffic_profile: Module name to use for traffic generation.
        :param skip_max_rate: Start with max rate first
        :param skip_warmup: Start TRex without warmup traffic if true.
        :type b_min: float
        :type b_max: float
        :type traffic_profile: str
        :type skip_max_rate: bool
        :type skip_warmup: bool
        :returns: nothing
        :raises ValueError: If input values are not valid.
        """
        if not self._rate_min <= float(b_min) <= self._rate_max:
            raise ValueError(u"Min rate is not in min,max range")
        if not self._rate_min <= float(b_max) <= self._rate_max:
            raise ValueError(u"Max rate is not in min,max range")
        if float(b_max) < float(b_min):
            raise ValueError(u"Min rate is greater than max rate")

        # rate is half of interval + start of interval if not using max rate
        rate = ((float(b_max) - float(b_min)) / 2) + float(b_min) \
            if skip_max_rate else float(b_max)

        # rate diff with previous run
        rate_diff = abs(self._last_binary_rate - rate)

        # convergence criterium
        if float(rate_diff) < float(self._binary_convergence_threshold):
            self._search_result = SearchResults.SUCCESS \
                if self._search_result_rate else SearchResults.FAILURE
            return

        self._last_binary_rate = rate

        res = []
        for dummy in range(self._max_attempts):
            res.append(self.measure_loss(
                rate, self._frame_size, self._loss_acceptance,
                self._loss_acceptance_type, traffic_profile,
                skip_warmup=skip_warmup
            ))

        res = self._get_res_based_on_search_type(res)

        # loss occurred and it was above acceptance criteria
        if not res:
            self.binary_search(b_min, rate, traffic_profile, True, True)
        # there was no loss / loss below acceptance criteria
        else:
            self._search_result_rate = rate
            self.binary_search(rate, b_max, traffic_profile, True, True)

    def combined_search(self, start_rate, traffic_profile):
        """Combined search of rate with loss below acceptance criteria.

        :param start_rate: Initial rate.
        :param traffic_profile: Module name to use for traffic generation.
        :type start_rate: float
        :type traffic_profile: str
        :returns: nothing
        :raises RuntimeError: If linear search failed.
        """
        self.linear_search(start_rate, traffic_profile)

        if self._search_result in \
                [SearchResults.SUCCESS, SearchResults.SUSPICIOUS]:
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
            self.binary_search(b_min, b_max, traffic_profile, True)


            # linear search succeed but binary failed or suspicious
            if self._search_result != SearchResults.SUCCESS:
                self._search_result = SearchResults.SUSPICIOUS
                self._search_result_rate = temp_rate
            # linear and binary search succeed
            else:
                return
        else:
            raise RuntimeError(u"Linear search FAILED")

    @staticmethod
    def floats_are_close_equal(num_a, num_b, rel_tol=1e-9, abs_tol=0.0):
        """Compares two float numbers for close equality.

        :param num_a: First number to compare.
        :param num_b: Second number to compare.
        :param rel_tol: The relative tolerance.
        :param abs_tol: The minimum absolute tolerance level. (Optional,
            default value: 0.0)
        :type num_a: float
        :type num_b: float
        :type rel_tol: float
        :type abs_tol: float
        :returns: Returns True if num_a is close in value to num_b or equal.
            False otherwise.
        :rtype: boolean
        :raises ValueError: If input values are not valid.
        """
        if num_a == num_b:
            return True

        if rel_tol < 0.0 or abs_tol < 0.0:
            raise ValueError(u"Error tolerances must be non-negative")

        return abs(num_b - num_a) <= max(
            rel_tol * max(abs(num_a), abs(num_b)), abs_tol
        )

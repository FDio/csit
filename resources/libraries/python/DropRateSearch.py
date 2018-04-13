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
import math
import logging

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
    def get_latency(self):
        """Return min/avg/max latency.

        :returns: Latency stats.
        :rtype: list
        """
        pass

    @abstractmethod
    def measure_loss(self, rate, frame_size, loss_acceptance,
                     loss_acceptance_type, traffic_type, skip_warmup=False):
        """Send traffic from TG and measure count of dropped frames.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_type: Traffic profile ([2,3]-node-L[2,3], ...).
        :param skip_warmup: Start TRex without warmup traffic if true.
        :type rate: int
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_type: str
        :type traffic_type: bool
        :returns: Drop threshold exceeded? (True/False)
        :rtype bool
        """
        pass

    def set_search_rate_boundaries(self, max_rate, min_rate):
        """Set search boundaries: min,max.

        :param max_rate: Upper value of search boundaries.
        :param min_rate: Lower value of search boundaries.
        :type max_rate: float
        :type min_rate: float
        :returns: nothing
        :raises: ValueError if min rate is lower than 0 and higher than max rate
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
        :returns: nothing
        :raises: ValueError if loss acceptance is lower than zero
        """
        if float(loss_acceptance) < 0:
            raise ValueError("Loss acceptance must be higher or equal 0")
        else:
            self._loss_acceptance = float(loss_acceptance)

    def get_loss_acceptance(self):
        """Return configured loss acceptance treshold.

        :returns: Loss acceptance treshold.
        :rtype: float
        """
        return self._loss_acceptance

    def set_loss_acceptance_type_percentage(self):
        """Set loss acceptance treshold type to percentage.

        :returns: nothing
        """
        self._loss_acceptance_type = LossAcceptanceType.PERCENTAGE

    def set_loss_acceptance_type_frames(self):
        """Set loss acceptance treshold type to frames.

        :returns: nothing
        """
        self._loss_acceptance_type = LossAcceptanceType.FRAMES

    def loss_acceptance_type_is_percentage(self):
        """Return true if loss acceptance treshold type is percentage,
           false otherwise.

        :returns: True if loss acceptance treshold type is percentage.
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
        :raises: Exception if rate type is unknown
        """
        if rate_type not in RateType:
            raise Exception("rate_type unknown: {}".format(rate_type))
        else:
            self._rate_type = rate_type

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

        :param convergence: Treshold value number.
        :type convergence: float
        :returns: nothing
        """
        self._binary_convergence_threshold = float(convergence)

    def get_binary_convergence_threshold(self):
        """Get convergence for binary search.

        :returns: Treshold value number.
        :rtype: float
        """
        return self._binary_convergence_threshold

    def get_rate_type_str(self):
        """Return rate type representation.

        :returns: String representation of rate type.
        :rtype: str
        :raises: ValueError if rate type is unknown
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
        :returns: nothing
        :raises: ValueError if max attempts is lower than zero
        """
        if int(max_attempts) > 0:
            self._max_attempts = int(max_attempts)
        else:
            raise ValueError("Max attempt must by greater than zero")

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
        :raises: ValueError if search type is unknown
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
        :raises: ValueError if search result type is unknown
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
        :returns: nothing
        :raises: ValueError if start rate is not in range
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

        :returns: Result rate and latency stats.
        :rtype: tuple
        :raises: Exception if search failed
        """
        if self._search_result == SearchResults.FAILURE:
            raise Exception('Search FAILED')
        elif self._search_result in [SearchResults.SUCCESS,
                                     SearchResults.SUSPICIOUS]:
            return self._search_result_rate, self.get_latency()

    def binary_search(self, b_min, b_max, traffic_type, skip_max_rate=False,
                      skip_warmup=False):
        """Binary search of rate with loss below acceptance criteria.

        :param b_min: Min range rate.
        :param b_max: Max range rate.
        :param traffic_type: Traffic profile.
        :param skip_max_rate: Start with max rate first
        :param skip_warmup: Start TRex without warmup traffic if true.
        :type b_min: float
        :type b_max: float
        :type traffic_type: str
        :type skip_max_rate: bool
        :type skip_warmup: bool
        :returns: nothing
        :raises: ValueError if input values are not valid
        """

        if not self._rate_min <= float(b_min) <= self._rate_max:
            raise ValueError("Min rate is not in min,max range")
        if not self._rate_min <= float(b_max) <= self._rate_max:
            raise ValueError("Max rate is not in min,max range")
        if float(b_max) < float(b_min):
            raise ValueError("Min rate is greater than max rate")

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
            res.append(self.measure_loss(rate, self._frame_size,
                                         self._loss_acceptance,
                                         self._loss_acceptance_type,
                                         traffic_type, skip_warmup=skip_warmup))

        res = self._get_res_based_on_search_type(res)

        # loss occurred and it was above acceptance criteria
        if not res:
            self.binary_search(b_min, rate, traffic_type, True, True)
        # there was no loss / loss below acceptance criteria
        else:
            self._search_result_rate = rate
            self.binary_search(rate, b_max, traffic_type, True, True)

    def combined_search(self, start_rate, traffic_type):
        """Combined search of rate with loss below acceptance criteria.

        :param start_rate: Initial rate.
        :param traffic_type: Traffic profile.
        :type start_rate: float
        :type traffic_type: str
        :returns: nothing
        :raises: RuntimeError if linear search failed
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
        :returns: Returns True if num_a is close in value to num_b or equal.
                 False otherwise.
        :rtype: boolean
        :raises: ValueError if input values are not valid
        """

        if num_a == num_b:
            return True

        if rel_tol < 0.0 or abs_tol < 0.0:
            raise ValueError('Error tolerances must be non-negative')

        return abs(num_b - num_a) <= max(rel_tol * max(abs(num_a), abs(num_b)),
                                         abs_tol)


class ReceiveRateMeasurement(object):
    """Structure defining the result of single Rr measurement."""

    def __init__(self, duration, target_tr, transmit_count, drop_count):
        """Constructor, normalize primary and compute secondary quantities."""
        self.duration = float(duration)
        self.target_tr = float(target_tr)
        self.transmit_count = int(transmit_count)
        self.drop_count = int(drop_count)
        self.receive_count = transmit_count - drop_count
        self.transmit_rate = transmit_count / self.duration
        self.drop_rate = drop_count / self.duration
        self.receive_rate = self.receive_count / self.duration
        self.drop_fraction = float(self.drop_count) / self.transmit_count
        # TODO: Do we want to store also the real time (duration + overhead)?

    def __str__(self):
        """Return string reporting Rr."""
        return "d=" + str(self.duration) + ",Tr=" + str(self.target_tr) + ",Df=" + str(self.drop_fraction)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "ReceiveRateMeasurement(duration=" + repr(self.duration) + \
               ",target_tr=" + repr(self.target_tr) + \
               ",transmit_count=" + repr(self.transmit_count) + \
               ",drop_count=" + repr(self.drop_count) + ")"


class ReceiveRateInterval(object):
    """Structure defining two Rr measurements, presumably close to each other."""

    def __init__(self, measured_low, measured_high):
        """Constructor, store the measurement after checking argument types."""
        # TODO: Type checking is not very pythonic, perhaps users can fix wrong usage without it?
        if not isinstance(measured_low, ReceiveRateMeasurement):
            raise TypeError("measured_low is not a ReceiveRateMeasurement: " + repr(measured_low))
        if not isinstance(measured_high, ReceiveRateMeasurement):
            raise TypeError("measured_high is not a ReceiveRateMeasurement: " + repr(measured_high))
        self.measured_low = measured_low
        self.measured_high = measured_high
        self.sort()

    def sort(self):
        """Sort bounds by target Tr, compute secondary quantities."""
        if self.measured_low.target_tr > self.measured_high.target_tr:
            self.measured_low, self.measured_high = self.measured_high, self.measured_low
        self.abs_tr_width = self.measured_high.target_tr - self.measured_low.target_tr
        """Absolute width of target transmit rate. Upper minus lower."""
        self.rel_tr_width = self.abs_tr_width / self.measured_high.target_tr
        """Relative width of target transmit rate. Ansolute divided by upper."""

    def width_in_goals(self, relative_width_goal):
        """Return float value.

        Relative width goal is some (negative) value on logarithmic scale.
        Current relative width is another logarithmic value.
        Return the latter divided by the former.
        This is useful in finding out how did surprising widths come to existence."""
        return math.log(1.0 - self.rel_tr_width) / math.log(1.0 - relative_width_goal)

    def __str__(self):
        """Return string as half-open interval."""
        return "[" + str(self.measured_low) + ";" + str(self.measured_high) + ")"

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "ReceiveRateInterval(measured_low=" + repr(self.measured_low) + \
               ",measured_high=" + repr(self.measured_high) + ")"


class NdrPdrResult(object):
    """Two measurement intervals, return value of search algorithms.

    Partial fraction is NOT part of the result. Pdr interval should be valid
    for all partial fractions implied by the interval."""

    def __init__(self, ndr_interval, pdr_interval):
        """Constructor, store the measurement after checking argument types."""
        # TODO: Type checking is not very pythonic, perhaps users can fix wrong usage without it?
        if not isinstance(ndr_interval, ReceiveRateInterval):
            raise TypeError("ndr_interval, is not a ReceiveRateInterval: " + repr(ndr_interval))
        if not isinstance(pdr_interval, ReceiveRateInterval):
            raise TypeError("pdr_interval, is not a ReceiveRateInterval: " + repr(pdr_interval))
        self.ndr_interval = ndr_interval
        self.pdr_interval = pdr_interval

    def width_in_goals(self, relative_width_goal):
        """Return a debug string related to widths in logarithmic scale."""
        return (  "ndr " + str(self.ndr_interval.width_in_goals(relative_width_goal))
                + "; pdr " + str(self.pdr_interval.width_in_goals(relative_width_goal)))

    def __str__(self):
        """Return string as tuple of named values."""
        return "NDR=" + str(self.ndr_interval) + ";PDR=" + str(self.pdr_interval)

    def __repr__(self):
        """Return string evaluable as a constructor call."""
        return "NdrPdrResult(ndr_interval=" + repr(self.ndr_interval) + \
               ",pdr_interval=" + repr(self.pdr_interval) + ")"


class AbstractRateProvider(object):
    """Abstract class defining common API for rate providers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def measure(self, duration, transmit_rate):
        """Perform trial measurement and return ReceiveRateMeasurement."""
        pass


class AbstractSearchAlgorithm(object):
    """Abstract class defining common API for search algorithms."""

    __metaclass__ = ABCMeta

    def __init__(self, rate_provider):
        """Constructor, needs injected rate provider."""
        # TODO: Type check for AbstractRateProvider?
        self.rate_provider = rate_provider

    @abstractmethod
    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Return NdrPdrResult object with the narrow measured data."""
        # TODO: Do we agree on arguments related to precision or trial duration?
        pass


class OptimizedSearchAlgorithm(AbstractSearchAlgorithm):
    """Optimized binary search algorithm for finding NDR and PDR bounds.

    Traditional binary search algorithm needs initial interval (lower and upper bound),
    and returns final interval after bisecting (until some exit condition is met).
    The exit condition is usually related to the interval width,
    (upper bound value minus lower bound value).

    The optimized algorithm contains several improvements
    aimed to reduce overall search time.

    One improvement is searching for two intervals at once.
    The intervals are for NDR (No Drop Rate) and PDR (Partial Drop Rate).

    Next improvement is that the initial interval does need to be valid.
    Imagine initial interval (10, 11) where 11 is smaller than the searched value.
    The algorithm will try (11, 13) interval next, and if 13 is still smaller,
    (13, 17) and so on, doubling width until the upper bound is valid.
    The part when interval expands is called external search,
    the part when interval is bisected is called internal search.

    Next improvement is that trial measurements at small trial duration
    can be used to find a reasonable interval for full trial duration search.
    This results in more trials performed, but generally smaller overall duration.

    Next improvement is bisecting in logarithmic quantities,
    so that exit criteria can be independent of measurement units.

    Next improvement is basing the initial interval on receive rates.

    Final improvement is exiting early if the minimal value is not a valid lower bound.

    The complete search consist of several phases, each phase performing several trial measurements.
    Initial phase creates initial interval based on receive rates
    at maximum rate and at maximum receive rate (MRR).
    Final phase and preceding intermediate phases are performing external and internal search,
    each resulting interval is the starting point for the next phase.
    The resulting interval of final phase is the result of the whole algorithm.

    Each non-initial phase uses its own trial duration and width goal.
    Any non-initial phase stops searching (for NDR or PDR independently)
    when minimum is not a valid lower bound (at current duration),
    or all of the following is true:
    Both bounds are valid, bound bounds are measured at the current phase trial duration,
    interval width is less than the width goal for current phase."""

    class ProgressState(object):
        """Structure containing data to be passed around in recursion."""

        def __init__(self, result, phases, duration, width_goal, allowed_drop_fraction, fail_rate, line_rate):
            """Convert and store the argumeeeent values."""
            self.result = result
            """NdrPdrResult holding the current bounds."""
            self.phases = int(phases)
            """How many intermediate phases to execute before the current phase."""
            self.duration = float(duration)
            """Trial duration to be used at the current phase."""
            self.width_goal = float(width_goal)
            """Goal relative width for the current phase."""
            self.allowed_drop_fraction = float(allowed_drop_fraction)
            """Drop fraction allowed for the current PDR search."""
            self.fail_rate = float(fail_rate)
            """Hard minimum target transmit rate for the current search."""
            self.line_rate = float(line_rate)
            """Hard maximum target transmit rate for the current search."""

    def __init__(self, rate_provider, final_trial_duration=30.0, final_relative_width=0.005, intermediate_phases=2, initial_trial_duration=1.0):
        """Store rate provider and additional arguments."""
        super(OptimizedSearchAlgorithm, self).__init__(rate_provider)
        self.final_trial_duration = float(final_trial_duration)
        """Trial duration to be used in the final phase."""
        self.final_relative_width = float(final_relative_width)
        """Final lower bound transmit rate cannot be more distant that this multiple of upper bound."""
        self.intermediate_phases = int(intermediate_phases)
        """Number of intermediate phases to execute before the final phase."""
        self.initial_trial_duration = float(initial_trial_duration)
        """Trial duration to be used in the first intermediate phase."""

    def narrow_down_ndr_and_pdr(self, fail_rate, line_rate, allowed_drop_fraction):
        """Perform initial phase, create state object, proceed with non-initial phases."""
        fail_rate = float(fail_rate)
        line_rate = float(line_rate)
        allowed_drop_fraction = float(allowed_drop_fraction)
        line_measurement = self.rate_provider.measure(self.initial_trial_duration, line_rate)
        # 0.999 is to avoid rounding errors making the subsequent logic think the width is too broad.
        max_lo = max(fail_rate, line_rate * (1.0 - 0.999 * self.final_relative_width))
        mrr = min(max_lo, max(fail_rate, line_measurement.receive_rate))
        mrr_measurement = self.rate_provider.measure(self.initial_trial_duration, mrr)
        # Attempt to get narrower width.
        max2_lo = max(fail_rate, mrr * (1.0 - 0.999 * self.final_relative_width))
        mrr2 = min(max2_lo, mrr_measurement.receive_rate)
        if mrr2 > fail_rate:
            line_measurement = mrr_measurement
            mrr_measurement = self.rate_provider.measure(self.initial_trial_duration, mrr2)
        starting_interval = ReceiveRateInterval(mrr_measurement, line_measurement)
        starting_result = NdrPdrResult(starting_interval, starting_interval)
        state = self.ProgressState(starting_result, self.intermediate_phases,
                                   self.final_trial_duration, self.final_relative_width,
                                   allowed_drop_fraction, fail_rate, line_rate)
        state = self.ndrpdr(state)
        return state.result

    def _measure_and_update_state(self, state, transmit_rate):
        """Perform trial measurement, update bounds, return new state."""
        logging.info("result before update: %s", state.result)
        logging.debug("relative widths in goals: %s", state.result.width_in_goals(self.final_relative_width))
        measurement = self.rate_provider.measure(state.duration, transmit_rate)
        ndr_interval = self._new_interval(state.result.ndr_interval, measurement, 0.0)
        pdr_interval = self._new_interval(state.result.pdr_interval, measurement, state.allowed_drop_fraction)
        state.result = NdrPdrResult(ndr_interval, pdr_interval)
        return state

    def _new_interval(self, old_interval, measurement, allowed_drop_fraction):
        """Return new interval with bounds updated according to the measurement."""
        old_lo, old_hi = old_interval.measured_low, old_interval.measured_high
        # Priority zero: direct replace if the target Tr is the same.
        if measurement.target_tr in (old_lo.target_tr, old_hi.target_tr):
            if measurement.target_tr == old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_hi)
            else:
                return ReceiveRateInterval(old_lo, measurement)
        # Priority one: invalid lower bound allows only one type of update.
        if old_lo.drop_fraction > allowed_drop_fraction:
            # We can only expand down, old bound becomes valid upper one.
            if measurement.target_tr < old_lo.target_tr:
                return ReceiveRateInterval(measurement, old_lo)
            else:
                return old_interval
        # Lower bound is now valid.
        # Next priorities depend on target Tr.
        if measurement.target_tr < old_lo.target_tr:
            # Lower external measurement, relevant only if the new measurement has high drop rate.
            if measurement.drop_fraction > allowed_drop_fraction:
                # Returning the broader interval as old_lo would be invalid upper bound.
                return ReceiveRateInterval(measurement, old_hi)
        elif measurement.target_tr > old_hi.target_tr:
            # Upper external measurement, only relevant for invalid upper bound.
            if old_hi.drop_fraction <= allowed_drop_fraction:
                # Old upper bound becomes valid new lower bound.
                return ReceiveRateInterval(old_hi, measurement)
        else:
            # Internal measurement, replaced boundary depends on measured drop fraction.
            if measurement.drop_fraction > allowed_drop_fraction:
                # We have found a narrow valid interval,
                # regardless of whether old upper bound was valid.
                return ReceiveRateInterval(old_lo, measurement)
            else:
                # We do not want to shrink interval if upper bound is not valid.
                if old_hi.drop_fraction > allowed_drop_fraction:
                    return ReceiveRateInterval(measurement, old_hi)
        # Fallback, the interval is unchanged by the measurement.
        return old_interval

    @staticmethod
    def double_relative_width(relative_width):
        """Return relative width corresponding to double logarithmic width."""
        return 1.999 * relative_width - relative_width * relative_width
        # The number should be 2.0, but we want to avoid rounding errors,
        # and ensure half of double is not larger than the original value.

    @staticmethod
    def double_step_down(relative_width, current_bound):
        """Return rate of double logarithmic width below."""
        return current_bound * (1.0 - OptimizedSearchAlgorithm.double_relative_width(relative_width))

    @staticmethod
    def double_step_up(relative_width, current_bound):
        """Return rate of double logarithmic width above."""
        return current_bound / (1.0 - OptimizedSearchAlgorithm.double_relative_width(relative_width))

    @staticmethod
    def half_relative_width(relative_width):
        """Return relative width corresponding to half logarithmic width."""
        return 1.0 - math.sqrt(1.0 - relative_width)

    @staticmethod
    def half_step_up(relative_width, current_bound):
        """Return rate of half logarithmic width above."""
        return current_bound / (1.0 - OptimizedSearchAlgorithm.half_relative_width(relative_width))

    def ndrpdr(self, state):
        """Iterate to improve bounds. When width goal is met, return the new state."""
        if state.phases > 0:
            # We need to finish preceding intermediate phases first.
            saved_phases = state.phases
            state.phases -= 1
            # Preceding phases have shorter duration.
            saved_duration = state.duration
            duration_multiplier = state.duration / self.initial_trial_duration
            phase_exponent = float(state.phases) / saved_phases
            state.duration = self.initial_trial_duration * math.pow(duration_multiplier, phase_exponent)
            # Shorter durations do not need that narrow widths.
            saved_width = state.width_goal
            state.width_goal = self.double_relative_width(state.width_goal)
            # Recurse.
            state = self.ndrpdr(state)
            # Restore the state for current phase.
            state.duration = saved_duration
            state.width_goal = saved_width
            state.phases = saved_phases  # Not needed, but just in case.
        logging.info("starting iterations with duration %s and relative width goal %s", state.duration, state.width_goal)
        while 1:
            # Order of priorities: improper bounds (nl, pl, nh, ph), then narrowing relative Tr widths.
            # Durations are not priorities yet, they will settle on their own hopefully.
            ndr_lo = state.result.ndr_interval.measured_low
            ndr_hi = state.result.ndr_interval.measured_high
            pdr_lo = state.result.pdr_interval.measured_low
            pdr_hi = state.result.pdr_interval.measured_high
            ndr_rel_width = max(state.width_goal, state.result.ndr_interval.rel_tr_width)
            pdr_rel_width = max(state.width_goal, state.result.pdr_interval.rel_tr_width)
            # If we are hitting line or fail rate, we cannot shift, but we can re-measure.
            if ndr_lo.drop_fraction > 0.0:
                if ndr_lo.target_tr > state.fail_rate:
                    new_tr = max(state.fail_rate, self.double_step_down(ndr_rel_width, ndr_lo.target_tr))
                    logging.info("ndr lo external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif ndr_lo.duration < state.duration:
                    logging.info("ndr lo fail re-measure")
                    state = self._measure_and_update_state(state, state.fail_rate)
                    continue
            if pdr_lo.drop_fraction > state.allowed_drop_fraction:
                if pdr_lo.target_tr > state.fail_rate:
                    new_tr = max(state.fail_rate, self.double_step_down(pdr_rel_width, pdr_lo.target_tr))
                    logging.info("pdr lo external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif pdr_lo.duration < state.duration:
                    logging.info("pdr lo fail re-measure")
                    state = self._measure_and_update_state(state, state.fail_rate)
                    continue
            if ndr_hi.drop_fraction <= 0.0:
                if ndr_hi.target_tr < state.line_rate:
                    new_tr = max(state.fail_rate, self.double_step_up(ndr_rel_width, ndr_hi.target_tr))
                    logging.info("ndr hi external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif ndr_hi.duration < state.duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(state, state.line_rate)
                    continue
            if pdr_hi.drop_fraction <= state.allowed_drop_fraction:
                if pdr_hi.target_tr < state.line_rate:
                    new_tr = max(state.fail_rate, self.double_step_up(pdr_rel_width, pdr_hi.target_tr))
                    logging.info("pdr hi external %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                elif pdr_hi.duration < state.duration:
                    logging.info("ndr hi line re-measure")
                    state = self._measure_and_update_state(state, state.line_rate)
                    continue
            # If we are hitting line_rate, it is still worth narrowing width,
            # hoping large enough Df will happen.
            # But if we are hitting fail rate (at current duration), no additional measurement
            # will help with that, so we can stop narrowing in this phase.
            if ndr_lo.target_tr <= state.fail_rate and ndr_lo.drop_fraction > 0.0:
                ndr_rel_width = 0.0
            if pdr_lo.target_tr <= state.fail_rate and pdr_lo.drop_fraction > state.allowed_drop_fraction:
                pdr_rel_width = 0.0
            if max(ndr_rel_width, pdr_rel_width) > state.width_goal:
                # We have to narrow some width.
                if ndr_rel_width >= pdr_rel_width:
                    new_tr = self.half_step_up(ndr_rel_width, ndr_lo.target_tr)
                    logging.info("Bisecting for NDR at %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
                else:
                    new_tr = self.half_step_up(pdr_rel_width, pdr_lo.target_tr)
                    logging.info("Bisecting for PDR at %s", new_tr)
                    state = self._measure_and_update_state(state, new_tr)
                    continue
            # We do not need to improve width, but there still might be some measurements with smaller duration.
            # We need to re-measure with full duration, possibly creating invalid bounds to resolve (thus broadening width).
            if ndr_lo.duration < state.duration:
                logging.info("re-measuring NDR lower bound")
                self._measure_and_update_state(state, ndr_lo.target_tr)
                continue
            if pdr_lo.duration < state.duration:
                logging.info("re-measuring PDR lower bound")
                self._measure_and_update_state(state, pdr_lo.target_tr)
                continue
            # Except when lower bounds have high Df, in that case we do not need to re-measure _upper_ bounds.
            if ndr_hi.duration < state.duration and ndr_rel_width > 0.0:
                logging.info("re-measuring NDR upper bound")
                self._measure_and_update_state(state, ndr_hi.target_tr)
                continue
            if pdr_hi.duration < state.duration and pdr_rel_width > 0.0:
                logging.info("re-measuring PDR upper bound")
                self._measure_and_update_state(state, pdr_hi.target_tr)
                continue
            # Widths are narrow (or failing), bound measurements are long enough, we can return.
            logging.info("phase done")
            break
        return state

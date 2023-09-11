# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""Module defining MultipleLossRatioSearch class."""

from __future__ import annotations

import logging
import time

from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from .config import Config
from .discrete_interval import DiscreteInterval
from .discrete_load import DiscreteLoad
from .discrete_result import DiscreteResult
from .limit_handler import LimitHandler
from .load_candidate import LoadCandidate
from .load_rounding import LoadRounding
from .measurement_database import MeasurementDatabase
from .pep3140 import Pep3140Dict
from .search_goal import SearchGoal
from .strategy.selector import CandidateSelector
from .target_scaling import TargetScaling
from .target_spec import TargetSpec
from .trial_measurement import AbstractMeasurer


SECONDARY_FIELD = field(default=None, init=False, repr=False)
"""A shorthand for a frequently used value, a field not to be set in init."""


@dataclass
class MultipleLossRatioSearch:
    """Optimized binary search algorithm for finding conditional througputs.

    Traditional binary search algorithm needs initial interval
    (lower and upper bound), and returns final narrow bounds
    (related to its search goal) after bisecting
    (until some exit condition is met).
    The exit condition is usually related to the interval width,
    (upper bound tps value minus lower bound value).

    The optimized algorithm in this class contains several improvements
    aimed to reduce overall search time.

    One improvement is searching for bounds for multiple search goals at once.
    Specifically, the trial measurement results influence bounds for all goals,
    even though the selection of trial imputs for next measurement
    focused only on one goal (but the focus can switch between goal any time).

    Next improvement is that the "current" interval does not need to be valid
    (e.g. one of the bounds is missing).
    In that case, this algorithm will move and expand the interval,
    in a process called external search. Only when both bounds are found,
    the interval bisection (called internal search) starts making it narrow.

    Next improvement is that results of trial measurements
    with small trial duration can be used to find a reasonable starting interval
    for full trial duration search.
    This results in more trials performed, but smaller overall duration
    in general.
    Internally, such shorter trials come from "preceding targets",
    handles in a same way as a search goal "final target".

    Next improvement is bisecting in logarithmic quantities,
    so that target relative width is independent of measurement units.

    Next improvement is basing the initial interval on forwarding rates
    of few initial measurements, starting at max load and using forwarding rates
    seen so far.

    Final improvement is exiting early if the minimal load
    is not a valid lower bound (at final duration)
    and also exiting if the overall search duration is too long.

    FIXME below.
    The complete search consist of several phases,
    each phase performing several trial measurements.
    Initial phase creates initial interval based on forwarding rates
    at maximum rate and at maximum forwarding rate (MRR).
    Final phase and preceding intermediate phases are performing
    external and internal search steps,
    each resulting interval is the starting point for the next phase.
    The resulting intervals of final phase is the result of the whole algorithm.
    Smaller loss ratio goals are searched first (until relative width goal
    at final trial duration) before first intermediat phase
    starts for next loss ratio goal.

    Each non-initial phase uses its own trial duration.
    Any non-initial phase stops searching (for smallest ratio goal)
    when min load is not a valid lower bound (at current duration),
    or all of the following is true (for any ratio goal):
    Both bounds are valid, bounds are measured at the current phase
    trial duration (or longer), interval width is less than the width goal
    for the current phase.

    Note that bounds are not really hardwired to loss ratio goals.
    For each goal, the database of results is queried
    to find tightest bounds (if any).

    TODO: Review and update all terminology once it is frozen.
    """

    config: Config
    """Arguments required at construction time."""
    measurer: AbstractMeasurer = SECONDARY_FIELD
    """Measurer to use, set at calling search()."""
    debug: Callable[[str], None] = SECONDARY_FIELD
    """Object to call for logging, None means logging.debug."""
    rounding: LoadRounding = SECONDARY_FIELD
    """Derived from goals. Instance to use for intended load rounding."""
    from_float: Callable[[float], DiscreteLoad] = SECONDARY_FIELD
    """Conversion method from float [tps] load values."""
    limit_handler: LimitHandler = SECONDARY_FIELD
    """Derived. Load post-processing utility based on config and rounding."""
    scaling: TargetScaling = SECONDARY_FIELD
    """Derived. Utility for creating target chains for search goals."""
    database: MeasurementDatabase = SECONDARY_FIELD
    """Storage for (stats of) measurement results so far."""
    stop_time: float = SECONDARY_FIELD
    """Monotonic time value at which the search should end with failure."""

    def search(
        self,
        measurer: AbstractMeasurer,
        debug: Optional[Callable[[str], None]] = None,
    ) -> Pep3140Dict[SearchGoal, DiscreteInterval]:
        """Perform initial trials, create state object, proceed with main loop.

        Stateful arguments (measurer and debug) are stored.
        Derived objects are constructed from config.

        FIXME

        Note that the order of items in the result dict is affected by
        hashing for SearchGoalSet and does NOT match the iterable
        used to construct the set.

        :param measurer: Measurement provider to use by this search object.
        :param debug: Callable to optionally use instead of logging.debug().
        :returns: Structure containing narrowed down intervals
            and their measurements. The endpoints of the intervals
            are not just discrete loads, they are load stats trimmed
            to the final target.
            TODO: Add a specific class for trimmed stat intervals?
        :type measurer: AbstractMeasurer
        :type debug: Optional[Callable[[str], None]]
        :rtype: Pep3140Dict[SearchGoal, DiscreteInterval]
        :raises RuntimeError: If total duration is larger than timeout.
        """
        self.measurer = measurer
        self.debug = logging.debug if debug is None else debug
        self.rounding = LoadRounding(
            min_load=self.config.min_load,
            max_load=self.config.max_load,
            float_goals=[goal.relative_width for goal in self.config.goals],
        )
        self.from_float = DiscreteLoad.float_conver(rounding=self.rounding)
        self.limit_handler = LimitHandler(
            rounding=self.rounding,
            debug=self.debug,
        )
        self.scaling = TargetScaling(
            goals=self.config.goals,
            rounding=self.rounding,
        )
        self.database = MeasurementDatabase(self.scaling.targets)
        self.stop_time = time.monotonic() + self.config.search_duration_max
        result0, result1 = self.run_initial_trials()
        self.main_loop(result0.discrete_load, result1.discrete_load)
        ret_dict = Pep3140Dict()
        for goal in self.config.goals:
            target = self.scaling.goal_to_final_target[goal]
            interval = self.database.get_interval(target=target)
            ret_dict[goal] = interval
        return ret_dict

    def measure(self, duration: float, load: DiscreteLoad) -> DiscreteResult:
        """Call measurer and put the result to appropriate form in database.

        Also check the argument types and load roundness,
        and return the result to the caller.

        :param duration: Intended duration for the trial measurement.
        :param load: Intended load for the trial measurement:
        :type duration: float
        :type load: DiscreteLoad
        :returns: The trial results.
        :rtype: DiscreteResult
        """
        if not isinstance(duration, float):
            raise RuntimeError(f"Duration has to be float: {duration!r}")
        if not isinstance(load, DiscreteLoad):
            raise RuntimeError(f"Load has to be discrete: {load!r}")
        if not load.is_round:
            raise RuntimeError(f"Told to measure unrounded: {load!r}")
        self.debug(f"Measuring at d={duration},il={int(load)}")
        result = self.measurer.measure(
            intended_duration=duration,
            intended_load=float(load),
        )
        self.debug(f"Measured lr={result.loss_ratio}")
        result = DiscreteResult.with_load(result=result, load=load)
        self.database.add(result)
        return result

    def run_initial_trials(self) -> Tuple[DiscreteResult, DiscreteResult]:
        """Perform trials to get enough data to start the selectors.

        Measurements are done with all initial targets in mind,
        based on smallest target loss ratio, largest initial trial duration,
        and largest initial target width.

        Forwarding rate is used as a hint for next intended load,
        the relative quantity (as load can use different units).
        When the smallest target loss ratio is non-zero, a correction is needed
        (forwarding rate is only a good hint for zero loss ratio load).
        The correction is conservative (all increase in load turns to losses).

        Also, warmup trial is performed,
        all other trials are added to the database.

        This could return the initial width, but from implementation perspective
        it is easier to return two measurements (or the same one twice) here
        and compute width later.

        :returns: Two last measured value, in any order.
        :rtype: Tuple[DiscreteResult, DiscreteResult]
        """
        max_load = self.limit_handler.max_load
        ratio, duration, width = None, None, None
        for target in self.scaling.targets:
            if target.preceding:
                continue
            if ratio is None or ratio > target.loss_ratio:
                ratio = target.loss_ratio
            if not duration or duration < target.trial_duration:
                duration = target.trial_duration
            if not width or width < target.discrete_width:
                width = target.discrete_width
        self.debug(f"Init ratio {ratio} duration {duration} width {width}")
        if self.config.warmup_duration:
            self.debug("Warmup trial.")
            self.measure(self.config.warmup_duration, max_load)
            # Warmup should not affect the real results, reset the database.
            self.database = MeasurementDatabase(self.scaling.targets)
        self.debug(f"First trial at max rate: {max_load}")
        result0 = self.measure(duration, max_load)
        rfr = result0.relative_forwarding_rate
        corrected_rfr = (self.from_float(rfr) / (1.0 - ratio)).rounded_down()
        if corrected_rfr >= max_load:
            self.debug("Small loss, no other initial trials are needed.")
            return result0, result0
        mrr = self.limit_handler.handle(corrected_rfr, width, None, max_load)
        self.debug(f"Second trial at (corrected) mrr: {mrr}")
        result1 = self.measure(duration, mrr)
        # Attempt to get narrower width.
        result_ratio = result1.loss_ratio
        if result_ratio > ratio:
            rfr2 = result1.relative_forwarding_rate
            crfr2 = (self.from_float(rfr2) / (1.0 - ratio)).rounded_down()
            mrr2 = self.limit_handler.handle(crfr2, width, None, mrr)
        else:
            mrr2 = mrr + width
            mrr2 = self.limit_handler.handle(mrr2, width, mrr, max_load)
        if not mrr2:
            self.debug("Close enough, measuring at mrr2 is not needed.")
            return result0, result1
        self.debug(f"Third trial at (corrected) mrr2: {mrr2}")
        result2 = self.measure(duration, mrr2)
        return result1, result2

    def wrap_debug(self, target: TargetSpec) -> Callable[[str], None]:
        """Return new debug callable with info about which selector is calling.

        :param target: Which target is "current" for selector using the result.
        :type taregt: TargetSpec
        :return: New callable suitable to be injected as debug into a selector.
        :rtype: Callable[[str], None]
        """

        def wrapped_debug(text):
            """Call self debug with selector target info prepended.

            :param text: Message to log at debug level.
            :type text: str
            """
            self.debug(f"Target {target}: {text}")

        return wrapped_debug

    def main_loop(self, load0: DiscreteLoad, load1: DiscreteLoad) -> None:
        """Initialize selectors and keep measuring the winning candidate.

        The width for external search in initial targets is set
        to match the width from initial trials.

        The search ends when no selector nominates any candidate,
        or if the search takes too long.

        If a selector placed earlier in a sequence for a targets
        nominates a truthy candidate, later selectors are updated
        but their candidates are ignored.
        This makes search more stable when finding upper bounds.

        :param load0: Discrete load of one of results from run_initial_trials.
        :param load1: Discrete load of other of results from run_initial_trials.
        :type load0: DiscreteLoad
        :type load1: DiscreteLoad
        :type result_pair: Tuple[DiscreteResult, DiscreteResult]
        :raises RuntimeError: If the search takes too long.
        """
        if load1 < load0:
            load0, load1 = load1, load0
        selectors = []
        for target in self.scaling.goal_to_final_target.values():
            selector = CandidateSelector(
                final_target=target,
                initial_lower_load=load0,
                initial_upper_load=load1,
                database=self.database,
                handler=self.limit_handler,
                debug=self.wrap_debug(target),
            ).nomination_iterator()
            selectors.append(selector)
        while time.monotonic() < self.stop_time:
            winner = LoadCandidate(load=None, duration=None)
            for selector in selectors:
                winner = min(winner, next(selector))
            if not winner:
                break
            # We do not check duration versus stop_time here,
            # as some measurers can be unpredictably faster
            # than their intended duration suggests.
            self.measure(duration=winner.duration, load=winner.load)
        else:
            raise RuntimeError("Optimized search takes too long.")
        self.debug("Search done.")

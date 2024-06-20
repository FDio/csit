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

import logging
import time

from collections.abc import Generator
from dataclasses import dataclass
from types import coroutine
from typing import Callable, Optional, Tuple

from .candidate import Candidate
from .config import Config
from .dataclass import secondary_field
from .discrete_load import DiscreteLoad
from .discrete_result import DiscreteResult
from .expander import GlobalWidth
from .goal_result import GoalResult
from .limit_handler import LimitHandler
from .load_rounding import LoadRounding
from .measurement_database import MeasurementDatabase
from .pep3140 import Pep3140Dict
from .search_goal import SearchGoal
from .selector import Selector
from .target_scaling import TargetScaling
from .trial_measurement import AbstractMeasurer
from .trial_measurement import MeasurementResult as Result


@dataclass
class MultipleLossRatioSearch:
    """Implementation of the controller part of MLRsearch algorithm.

    The manager part is creating and calling this,
    the measurer part is injected.

    Traditional binary search algorithm needs initial interval
    (lower and upper bound), and returns final narrow bounds
    (related to its search goal) after bisecting
    (until some exit condition is met).
    The exit condition is usually related to the interval width,
    (upper bound value minus lower bound value).

    The optimized algorithm in this class contains several improvements
    aimed to reduce overall search time.

    One improvement is searching for bounds for multiple search goals at once.
    Specifically, the trial measurement results influence bounds for all goals,
    even though the selection of trial inputs for next measurement
    focuses only on one goal. The focus can switch between goals frequently.

    Next improvement is that results of trial measurements
    with small trial duration can be used to find a reasonable starting interval
    for full trial duration search.
    This results in more trials performed, but smaller overall duration
    in general.
    Internally, such shorter trials come from "preceding targets",
    handled in a same way as a search goal "final target".
    Related improvement is that the "current" interval does not need to be valid
    (e.g. one of the bounds is missing).
    In that case, this algorithm will move and expand the interval,
    in a process called external search. Only when both bounds are found,
    the interval bisection (called internal search) starts making it narrow.

    Next improvement is bisecting in logarithmic quantities,
    so that target relative width is independent of measurement units.

    Next improvement is basing the initial interval on forwarding rates
    of few initial measurements, starting at max load and using forwarding rates
    seen so far.

    Next improvement is to allow the use of multiple shorter trials
    instead one big trial, allowing a percentage of trials
    to exceed the loss ratio target.
    This makes the result more stable in practice.
    Conservative behavior (single long trial, zero exceed ratio)
    is still available using corresponding goal definitions.

    Final improvement is exiting early if the minimal load
    is not a valid lower bound (at final duration)
    and also exiting if the overall search duration is too long.

    There are also subtle optimizations related to candidate selection
    and uneven splitting of intervals, too numerous to list here.

    The return values describe performance at the relevant lower bound
    as "conditional throughput", which is based on loss ratio of one of trials
    selected as a quantile based on exceed ratio parameter.
    Usually this value may be quite pessimistic, as MLRsearch stops
    measuring a load as soon as it becomes a lower bound,
    so conditional throughput is usually based on forwarding rate
    of the worst on the good long trials.

    There are two entry points.
    Use "search" method when Measurer is a Python object.
    When "search_async" is called instead, it returns a coroutine.
    That coroutine yields a tuple of floats, values are duration and load
    for the next trial. Manager is supposed to perform the trial
    and send back the result as a MeasurementResult instance.
    Final search results are presented as value attribute of StopIteration.

    Methods on path of the yield are mostly defined as "async def",
    even though they are not intended to be run in an async framework.
    This is because the code with async/await is easier to read
    than generator-based "yield from" coroutines.
    """

    config: Config
    """Arguments required at construction time."""
    # End of fields required at instance creation.
    measurer: Optional[AbstractMeasurer] = secondary_field()
    """Measurer to use, set at calling search()."""
    debug: Callable[[str], None] = secondary_field()
    """Object to call for logging, None means logging.debug."""
    # End of fields required at search call.
    # Fields below are computed from data above
    rounding: LoadRounding = secondary_field()
    """Derived from goals. Instance to use for intended load rounding."""
    from_float: Callable[[float], DiscreteLoad] = secondary_field()
    """Conversion method from float [tps] intended load values."""
    limit_handler: LimitHandler = secondary_field()
    """Load post-processing utility based on config and rounding."""
    scaling: TargetScaling = secondary_field()
    """Utility for creating target chains for search goals."""
    database: MeasurementDatabase = secondary_field()
    """Storage for (stats of) measurement results so far."""
    stop_time: float = secondary_field()
    """Monotonic time value at which the search should end with failure."""

    def search(
        self,
        measurer: AbstractMeasurer,
        debug: Optional[Callable[[str], None]] = None,
    ) -> Pep3140Dict[SearchGoal, GoalResult]:
        """Perform initial trials, create state object, proceed with main loop.

        This is the intended entry point for sync mode,
        e.g. when measurer is provided as a Python object instance.

        :param measurer: Measurement provider to use by this search object.
        :param debug: Callable to optionally use instead of logging.debug().
        :type measurer: AbstractMeasurer
        :type debug: Optional[Callable[[str], None]]
        :returns: Structure containing conditional throughputs and other stats,
            one for each search goal. If a value is None it means there is
            no lower bound (min load turned out to be an upper bound).
        :rtype: Pep3140Dict[SearchGoal, GoalResult]
        :raises RuntimeError: If total duration is larger than timeout,
            or if min load becomes an upper bound for a search goal
            that has fail fast true.
            Also if configuration is found inconsistent.
        """
        if measurer is None:
            raise RuntimeError("Measurer cannot be None in sync search.")
        self.measurer = measurer
        search_coroutine = self.search_async(debug=debug)
        try:
            inputs = search_coroutine.send(None)
        except StopIteration as result:
            return result.value
        raise RuntimeError(f"Internal error, yield from sync search: {inputs=}")

    async def search_async(
        self,
        debug: Optional[Callable[[str], None]] = None,
    ) -> Generator[
        Tuple[float, float], Result, Pep3140Dict[SearchGoal, GoalResult]
    ]:
        """Perform initial trials, create state object, proceed with main loop.

        This is the intended entry point for async mode,
        e.g. when measurer is None and Manager is supposed to measure
        when duration and load is yielded to it.
        This allows the Manager-Measurer interaction to be coded
        in languages without support for Python objects.

        Stateful arguments (measurer and debug) are stored.
        Derived objects are constructed from config.

        In sync mode this acts like a normal function.
        In async mode this acts as a generator yielding to Manager.

        :param debug: Callable to optionally use instead of logging.debug().
        :type debug: Optional[Callable[[str], None]]
        :returns: Structure containing conditional throughputs and other stats,
            one for each search goal. If a value is None it means there is
            no lower bound (min load turned out to be an upper bound).
        :rtype: Pep3140Dict[SearchGoal, GoalResult]
        :raises RuntimeError: If total duration is larger than timeout,
            or if min load becomes an upper bound for a search goal
            that has fail fast true.
            Also if configuration is found inconsistent.
        """
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
        result0, result1 = await self._run_initial_trials()
        await self._main_loop(result0.discrete_load, result1.discrete_load)
        ret_dict = Pep3140Dict()
        for goal in self.config.goals:
            target = self.scaling.goal_to_final_target[goal]
            bounds = self.database.get_relevant_bounds(target=target)
            ret_dict[goal] = GoalResult.from_bounds(bounds=bounds)
        return ret_dict

    @coroutine
    def _measure_directly_or_indirectly(
        self, duration: float, load: float
    ) -> Generator[Tuple[float, float], Result, Result]:
        """If measurer is set, call it. Otherwise yield to Manager.

        If measurer is not set, this yields two floats (duration and load).
        In that case, Manager is supposed to call Measurer
        and send back the trial result.

        This cannot be "async def", as those native coroutines
        are not allowed to both yield and return.

        :param duration: Intended duration for the trial measurement.
        :param load: Intended load for the trial measurement.
        :type duration: float
        :type load: float
        :returns: The trial result, perhaps sent from Manager.
        :rtype: Generator[Tuple[float, float], Result, Result]
        """
        if self.measurer is not None:
            self.debug(f"Calling Measurer: d={duration},il={int(load)}")
            return self.measurer.measure(
                intended_duration=duration,
                intended_load=load,
            )
        self.debug(f"Yielding to Manager d={duration},il={int(load)}")
        result = yield (duration, load)
        return result

    async def _measure(
        self, duration: float, load: DiscreteLoad
    ) -> DiscreteResult:
        """Call measurer and put the result to appropriate form in database.

        Also check the argument types and load roundness,
        and return the result to the caller.

        In sync mode this acts like a normal function.
        In async mode this acts as a generator yielding to Manager.

        :param duration: Intended duration for the trial measurement.
        :param load: Intended load for the trial measurement.
        :type duration: float
        :type load: DiscreteLoad
        :returns: The trial results.
        :rtype: DiscreteResult
        :raises RuntimeError: If an argument doed not have the required type.
        """
        if not isinstance(duration, float):
            raise RuntimeError(f"Duration has to be float: {duration!r}")
        if not isinstance(load, DiscreteLoad):
            raise RuntimeError(f"Load has to be discrete: {load!r}")
        if not load.is_round:
            raise RuntimeError(f"Told to measure unrounded: {load!r}")
        result = await self._measure_directly_or_indirectly(
            duration=duration, load=float(load)
        )
        self.debug(f"Measured lr={result.loss_ratio}")
        result = DiscreteResult.with_load(result=result, load=load)
        self.database.add(result)
        return result

    async def _run_initial_trials(
        self,
    ) -> Tuple[DiscreteResult, DiscreteResult]:
        """Perform trials to get enough data to start the selectors.

        Measurements are done with all initial targets in mind,
        based on smallest target loss ratio, largest initial trial duration,
        and largest initial target width.

        Forwarding rate is used as a hint for next intended load.
        The relative quantity is used, as load can use different units.
        When the smallest target loss ratio is non-zero, a correction is needed
        (forwarding rate is only a good hint for zero loss ratio load).
        The correction is conservative (all increase in load turns to losses).

        Also, warmup trial (if configured) is performed,
        all other trials are added to the database.

        This could return the initial width, but from implementation perspective
        it is easier to return two measurements (or the same one twice) here
        and compute width later. The "one value twice" happens when max load
        has small loss, or when min load has big loss.

        In sync mode this acts like a normal function.
        In async mode this acts as a generator yielding to Manager.

        :returns: Two last measured values, in any order. Or one value twice.
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
            await self._measure(self.config.warmup_duration, max_load)
            # Warmup should not affect the real results, reset the database.
            self.database = MeasurementDatabase(self.scaling.targets)
        self.debug(f"First trial at max rate: {max_load}")
        result0 = await self._measure(duration, max_load)
        rfr = result0.relative_forwarding_rate
        corrected_rfr = (self.from_float(rfr) / (1.0 - ratio)).rounded_down()
        if corrected_rfr >= max_load:
            self.debug("Small loss, no other initial trials are needed.")
            return result0, result0
        mrr = self.limit_handler.handle(corrected_rfr, width, None, max_load)
        self.debug(f"Second trial at (corrected) mrr: {mrr}")
        result1 = await self._measure(duration, mrr)
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
            return result1, result1
        self.debug(f"Third trial at (corrected) mrr2: {mrr2}")
        result2 = await self._measure(duration, mrr2)
        return result1, result2

    async def _main_loop(
        self, load0: DiscreteLoad, load1: DiscreteLoad
    ) -> None:
        """Initialize selectors and keep measuring the winning candidate.

        Selectors are created, the two input loads are useful starting points.

        The search ends when no selector nominates any candidate,
        or if the search takes too long (or if a selector raises).

        Winner is selected according to ordering defined in Candidate class.
        In case of a tie, selectors for earlier goals are preferred.

        As a selector is only allowed to update current width as the winner,
        the update is done here explicitly.

        In sync mode this acts like a normal function.
        In async mode this acts as a generator yielding to Manager.

        :param load0: Discrete load of one of results from _run_initial_trials.
        :param load1: Discrete load of other of results from _run_initial_trials.
        :type load0: DiscreteLoad
        :type load1: DiscreteLoad
        :raises RuntimeError: If the search takes too long,
            or if min load becomes an upper bound for any search goal
        """
        if load1 < load0:
            load0, load1 = load1, load0
        global_width = GlobalWidth.from_loads(load0, load1)
        selectors = []
        for target in self.scaling.goal_to_final_target.values():
            selector = Selector(
                final_target=target,
                global_width=global_width,
                initial_lower_load=load0,
                initial_upper_load=load1,
                database=self.database,
                handler=self.limit_handler,
                debug=self.debug,
            )
            selectors.append(selector)
        while time.monotonic() < self.stop_time:
            winner = Candidate()
            for selector in selectors:
                # Order of arguments is important
                # when two targets nominate the same candidate.
                winner = min(Candidate.nomination_from(selector), winner)
            if not winner:
                break
            # We do not check duration versus stop_time here,
            # as some measurers can be unpredictably faster
            # than their intended duration suggests.
            await self._measure(duration=winner.duration, load=winner.load)
            # Delayed updates.
            if winner.width:
                global_width.width = winner.width
            winner.won()
        else:
            raise RuntimeError("Optimized search takes too long.")
        self.debug("Search done.")

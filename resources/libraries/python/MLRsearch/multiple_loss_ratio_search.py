# Copyright (c) 2022 Cisco and/or its affiliates.
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
from typing import Callable, Dict, Optional

from .config import Config
from .criterion import Criterion
from .discrete_interval import DiscreteInterval
from .discrete_load import DiscreteLoad
from .limit_handler import LimitHandler
from .load_candidate import LoadCandidate
from .load_rounding import LoadRounding
from .measurement_database import MeasurementDatabase
from .target_scaling import TargetScaling
from .target_tracker import TargetTracker
from .trial_measurement.abstract_measurer import AbstractMeasurer
from .trial_measurement.measurement_result import MeasurementResult


SECONDARY_FIELD = field(default=None, init=False, repr=False)
"""A shorthand for a frequently used value, a field not to be set in init."""


@dataclass
class MultipleLossRatioSearch:
    """Optimized binary search algorithm for finding bounds for multiple ratios.

    Traditional binary search algorithm needs initial interval
    (lower and upper bound), and returns final narrow interval
    (related to its loss ratio goal) after bisecting
    (until some exit condition is met).
    The exit condition is usually related to the interval width,
    (upper bound value minus lower bound value).

    This optimized algorithm contains several improvements
    aimed to reduce overall search time.

    One improvement is searching for intervals for multiple loss goals at once.
    Specifically, the intervals are found in sequence (one call), but previous
    trial measutrement results are re-used when searching for next interval.

    Next improvement is that the "initial" interval does not need to be valid
    (e.g. one of the "bounds" does not have correct loss ratio).
    In that case, this algorithm will move and expand the interval,
    in a process called external search. Only when both bound become valid,
    the interval bisection (called internal search) starts making it narrow.

    Next improvement is that results of trial measurements
    with small trial duration can be used to find a reasonable interval
    for full trial duration search.
    This results in more trials performed, but smaller overall duration
    in general.

    Next improvement is bisecting in logarithmic quantities,
    so that exit criterion (relative width) is independent of measurement units.

    Next improvement is basing the initial interval on forwarding rates
    of few initial measurements, starting at max load.

    Final improvement is exiting early if the minimal load
    is not a valid lower bound (at final duration)
    and also exiting if the overall search duration is too long.

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

    TODO: Review and update this docstring according to IETF draft.
    """

    config: Config
    """Arguments required at construction time."""
    measurer: AbstractMeasurer = SECONDARY_FIELD
    """Measurer to use, set at calling search()."""
    debug: Callable[[str], None] = SECONDARY_FIELD
    """Object to call for logging, None means logging.debug."""
    rounding: LoadRounding = SECONDARY_FIELD
    """Instance to use for intended load rounding."""
    from_float: Callable[[float], DiscreteLoad] = SECONDARY_FIELD
    """Conversion method from float [tps] load values."""
    limit_handler: LimitHandler = SECONDARY_FIELD
    """FIXME"""
    scaling: TargetScaling = SECONDARY_FIELD
    """FIXME"""
    database: MeasurementDatabase = SECONDARY_FIELD
    """Storage for measurement results so far."""
    stop_time: float = SECONDARY_FIELD
    """Monotonic time value at which the search should end with failure."""

    def search(
        self,
        measurer: AbstractMeasurer,
        debug: Optional[Callable[[str], None]] = None,
    ) -> Dict[Criterion, DiscreteInterval]:
        """Perform initial phase, create state object, proceed with next phases.

        Stateful arguments (measurer and debug) are stored.
        Derived objects are constructed from config.

        :param measurer: Rate provider to use by this search object.
        :param debug: Callable to optionally use instead of logging.debug().
        :returns: Structure containing narrowed down intervals
            and their measurements.
        :type measurer: AbstractMeasurer
        :type debug: Optional[Callable[[str], None]]
        :rtype: List[DiscreteInterval]
        :raises RuntimeError: If total duration is larger than timeout.
        """
        self.measurer = measurer
        self.debug = logging.debug if debug is None else debug
        self.rounding = LoadRounding(
            min_load=self.config.min_load,
            max_load=self.config.max_load,
            float_goals=[crit.relative_width for crit in self.config.criteria],
        )
        self.from_float = DiscreteLoad.float_conver(rounding=self.rounding)
        self.limit_handler = LimitHandler(
            rounding=self.rounding,
            debug=self.debug,
        )
        self.scaling = TargetScaling(
            criteria=self.config.criteria,
            rounding=self.rounding,
        )
        self.database = MeasurementDatabase(self.scaling.specs)
        self.stop_time = time.monotonic() + self.config.search_duration_max
        self.do_initial_measurements()
        self.ndrpdr_main_loop()
        ret_dict = dict()
        for criterion in self.config.criteria:
            target_spec = self.scaling.criterion_to_spec[criterion]
            interval = self.database.get_interval(target_spec=target_spec)
            # TODO: Interval end should have stat only for criterion target,
            # not all targets as currently.
            ret_dict[criterion] = interval
        return ret_dict

    def measure(self, duration: float, load: DiscreteLoad) -> MeasurementResult:
        """Call measurer and cast the result to be comparable.

        FIXME
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
        # TODO: Create a subclass for MLR-specific result.
        result.discrete_load = load
        self.database.add(result)
        return result

    def do_initial_measurements(self):
        """Perform measurements to get enough data for full logic.

        Measurements are done with first intermediate phase in mind,
        so initial duration is used, and width goal (for phase 0)
        for first ratio is used to avoid wastefully narrow intervals.

        Forwarding rate is used as a hint for next intended load,
        the relative quantity in case load has different units.
        When the first ratio is non-zero, a correction is needed
        (forwarding rate is only a good hint for zero ratio).
        The correction is conservative (all increase in load turns to losses).

        :returns: Measurement results to consider next.
        :rtype: List[ComparableMeasurementResult]
        """
        max_load = self.limit_handler.max_load
        spec = self.scaling.specs[0]
        ratio = spec.loss_ratio
        duration = spec.single_duration_whole
        width = spec.discrete_width
        self.debug(f"Init ratio {ratio} duration {duration} width {width}")
        if self.config.warmup_duration:
            self.debug("Warmup trial.")
            self.measure(self.config.warmup_duration, max_load)
            # Warmup should not affect the real results, reset the database.
            self.database = MeasurementDatabase(self.scaling.specs)
        self.debug(f"First measurement at max rate: {max_load}")
        result = self.measure(duration, max_load)
        rfr = result.relative_forwarding_rate
        corrected_rfr = (self.from_float(rfr) / (1.0 - ratio)).rounded_down()
        if corrected_rfr >= max_load:
            self.debug("Small loss, no other initial measurements are needed.")
            return
        mrr = self.limit_handler.handle(corrected_rfr, width, None, max_load)
        if not mrr:
            self.debug("Warning: limits too close or goal too wide?")
            return
        self.debug(f"Second measurement at (corrected) mrr: {mrr}")
        result = self.measure(duration, mrr)
        # Attempt to get narrower width.
        result_ratio = result.loss_ratio
        if result_ratio > ratio:
            rfr2 = result.relative_forwarding_rate
            crfr2 = (self.from_float(rfr2) / (1.0 - ratio)).rounded_down()
            mrr2 = self.limit_handler.handle(crfr2, width, None, mrr)
        else:
            mrr2 = mrr + width
            mrr2 = self.limit_handler.handle(mrr2, width, mrr, max_load)
        if not mrr2:
            self.debug("Close enough, measuring at mrr2 is not needed.")
            return
        self.debug(f"Third measurement at (corrected) mrr2: {mrr2}")
        self.measure(duration, mrr2)

    def wrap_debug(self, spec):
        """FIXME"""

        def wrapped_debug(text):
            """FIXME"""
            self.debug(f"Tracker {spec}: {text}")

        return wrapped_debug

    def ndrpdr_main_loop(self) -> None:
        """Search for narrow enough bounds for this ratio at this phase."""
        trackers = list()
        for spec in self.scaling.specs:
            trackers.append(
                TargetTracker(
                    target_spec=spec,
                    database=self.database,
                    handler=self.limit_handler,
                    debug=self.wrap_debug(spec),
                )
            )
        measured = None
        while time.monotonic() < self.stop_time:
            winner = LoadCandidate(load=None, duration=None)
            for tracker in trackers:
                candi = tracker.candidate_after(measured)
                if candi < winner:
                    winner = candi
            if not winner:
                break
            # We have a new intended load to measure with.
            # We do not check duration versus stop_time here,
            # as some measurers can be unpredictably faster
            # than their intended duration suggests.
            measured = self.measure(duration=winner.duration, load=winner.load)
        else:
            # Time is up.
            raise RuntimeError("Optimized search takes too long.")
        self.debug("Search done.")

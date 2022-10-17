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

import logging
import time

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Union

from .config import Config
from .criterion import Criterion
from .discrete_load import DiscreteLoad
from .discrete_width import DiscreteWidth
from .discrete_interval import DiscreteInterval
from .duration_and_width_scaling import DurationAndWidthScaling
from .load_rounding import LoadRounding
from .load_stat import LoadStat
from .measurement_database import MeasurementDatabase
from .relevant_bounds import RelevantBounds
from .selection_info import SelectionInfo
from .trial_measurement.abstract_measurer import AbstractMeasurer
from .trial_measurement.measurement_result import MeasurementResult


SECONDARY_FIELD = field(default=None, init=False, repr=False)
"""A shorthand for a frequently used value, a field not to be set in init."""

MaybeLoad = Union[None, DiscreteLoad, LoadStat]


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
    from_int: Callable[[int], DiscreteLoad] = SECONDARY_FIELD
    """Conversion method from int load values."""
    from_float: Callable[[float], DiscreteLoad] = SECONDARY_FIELD
    """Conversion method from float [tps] load values."""
    discrete_min_load: DiscreteLoad = SECONDARY_FIELD
    """Min load converted to discrete load."""
    discrete_max_load: DiscreteLoad = SECONDARY_FIELD
    """Max load converted to discrete load."""
    scaling: Dict[Criterion, DurationAndWidthScaling] = SECONDARY_FIELD
    """Scaling to use with corresponding target loss ratio."""
    stop_time: float = SECONDARY_FIELD
    """Monotonic time value at which the search should end with failure."""
    database: MeasurementDatabase = SECONDARY_FIELD
    """Storage for measurement results so far."""

    def search(
        self,
        measurer: AbstractMeasurer,
        debug: Optional[Callable[[str], None]] = None,
    ) -> List[DiscreteInterval]:
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
        self.from_int = DiscreteLoad.int_conver(self.rounding)
        self.from_float = DiscreteLoad.float_conver(self.rounding)
        self.discrete_min_load = self.from_float(self.config.min_load)
        self.discrete_max_load = self.from_float(self.config.max_load)
        self.scaling = dict()
        for criterion in self.config.criteria:
            self.scaling[criterion] = DurationAndWidthScaling(
                criterion=criterion,
                rounding=self.rounding,
            )
        self.stop_time = time.monotonic() + self.config.max_search_duration
        self.database = None  # Initialized via the next line.
        self.do_initial_measurements()
        self.ndrpdr_root()
        return self.database.get_intervals()

    def measure(
        self,
        duration: float,
        load: DiscreteLoad,
        criterion: Criterion,
    ) -> List[MeasurementResult]:
        """Call measurer and cast the result to be comparable.

        :param duration: Trial duration [s].
        :param int_load: Intended load (transactions to attempt).
        :type duration: float
        :type intended_load: DiscreteLoad
        :returns: Structure detailing the result of the measurement.
        :rtype: comparable_measurement_result.ComparableMeasurementResult
        :raises RuntimeError: If a wrong argument type is detected.
        """
        if not isinstance(duration, float):
            raise RuntimeError(f"Duration has to be float: {duration!r}")
        if not isinstance(load, DiscreteLoad):
            raise RuntimeError(f"Load has to be discrete: {load!r}")
        if not load.is_round:
            raise RuntimeError(f"Told to measure unrounded: {load_stat!r}")
        min_duration = min(duration, self.config.single_trial_duration)
        load_stat = self.database.stat_for(load, min_duration)
        ret_list = list()
        while not load_stat.determined(criterion, duration):
            result = self.measurer.measure(
                intended_duration=load_stat.intended_duration,
                intended_load=float(load_stat),
            )
            ret_list.append(result)
            load_stat.add(result)
            self.debug(f"Updated stat: {load_stat}")
        self.debug(u"Enough trials for this stat.")
        self.database.update(load_stat)
        return ret_list

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
        max_load = self.discrete_max_load
        criterion = self.config.criteria.criteria[0]
        ratio = criterion.loss_ratio
        duration = self.scaling[criterion].duration(phase=0)
        width_goal = self.scaling[criterion].width_goal(phase=0)
        self.debug(f"Init ratio {ratio} duration {duration} width {width_goal}")
        if self.config.warmup_duration:
            self.debug(u"Warmup trial.")
            self.database = MeasurementDatabase(self.config.criteria)
            self.measure(self.config.warmup_duration, max_load, criterion)
        self.database = MeasurementDatabase(self.config.criteria)
        self.debug(f"First measurement at max rate: {max_load}")
        results = self.measure(duration, max_load, criterion)
        rfr = min(result.relative_forwarding_rate for result in results)
        corrected_rfr = self.from_float(rfr) / (1.0 - ratio)
        if corrected_rfr >= max_load:
            self.debug("Small loss, no other initial measurements are needed.")
            return
        mrr = self.handle_load_limits(corrected_rfr, width_goal, None, max_load)
        if not mrr:
            self.debug("Warning: limits too close or goal too wide?")
            return
        self.debug(f"Second measurement at (corrected) mrr: {mrr}")
        results = self.measure(duration, mrr, criterion)
        # Attempt to get narrower width.
        result_ratio = max(result.loss_ratio for result in results)
        if result_ratio > ratio:
            rfr2 = min(result.relative_forwarding_rate for result in results)
            crfr2 = self.from_float(rfr2) / (1.0 - ratio)
            mrr2 = self.handle_load_limits(crfr2, width_goal, None, mrr)
        else:
            mrr2 = mrr + width_goal
            mrr2 = self.handle_load_limits(mrr2, width_goal, mrr, max_load)
        if not mrr2:
            self.debug("Good mrr, measuring at mrr2 is not needed.")
            return
        self.debug(f"Third measurement at (corrected) mrr2: {mrr2}")
        self.measure(duration, mrr2, criterion)

    def ndrpdr_root(self) -> None:
        """Iterate search over ratios and phases.

        :raises RuntimeError: If total duration is larger than timeout.
        """
        for criterion in self.config.criteria:
            self.debug(f"Focusing on criterion {criterion} now.")
            for phase in range(criterion.intermediate_phases + 1):
                self.ndrpdr_iteration(criterion, phase)
        self.debug("All criteria done.")

    def ndrpdr_iteration(self, criterion: Criterion, phase: int) -> None:
        """Search for narrow enough bounds for this ratio at this phase.

        :param ratio: Target loss ratio the bounds should encompass.
        :param phase: Current phase number, implies duration and width goal.
        :type ratio: float
        :type phase: int
        """
        scaling = self.scaling[criterion]
        width_goal = scaling.width_goal(phase)
        current_duration = scaling.duration(phase)
        previous_duration = scaling.duration(phase - 1) if phase else None
        self.debug(
            f"Starting phase for criterion {criterion}"
            f" with duration {current_duration}"
            f" and relative width goal {width_goal}."
        )
        selection = SelectionInfo(halve=True, remeasure=True)
        while time.monotonic() < self.stop_time:
            bounds = RelevantBounds.from_database(
                self.database, criterion, current_duration, previous_duration
            )
            selection = self.select_load(
                bounds, width_goal, criterion, selection
            )
            load = selection.load
            if selection.handle:
                load = self.handle_load_limits(
                    load, width_goal, bounds.clo1, bounds.chi1
                )
            if not load:
                self.debug("Phase done.")
                break
            # We have a new intended load to measure with.
            # We do not check duration versus stop_time here,
            # as some measurers can be unpredictably faster
            # than their intended duration suggests.
            self.measure(current_duration, load, criterion)
        else:
            # Time is up.
            raise RuntimeError("Optimized search takes too long.")

    def handle_load_limits(
        self,
        load: MaybeLoad,
        width_goal: DiscreteWidth,
        clo: MaybeLoad,
        chi: MaybeLoad,
    ) -> Optional[MaybeLoad]:
        """Return new intended load after considering limits and bounds.

        Not only we want to avoid measuring outside minmax interval,
        we also want to avoid measuring too close to known limits and bounds.
        We either round or return None, depending on hints from bound loads.

        When rounding away from hard limits, we may end up being
        too close to an already measured bound.
        In this case, pick a midpoint between the bound and the limit.
        The caller should have chosen (unrounded) load far enough from bounds.

        The last two arguments are just loads (not full measurement result)
        to allow callers to exclude some load without measuring them.
        As a convenience, full results are also supported,
        so that callers do not need to care about None when extracting load.

        :param load: Intended load candidate from select_load.
        :param width_goal: Relative width goal, considered narrow enough.
        :param clo: Intended load of current tightest lower bound.
        :param chi: Intended load of current tightest upper bound.
        :type load: Optional[DiscreteLoad]
        :type width_goal: DiscreteWidth
        :type clo: Optional[Union[DiscreteLoad, ComparableMeasurementResult]]
        :type chi: Optional[Union[DiscreteLoad, ComparableMeasurementResult]]
        :return: Adjusted load to measure at, or None if narrow enough.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If unsupported corner case is detected.
        """
        if not load:
            raise RuntimeError("Got None load to handle.")
        if not load.is_round:
            load = DiscreteLoad(rounding=load.rounding, int_load=int(load))
        min_load, max_load = self.discrete_min_load, self.discrete_max_load
        if not clo and not chi:
            load = self._handle_load_with_excludes(
                load, width_goal, min_load, max_load, min_ex=False, max_ex=False
            )
            return load
        if not clo:
            if chi <= min_load:
                # Expected when hitting the min load.
                return None
            if load >= chi:
                raise RuntimeError("Lower load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, min_load, chi, min_ex=False, max_ex=True
            )
            return load
        if not chi:
            if clo >= max_load:
                # Expected when hitting the max load.
                return None
            if load <= clo:
                raise RuntimeError("Higher load expected.")
            load = self._handle_load_with_excludes(
                load, width_goal, clo, max_load, min_ex=True, max_ex=False
            )
            return load
        if load <= clo:
            raise RuntimeError("Higher load expected.")
        if load >= chi:
            raise RuntimeError("Lower load expected.")
        load = self._handle_load_with_excludes(
            load, width_goal, clo, chi, min_ex=True, max_ex=True
        )
        return load

    def _handle_load_with_excludes(
        self,
        load: DiscreteLoad,
        width_goal: DiscreteWidth,
        minimum: DiscreteLoad,
        maximum: DiscreteLoad,
        min_ex: bool,
        max_ex: bool,
    ) -> Optional[DiscreteLoad]:
        """Round load if too close to limits, respecting exclusions.

        Here, round means first rounding to int value (see DiscreteLoad),
        then avoiding getting too close (less than width goal)
        to maximum or minimum.

        This is a reusable block.
        Limits may come from previous bounds or from hard load limits.
        When coming from bounds, rounding to that is not allowed.
        When coming from hard limits, rounding to the limit value
        is allowed in general (given by the setting the _ex flag).

        :param load: The candidate intended load before accounting for limits.
        :param width_goal: Relative width of area around the limits to avoid.
        :param minimum: The lower limit to round around.
        :param maximum: The upper limit to round around.
        :param min_ex: If false, rounding to the minimum is allowed.
        :param max_ex: If false, rounding to the maximum is allowed.
        :type load: DiscreteLoad
        :type width_goal: DiscreteWidth
        :type minimum: DiscreteLoad
        :type maximum: DiscreteLoad
        :type min_ex: bool
        :type max_ex: bool
        :returns: Adjusted load value, or None if narrow enough.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If internal inconsistency is detected.
        """
        load = self.from_int(int(load))
        if not minimum <= load <= maximum:
            raise RuntimeError("Please do not call with irrelevant load.")
        width = maximum - minimum
        if width_goal >= width:
            self.debug("Warning: Handling called with wide goal.")
            if not min_ex:
                self.debug("Minimum not excluded, rounding to it.")
                return minimum
            if not max_ex:
                self.debug("Maximum not excluded, rounding to it.")
                return maximum
            self.debug("Both limits excluded, narrow enough.")
            return None
        soft_min = minimum + width_goal
        soft_max = maximum - width_goal
        if soft_min > soft_max:
            self.debug("Whole interval is less than two goals.")
            middle = DiscreteInterval(minimum, maximum).middle(width_goal)
            soft_min = soft_max = middle
        if load < soft_min:
            if min_ex:
                self.debug("Min excluded, rounding to soft min.")
                return soft_min
            self.debug("Min not excluded, rounding to minimum.")
            return minimum
        if load > soft_max:
            if max_ex:
                self.debug("Max excluded, rounding to soft max.")
                return soft_max
            self.debug("Max not excluded, rounding to maximum.")
            return maximum
        # Far enough from limits, no additional rounding is needed.
        return load

    def select_load(
        self,
        bounds: RelevantBounds,
        width_goal: DiscreteWidth,
        criterion: Criterion,
        selection: SelectionInfo,
    ) -> SelectionInfo:
        """Return updated selection info with new load to measure at.

        Returning None load means either we have narrow enough valid interval
        for this phase, or we are hitting some other early return condition,
        (e.g. hitting min load or max load).

        Situations related to min and max load are expected in measurement
        results, but load candidates are not constrained here,
        so the handling can be centralized elsewhere.

        Note that the special re-measurements for hitting min or max load
        are unconditional (but they still disable further re-measurements).

        The implementation moves most of the logic to sub-methods.
        They also do most of logging, unless they lack the required context.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Relative width goal, considered narrow enough.
        :param selection: Object containing flags controlling one-time actions.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :type selection: SelectionInfo
        :returns: The next load rate to measure at, None to end phase;
            whether the load should be limit handled, whether to halve
            or remeasure next.
        :rtype: SelectionInfo
        :raises RuntimeError: If internal logic error is detected.
        """
        if load := self._min_remea_load(bounds):
            return SelectionInfo(load=load)
        if load := self._max_remea_load(bounds):
            return SelectionInfo(load=load)
        if selection.halve:
            if load := self._halving_load(bounds, width_goal):
                return SelectionInfo(load=load, remeasure=selection.remeasure)
        if selection.remeasure:
            # Previous ratio could have left interval too narrow for halving.
            # Allow two re-measurements in those cases.
            # This is case one, when one bound is alread remeasured
            # (e.g. from previous ratio search).
            if load := self._lo_remea_load(bounds, width_goal):
                return SelectionInfo(load=load, remeasure=selection.halve)
            if load := self._hi_remea_load(bounds, width_goal):
                return SelectionInfo(load=load)
        if not bounds.clo1:
            if load := self._extend_down(bounds, width_goal, criterion):
                self.debug(f"No current lower bound, extending down: {load}")
                return SelectionInfo(load=load, handle=True)
            # Hitting min load.
            return SelectionInfo(load=None)
        if not bounds.chi1:
            load = self._extend_up(bounds, width_goal, criterion)
            return SelectionInfo(load=load, handle=load is not None)
        if not (bisect_load := self._bisect(bounds, width_goal)):
            return SelectionInfo(load=None)
        if not bounds.chi2:
            self.debug(f"Not extending down, so doing bisect: {bisect_load}")
            return SelectionInfo(load=bisect_load)
        # Not hitting min load, so extend_load cannot be None.
        if (
            extend_load := self._extend_down(bounds, width_goal, criterion)
        ) > bisect_load:
            # This can happen when:
            # Previous ratio ended up way below these (chi1) loads,
            # and current ratio phase-2 wandered here,
            # and phase-1 did not move much,
            # and current phase failed lowerbound re-measurement.
            self.debug(f"Preferring to extend down: {extend_load}.")
            return SelectionInfo(load=extend_load, handle=True)
        # There is no realistic scenario where extending up from clo1 is good.
        self.debug(f"Preferring to bisect: {bisect_load}.")
        return SelectionInfo(load=bisect_load)

    def _min_remea_load(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Return None, or min load remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :type bounds: RelevantBounds
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if bounds.phi1:
            if (load := self.discrete_min_load) == bounds.phi1:
                self.debug(f"Min load remeasurement available: {load}")
                return load
        return None

    def _max_remea_load(self, bounds: RelevantBounds) -> Optional[DiscreteLoad]:
        """Return None, or max load remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :type bounds: RelevantBounds
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if bounds.plo1:
            if (load := self.discrete_max_load) == bounds.plo1:
                self.debug(f"Max load remeasurement available: {load}")
                return load
        return None

    def _halving_load(
        self, bounds: RelevantBounds, width_goal: DiscreteWidth
    ) -> Optional[DiscreteLoad]:
        """Return None, or load for phase halving when detected.

        There is some overlap with last bisect, but we want to select
        the same load in both cases, regardless of tightest bounds duration.

        The decision is made based purely on interval width.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :returns: Intended load for halving, or None if this is not halving.
        :rtype: Optional[DiscreteLoad]
        """
        tlo, thi = bounds.clo1, bounds.chi1
        # Use plo1 if tighter.
        if bounds.plo1 and (not tlo or tlo < bounds.plo1):
            tlo = bounds.plo1
        # Use phi1 if tighter.
        if bounds.phi1 and (not thi or thi > bounds.phi1):
            thi = bounds.phi1
        if not tlo or not thi:
            return None
        interval = DiscreteInterval(tlo, thi)
        wig = interval.width_in_goals(width_goal)
        if wig > 2.0:
            return None
        if wig > 1.0:
            load = interval.middle(width_goal)
            self.debug(f"Halving available: {load}")
            return load
        if not bounds.clo1 and not bounds.chi1:
            self.debug("Warning: too narrow to halve, trigger re-measurement.")
            # This is case two, when both bounds need re-measurement.
            # Caller will allow a second re-measurement as this mimics halving.
            return tlo
        return None

    def _lo_remea_load(
        self, bounds: RelevantBounds, width_goal: DiscreteWidth
    ) -> Optional[DiscreteLoad]:
        """Return None, or load for lowerbound remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if not bounds.plo1 or not bounds.chi1:
            return None
        if bounds.clo1:
            interval = DiscreteInterval(bounds.clo1, bounds.chi1)
            if interval.width_in_goals(width_goal) <= 1.0:
                self.debug("Not re-measuring low when narrow alrady.")
                return None
        interval = DiscreteInterval(bounds.plo1, bounds.chi1)
        if interval.width_in_goals(width_goal) > 1.0:
            # The previous phase tightest bound would not be this far.
            return None
        load = bounds.plo1
        self.debug(f"Lowerbound re-measurement available: {load}")
        return load

    def _hi_remea_load(
        self, bounds: RelevantBounds, width_goal: DiscreteWidth
    ) -> Optional[DiscreteLoad]:
        """Return None, or load for upperbound remeasurement when detected.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :returns: Intended load for remeasurement, or None if this is not it.
        :rtype: Optional[DiscreteLoad]
        """
        if not bounds.phi1 or not bounds.clo1:
            return None
        if bounds.chi1:
            interval = DiscreteInterval(bounds.clo1, bounds.chi1)
            if interval.width_in_goals(width_goal) <= 1.0:
                self.debug("Not re-measureng high when narrow alrady.")
                return None
        interval = DiscreteInterval(bounds.clo1, bounds.phi1)
        if interval.width_in_goals(width_goal) > 1.0:
            # The previous phase tightest bound would not be this far.
            return None
        load = bounds.phi1
        self.debug(f"Upperbound remeasurement available: {load}")
        return load

    def _extend_down(
        self,
        bounds: RelevantBounds,
        width_goal: DiscreteWidth,
        criterion: Criterion,
    ) -> Optional[DiscreteLoad]:
        """Return extended width below.

        The only case when this returns None is when hitting min load already.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if bounds.chi1 <= self.discrete_min_load:
            self.debug("Hitting min load, exit early.")
            return None
        if not bounds.chi2:
            if bounds.chi1 < self.discrete_max_load:
                raise RuntimeError(f"Extending down without chi2: {bounds!r}")
            load = bounds.chi1 - width_goal
            self.debug(f"Max load re-measured high, extending down: {load}")
            return load
        # Old (phi1) values are not reliable enough to slow down the expansion.
        old_width = DiscreteInterval(bounds.chi1, bounds.chi2).discrete_width
        # Some width mismatch is expected, only one half is aligned to goal.
        old_width = max(old_width, width_goal)
        new_width = old_width * criterion.expansion_coefficient
        load = bounds.chi1 - new_width
        # Not emitting a comment to debug here, caller knows two cases.
        return load

    def _extend_up(
        self,
        bounds: RelevantBounds,
        width_goal: DiscreteWidth,
        criterion: Criterion,
    ) -> Optional[DiscreteLoad]:
        """Return extended width above.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        if bounds.clo1 >= self.discrete_max_load:
            self.debug("Hitting max rate, we can exit.")
            return None
        if not bounds.clo2:
            if bounds.clo1 > self.discrete_min_load:
                raise RuntimeError(f"Extending up without clo2: {bounds!r}")
            load = bounds.clo1 + width_goal
            self.debug(f"Min load re-measured low, extending down: {load}")
            return load
        # Old (plo1) values are not reliable enough to slow down the expansion.
        old_width = DiscreteInterval(bounds.clo2, bounds.clo1).discrete_width
        # Some width mismatch is expected, only one half is aligned to goal.
        old_width = max(old_width, width_goal)
        new_width = old_width * criterion.expansion_coefficient
        load = bounds.clo1 + new_width
        self.debug(f"No current upper bound, extending up: {load}")
        return load

    def _bisect(
        self, bounds: RelevantBounds, width_goal: DiscreteWidth
    ) -> Optional[DiscreteLoad]:
        """Return middle rate or None if width is narrow enough.

        :param bounds: Relevant bounds obtained from database.
        :param width_goal: Width goal for the current phase.
        :type bounds: RelevantBounds
        :type width_goal: DiscreteWidth
        :returns: Intended load candidate for the next trial measurement.
        :rtype: Optional[DiscreteLoad]
        :raises RuntimeError: If algorithm inconsistency is detected.
        """
        interval = DiscreteInterval(bounds.clo1, bounds.chi1)
        if (goals := interval.width_in_goals(width_goal)) <= 1.0:
            self.debug(f"Width {goals} goals small enough, phase can end now.")
            return None
        load = interval.middle(width_goal)
        # Not emitting a comment to debug here, caller knows two cases.
        return load

# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Library with keyword performing performance search."""

import math
import time

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from .MLRsearch.MultipleLossRatioSearch import MultipleLossRatioSearch
from .PLRsearch.PLRsearch import PLRsearch
from .model.ExportLog import export_mlrsearch_debug, export_plrsearch_by_level
from .robot_interaction import get_library_instance

__all__ = [u"SearchAlgorithms"]

class SearchAlgorithms:
    """Class to be imported as Robot Library, containing search keywords.

    Aside of setting up measurer and forwarding arguments,
    the main business is to adapt default arguments to test type.
    """

    @staticmethod
    def perform_ndrpdr_search(
        frame_size,
        traffic_profile,
        minimum_transmit_rate,
        maximum_transmit_rate,
        packet_loss_ratio=0.005,
        final_relative_width=0.005,
        final_trial_duration=30.0,
        initial_trial_duration=1.0,
        number_of_intermediate_phases=2,
        timeout=720.0,
        ppta=1,
        resetter=None,
        traffic_directions=2,
        transaction_duration=0.0,
        transaction_scale=0,
        transaction_type=u"packet",
        use_latency=False,
        ramp_up_rate=None,
        ramp_up_duration=None,
        state_timeout=300.0,
        expansion_coefficient=4.0,
    ):
        """Setup initialized TG, perform optimized search, return intervals.

        If transaction_scale is nonzero, all init and non-init trial durations
        are set to 1.0 (as they do not affect the real trial duration)
        and zero intermediate phases are used.
        This way no re-measurement happens.
        Warmup has to be handled via resetter or ramp-up mechanisms.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :param minimum_transmit_rate: Minimal load in transactions per second.
        :param maximum_transmit_rate: Maximal load in transactions per second.
        :param packet_loss_ratio: Ratio of packets lost, for PDR [1].
        :param final_relative_width: Final lower bound transmit rate
            cannot be more distant that this multiple of upper bound [1].
        :param final_trial_duration: Trial duration for the final phase [s].
        :param initial_trial_duration: Trial duration for the initial phase
            and also for the first intermediate phase [s].
        :param number_of_intermediate_phases: Number of intermediate phases
            to perform before the final phase [1].
        :param timeout: The search will fail itself when not finished
            before this overall time [s].
        :param ppta: Packets per transaction, aggregated over directions.
            Needed for udp_pps which does not have a good transaction counter,
            so we need to compute expected number of packets.
            Default: 1.
        :param resetter: Callable to reset DUT state for repeated trials.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param transaction_duration: Total expected time to close transaction.
        :param transaction_scale: Number of transactions to perform.
            0 (default) means unlimited.
        :param transaction_type: An identifier specifying which counters
            and formulas to use when computing attempted and failed
            transactions. Default: "packet".
        :param use_latency: Whether to measure latency during the trial.
            Default: False.
        :param ramp_up_rate: Rate to use in ramp-up trials [pps].
        :param ramp_up_duration: Duration of ramp-up trials [s].
        :param state_timeout: Time of life of DUT state [s].
        :param expansion_coefficient: In external search multiply width by this.
        :type frame_size: str or int
        :type traffic_profile: str
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type packet_loss_ratio: float
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type ppta: int
        :type resetter: Optional[Callable[[], None]]
        :type traffic_directions: int
        :type transaction_duration: float
        :type transaction_scale: int
        :type transaction_type: str
        :type use_latency: bool
        :type ramp_up_rate: float
        :type ramp_up_duration: float
        :type state_timeout: float
        :type expansion_coefficient: float
        :returns: Structure containing narrowed down NDR and PDR intervals
            and their measurements.
        :rtype: List[Receiverateinterval]
        :raises RuntimeError: If total duration is larger than timeout.
        """
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        # Overrides for fixed transaction amount.
        # TODO: Move to robot code? We have two call sites, so this saves space,
        #       even though this is surprising for log readers.
        if transaction_scale:
            initial_trial_duration = 1.0
            final_trial_duration = 1.0
            number_of_intermediate_phases = 0
            timeout += transaction_scale * 3e-4
        tg_instance.set_rate_provider_defaults(
            frame_size=frame_size,
            traffic_profile=traffic_profile,
            sleep_till_duration=False,
            ppta=ppta,
            resetter=resetter,
            traffic_directions=traffic_directions,
            transaction_duration=transaction_duration,
            transaction_scale=transaction_scale,
            transaction_type=transaction_type,
            use_latency=use_latency,
            ramp_up_rate=ramp_up_rate,
            ramp_up_duration=ramp_up_duration,
            state_timeout=state_timeout,
        )
        algorithm = MultipleLossRatioSearch(
            measurer=tg_instance,
            final_trial_duration=final_trial_duration,
            final_relative_width=final_relative_width,
            number_of_intermediate_phases=number_of_intermediate_phases,
            initial_trial_duration=initial_trial_duration,
            timeout=timeout,
            debug=export_mlrsearch_debug,
            expansion_coefficient=expansion_coefficient,
        )
        if packet_loss_ratio:
            packet_loss_ratios = [0.0, packet_loss_ratio]
        else:
            # Happens in reconf tests.
            packet_loss_ratios = [packet_loss_ratio]
        results = algorithm.narrow_down_intervals(
            min_rate=minimum_transmit_rate,
            max_rate=maximum_transmit_rate,
            packet_loss_ratios=packet_loss_ratios,
        )
        return results

    @staticmethod
    def perform_soak_search(
        frame_size,
        traffic_profile,
        minimum_transmit_rate,
        maximum_transmit_rate,
        plr_target=1e-7,
        tdpt=0.1,
        initial_count=50,
        timeout=7200.0,
        ppta=1,
        resetter=None,
        trace_enabled=False,
        traffic_directions=2,
        transaction_duration=0.0,
        transaction_scale=0,
        transaction_type=u"packet",
        use_latency=False,
        ramp_up_rate=None,
        ramp_up_duration=None,
        state_timeout=300.0,
    ):
        """Setup initialized TG, perform soak search, return avg and stdev.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :param minimum_transmit_rate: Minimal load in transactions per second.
        :param maximum_transmit_rate: Maximal load in transactions per second.
        :param plr_target: Ratio of packets lost to achieve [1].
        :param tdpt: Trial duration per trial.
            The algorithm linearly increases trial duration with trial number,
            this is the increment between succesive trials, in seconds.
        :param initial_count: Offset to apply before the first trial.
            For example initial_count=50 makes first trial to be 51*tdpt long.
            This is needed because initial "search" phase of integrator
            takes significant time even without any trial results.
        :param timeout: The search will stop after this overall time [s].
        :param ppta: Packets per transaction, aggregated over directions.
            Needed for udp_pps which does not have a good transaction counter,
            so we need to compute expected number of packets.
            Default: 1.
        :param resetter: Callable to reset DUT state for repeated trials.
        :param trace_enabled: True if trace enabled else False.
            This is very verbose tracing on numeric computations,
            do not use in production.
            Default: False
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param transaction_duration: Total expected time to close transaction.
        :param transaction_scale: Number of transactions to perform.
            0 (default) means unlimited.
        :param transaction_type: An identifier specifying which counters
            and formulas to use when computing attempted and failed
            transactions. Default: "packet".
        :param use_latency: Whether to measure latency during the trial.
            Default: False.
        :param ramp_up_rate: Rate to use in ramp-up trials [pps].
        :param ramp_up_duration: Duration of ramp-up trials [s].
        :param state_timeout: Time of life of DUT state [s].
        :type frame_size: str or int
        :type traffic_profile: str
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type plr_target: float
        :type initial_count: int
        :type timeout: float
        :type ppta: int
        :type resetter: Optional[Callable[[], None]]
        :type trace_enabled: bool
        :type traffic_directions: int
        :type transaction_duration: float
        :type transaction_scale: int
        :type transaction_type: str
        :type use_latency: bool
        :type ramp_up_rate: float
        :type ramp_up_duration: float
        :type state_timeout: float
        :returns: Average and stdev of estimated aggregate rate giving PLR.
        :rtype: 2-tuple of float
        """
        tg_instance = get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        # Overrides for fixed transaction amount.
        # TODO: Move to robot code? We have a single call site
        #       but MLRsearch has two and we want the two to be used similarly.
        if transaction_scale:
            # TODO: What is a good value for max scale?
            # TODO: Scale the timeout with transaction scale.
            timeout = 7200.0
        tg_instance.set_rate_provider_defaults(
            frame_size=frame_size,
            traffic_profile=traffic_profile,
            negative_loss=False,
            sleep_till_duration=True,
            ppta=ppta,
            resetter=resetter,
            traffic_directions=traffic_directions,
            transaction_duration=transaction_duration,
            transaction_scale=transaction_scale,
            transaction_type=transaction_type,
            use_latency=use_latency,
            ramp_up_rate=ramp_up_rate,
            ramp_up_duration=ramp_up_duration,
            state_timeout=state_timeout,
        )
        logger_trace = lambda msg: export_plrsearch_by_level(u"TRACE", msg)
        logger_trace = logger_trace if trace_enabled else None
        algorithm = PLRsearch(
            measurer=tg_instance,
            trial_duration_per_trial=tdpt,
            packet_loss_ratio_target=plr_target,
            trial_number_offset=initial_count,
            timeout=timeout,
            logger_error=lambda msg: export_plrsearch_by_level(u"ERROR", msg),
            logger_info=lambda msg: export_plrsearch_by_level(u"INFO", msg),
            logger_debug=lambda msg: export_plrsearch_by_level(u"DEBUG", msg),
            logger_trace=logger_trace,
        )
        result = algorithm.search(
            min_rate=minimum_transmit_rate,
            max_rate=maximum_transmit_rate,
        )
        return result

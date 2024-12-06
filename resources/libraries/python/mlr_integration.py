# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Utility functions for integrating standalone MLR library with CSIT."""

from typing import Tuple, Union

from robot.api import logger

from .MLRsearch import (
    Config,
    GoalResult,
    MeasurementResult,
    MultipleLossRatioSearch,
    SearchGoal,
)


class MlrSearch:
    """Class to be imported as Robot Library, containing search keywords.

    Main keywords rely on async mode of MLRsearch and are Measurer agnostic.
    Conversion keywords are added to suport specific traffic providers.
    """

    def __init__(self):
        """FIXME"""
        self.generator = None
        self.goals = []
        self.duration = None
        self.load = None

    def set_goals_for_search(
        self,
        min_load: float,
        max_load: float,
        loss_ratio: float = 0.005,
        relative_width: float = 0.005,
        initial_trial_duration: float = 1.0,
        final_trial_duration: float = 1.0,
        duration_sum: float = 21.0,
        expansion_coefficient: int = 2,
        preceding_targets: int = 2,
        search_duration_max: float = 1200.0,
    ) -> None:
        """
        FIXME
        """
        loss_ratios = [0.0, loss_ratio]
        exceed_ratio = 0.5
        self.goals = [
            SearchGoal(
                loss_ratio=loss_ratio,
                exceed_ratio=exceed_ratio,
                relative_width=relative_width,
                initial_trial_duration=initial_trial_duration,
                final_trial_duration=final_trial_duration,
                duration_sum=duration_sum,
                preceding_targets=preceding_targets,
                expansion_coefficient=expansion_coefficient,
                fail_fast=True,
            )
            for loss_ratio in loss_ratios
        ]
        config = Config()
        config.goals = self.goals
        config.min_load = min_load
        config.max_load = max_load
        config.search_duration_max = search_duration_max
        config.warmup_duration = 1.0
        algorithm = MultipleLossRatioSearch(config)
        self.generator = algorithm.search_async(debug=logger.debug)

    def iterate_search(
        self, trial_result: MeasurementResult
    ) -> Union[Tuple[Tuple[float, float], None], Tuple[None, Tuple[GoalResult, ...]]]:
        """FIXME"""
        if not self.generator:
            raise RuntimeError("No active search goals.")
        try:
            self.duration, self.load = self.generator.send(trial_result)
            return ((self.duration, self.load), None)
        except StopIteration as stop_info:
            mapping = stop_info.value
            results = [mapping[goal] for goal in self.goals]
            # self.__init__()
            return (None, tuple(results))

    def iperf_result_into_measurement(
        self, sec: float, mbps: float
    ) -> MeasurementResult:
        """FIXME"""
        return MeasurementResult(
            intended_duration=self.duration,
            intended_load=self.load,
            # TODO: Distinguish unsent and lost data.
            offered_count=self.duration * self.load,
            forwarding_count=sec * mbps,
            offered_duration=sec,
            # intended_count=self.duration * self.load,
        )

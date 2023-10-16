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

import dataclasses
import logging
import sys

#from KeyboardMeasurer import KeyboardMeasurer as measurer
#from RandomMeasurer import RandomMeasurer as measurer
#from PromilesMeasurer import PromilesMeasurer as measurer
#from SingleLossMeasurer import SingleLossMeasurer as measurer
#from TwoPhaseMeasurer import TwoPhaseMeasurer as measurer
from StretchMeasurer import StretchMeasurer as measurer
#from ReplayMeasurer import ReplayMeasurer as measurer
from LoggingMeasurer import LoggingMeasurer as infologging
from TimeTrackingMeasurer import TimeTrackingMeasurer as tracking

logging.basicConfig(level=getattr(logging, "DEBUG"))

# 0.75 is not a good value for twophase, but it found a bug, and it is good for singleloss.
#p = tracking(infologging(measurer()), overhead=0.0)
p = tracking(infologging(measurer(offsets={30.0: 1e6}, mrr=1e8, spread=5e6)))

print(u"optimized search, stretch measurer, printing")

from resources.libraries.python.MLRsearch import (
    MultipleLossRatioSearch as my_search, Config, SearchGoal
)
goals = list()
goals.append(SearchGoal(
    loss_ratio=0.0,
    exceed_ratio=0.5,
    relative_width=5e-3,
    initial_trial_duration=1.0,
    final_trial_duration=1.0,
    duration_sum=20.0,
    preceding_targets=2,
    expansion_coefficient=2,
))
goals.append(SearchGoal(
    loss_ratio=5e-3,
    exceed_ratio=0.5,
    relative_width=5e-3,
    initial_trial_duration=1.0,
    final_trial_duration=1.0,
    duration_sum=20.0,
    preceding_targets=2,
    expansion_coefficient=2,
))
#goals.append(SearchGoal(
#    loss_ratio=0.0,
#    exceed_ratio=0.0,
#    relative_width=1e-2,
#    initial_trial_duration=2.0,
#    final_trial_duration=5.0,
#    duration_sum=11.0,
#    preceding_targets=1,
#    expansion_coefficient=8,
#))
#goals.append(SearchGoal(
#    loss_ratio=0.0,
#    exceed_ratio=0.8,
#    relative_width=3e-3,
#    initial_trial_duration=1.0,
#    final_trial_duration=3.5,
#    duration_sum=61.0,
#    preceding_targets=2,
#    expansion_coefficient=4,
#))
#goals.append(SearchGoal(
#    loss_ratio=0.005,
#    exceed_ratio=0.1,
#    relative_width=1e-3,
#    initial_trial_duration=1.6,
#    final_trial_duration=8.0,
#    duration_sum=31.0,
#    preceding_targets=3,
#    expansion_coefficient=2,
#))
config = Config()
config.min_load = 9001.0
config.max_load = 28812908.182865925
config.goals = goals
config.warmup_duration = 1.0
algo = my_search(config)

print(f"config: {config}", flush=True)
result = algo.search(measurer=p)

print(f"result string: {result}")
for key, value in result.items():
    print(f"Conditional throughput {value.conditional_throughput!r} for goal {key}")
print(f"search took {p.total_time} seconds {p.measurements} measurements")
p.reset()

print("\n".join([module.__name__ for module in sys.modules.values() if module and module.__name__.startswith("resources.libraries.python.MLRsearch")]))

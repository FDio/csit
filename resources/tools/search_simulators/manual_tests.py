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
from LoggingMeasurer import LoggingMeasurer as infologging
from TimeTrackingMeasurer import TimeTrackingMeasurer as tracking

logging.basicConfig(level=getattr(logging, "DEBUG"))

# 0.75 is not a good value for twophase, but it found a bug, and it is good for singleloss.
p = tracking(infologging(measurer(offsets={30.0: 1e6}, mrr=1e8, spread=5e6)))

print(u"optimized search, stretch measurer, printing")

from resources.libraries.python.MLRsearch import (
    MultipleLossRatioSearch as my_search, Config, Criteria, Criterion
)
criteria = list()
criteria.append(Criterion(
    loss_ratio=0.0,
    exceed_ratio=0.0,
    relative_width=1e-2,
    single_duration_min=2.0,
    single_duration_max=5.0,
    sum_duration_min=11.0,
    intermediate_phases=1,
    expansion_coefficient=8,
))
criteria.append(Criterion(
    loss_ratio=0.0,
    exceed_ratio=0.8,
    relative_width=3e-3,
    single_duration_min=1.0,
    single_duration_max=3.5,
    sum_duration_min=61.0,
    intermediate_phases=2,
    expansion_coefficient=4,
))
criteria.append(Criterion(
    loss_ratio=0.005,
    exceed_ratio=0.1,
    relative_width=1e-3,
    single_duration_min=1.6,
    single_duration_max=8.0,
    sum_duration_min=31.0,
    intermediate_phases=3,
    expansion_coefficient=2,
))
config = Config()
config.min_load = 1e4
config.max_load = 1e9
config.criteria = Criteria(criteria)
algo = my_search(config)

print(f"config: {config}", flush=True)
result = algo.search(measurer=p)

print(f"result string: {result}")
#print(f"RW: NDR {result[crit_ndr].relative_width} PDR {result[crit_pdr].relative_width}")
print(f"search took {p.total_time} seconds {p.measurements} measurements")
p.reset()

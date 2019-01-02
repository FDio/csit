# Copyright (c) 2018 Cisco and/or its affiliates.
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

import math
import logging
import sys

from resources.libraries.python.MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement
from SoakMeasurer import SoakMeasurer as measurer
from PLRsearch import PLRsearch as search

logging.basicConfig(level=getattr(logging, "DEBUG"))

tuple_list = [
    (7445476.0, 7594313, 19864),
    (14880952.0, 15476044, 954883),
    (13962656.204, 14800278, 2426),
    (13960239.1319, 15076920, 37854),
]

print "soak compute, record measurer, non-printing"

p = measurer(7000000, 1000, 1, fast=False)
s = search(p, 0.2, 1e-7, 50, 36000)

trial_result_list = list()
#integrator_data = ([0.0, 0.0], [0.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0]])
integrator_data = ([0.0, 0.0], [0.029603742390783033, 0.02395773062443863], [[1.0, 0.0], [0.0, 1.0]], [[3.355809404422938, 0.0011789148354524992], [0.0011789148354524992, 3.367370292932736]])
for count, (rate, tx, lx) in enumerate(tuple_list):
    if count in (1,):
        result = s.measure_and_compute(7.0, 1e6, trial_result_list, 2.0*14880952, integrator_data)
        _, _, _, stretch, erf, integrator_data = result
        print "    stretch", stretch, "erf", erf
        print "integrator_data", repr(integrator_data)
    if count == 4:
        break
    rate *= 2
    duration = tx / rate
    measurement = ReceiveRateMeasurement(duration, rate, tx, lx)
    print "measurement", repr(measurement)
    trial_result_list.append(measurement)

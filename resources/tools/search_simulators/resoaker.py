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
    (7445476.0, 151887638, 197667, 10.2),
    (14880952.0, 309523674, 19399793, 10.4),
    (13948264.9044, 295703102, 113254, 10.6),
    (13942918.7528, 301166916, 75572, 10.8),
    (6517599.43803, 143387121, 17108, 11.0),
]

print "soak compute, record measurer, non-printing"

p = measurer(7000000, 1000, 1, fast=False)
s = search(p, 0.2, 1e-7, 50, 36000)

trial_result_list = list()
#integrator_data = ([0.0, 0.0], [0.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0]])
integrator_data = ([0.0, 0.0], [-0.3661988424244604, 0.7939183861669961], [[1.0, 0.0], [0.0, 1.0]], [[1.593264164980923e-08, -1.7825226924472367e-08], [-1.7825226924472367e-08, 2.1650976474784577e-08]])
for count, (rate, tx, lx, duration) in enumerate(tuple_list):
    if count in (4,):
        result = s.measure_and_compute(7.0, 1e6, trial_result_list, 2.0*14880952, integrator_data)
        _, _, _, stretch, erf, integrator_data = result
        print "    stretch", stretch, "erf", erf
        print "integrator_data", repr(integrator_data)
    if count == 5:
        break
    rate *= 2
    measurement = ReceiveRateMeasurement(duration, rate, tx, lx)
    print "measurement", repr(measurement)
    trial_result_list.append(measurement)

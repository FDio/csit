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
from stat_trackers import VectorStatTracker

logging.basicConfig(level=getattr(logging, "DEBUG"))

tuple_list = [
    (7445476.0, 151887638, 0, 0.2*51, 6210),
    (14880952.0, 309523655, 106336357, 0.2*52, 7757),
    (9768621.07302, 207094672, 460980, 0.2*53, 11705),
    (9746873.23884, 210532365, 765972, 0.2*54, 13057),
    (9606072.59491, 211333503, 2207292, 0.2*55, 14153),
    (8896393.78789, 199279136, 0, 0.2*56, 14606),
    (8444539.46302, 192535419, 0, 0.2*57, 13946),
    (7043723.85427, 163414323, 0, 0.2*58, 15006),
    (8440580.67985, 199197622, 0, 0.2*59, 15086),
    (7073231.62109, 169757488, 0, 0.2*60, 13563),
    (8440973.85148, 205959680, 0, 0.2*61, 14640),
]

print "soak compute, record measurer, non-printing"

p = measurer(7000000, 1000, 1, fast=False)
s = search(p, 0.2, 1e-7, 50, 36000, trace_enabled=True)

trial_result_list = list()
list_integrator_data = (
    (None, None, None, None),
    ([0.0, 0.0], [-0.01425912328672453, 0.004743736408224265], [[1.0, 0.0], [0.0, 1.0]], [[3.294252996489952, 0.04366929684188717], [0.04366929684188717, 3.3716348588596663]]),
    ([0.0, 0.0], [-0.5248042443319995, -0.11531977810815439], [[1.0, 0.0], [0.0, 1.0]], [[0.8166483142606422, -0.13936207604466258], [-0.13936207604466258, 2.6138827967419838]]),
    ([0.0, 0.0], [-0.13174157849361678, -0.16245231866734705], [[1.0, 0.0], [0.0, 1.0]], [[6.44107096526866e-09, -7.945325634753827e-07], [-7.945325634753827e-07, 2.2807385261091975]]),
    ([0.0, 0.0], [-0.13174029350472116, 0.41857085725184817], [[1.0, 0.0], [0.0, 1.0]], [[6.313269955384359e-09, -2.504534435917077e-07], [-2.504534435917077e-07, 1.0167690299388888e-05]]),
    ([0.0, 0.0], [-0.13025411186714206, -0.3855177302702337], [[1.0, 0.0], [0.0, 1.0]], [[3.531532536379895e-11, -4.6980859348694985e-07], [-4.6980859348694985e-07, 0.0066890034964233805]]),
    ([0.0, 0.0], [-0.13945972878112067, 0.5320834167413316], [[1.0, 0.0], [0.0, 1.0]], [[1.947792355803144e-09, -1.5714343149794605e-08], [-1.5714343149794605e-08, 1.450066135945041e-07]]),
    ([0.0, 0.0], [-0.1394596240814114, 0.5320827817771304], [[1.0, 0.0], [0.0, 1.0]], [[1.9444614156217883e-09, -1.5725614670450004e-08], [-1.5725614670450004e-08, 1.453918667172646e-07]]),
    ([0.0, 0.0], [-0.13945960778845617, 0.532082629519135], [[1.0, 0.0], [0.0, 1.0]], [[1.942147210099439e-09, -1.5704721182462376e-08], [-1.5704721182462376e-08, 1.451541662411258e-07]]),
    ([0.0, 0.0], [-0.13945960305525598, 0.5320827497712559], [[1.0, 0.0], [0.0, 1.0]], [[1.943154685437367e-09, -1.5727591139528047e-08], [-1.5727591139528047e-08, 1.4541627830416624e-07]]),
    ([0.0, 0.0], [-0.13945952792684238, 0.5320820446547516], [[1.0, 0.0], [0.0, 1.0]], [[1.9379264794268327e-09, -1.5670168276861733e-08], [-1.5670168276861733e-08, 1.448430690881437e-07]]),
    ([0.0, 0.0], [-0.13945955109583733, 0.532082200707949], [[1.0, 0.0], [0.0, 1.0]], [[1.936725463927175e-09, -1.565529449011735e-08], [-1.565529449011735e-08, 1.4470465211479452e-07]]),
)

def trackers(data):
    stretch = VectorStatTracker(averages=data[0], covariance_matrix=data[2])
    erf = VectorStatTracker(averages=data[1], covariance_matrix=data[3])
    return (stretch, erf)

for count, (rate, tx, lx, duration, samples) in enumerate(tuple_list):
    rate *= 2
    if count in (4,):
        result = s.measure_and_compute(20.0, rate, trial_result_list, 20000.0, 29761904.0, trackers(list_integrator_data[count]), samples)
        _, _, _, stretch, erf, integrator_data = result
        print "    stretch {0!r}".format(stretch), "erf {0!r}".format(erf)
        print "integrator_data", repr(integrator_data)
    if count == 11:
        break
    measurement = ReceiveRateMeasurement(duration, rate, tx, lx)
    print "measurement", repr(measurement)
    trial_result_list.append(measurement)

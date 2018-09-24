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

import logging
import sys

from resources.libraries.python.MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement
from SoakSearch import SoakSearch as search

logging.basicConfig(level=getattr(logging, "DEBUG"))

pair_list = [
    (18750000.00000, 3666783),
    (18750000.00000, 7399082),
    (13193069.80860, 4375813),
    (13565982.66350, 6453122),
    (11235516.67310, 2827942),
    (11232797.29800, 4244609),
    (10340968.59620, 2342110),
    (10357522.88340, 1778197),
    ( 5965801.51134,       0),
    (10073617.12310, 2359332),
    (10063403.02070, 1164559),
    ( 6350588.08787,       0),
    ( 9852997.20749, 1471251),
    ( 9856975.87835,  171633),
    ( 7557334.08493,       0),
    ( 9770046.62474, 1507027),
    ( 9770650.98436, 1828279),
    ( 7995015.81949,       0),
    ( 7502389.48869,       0),
    ( 7505261.83673,       0),
]

print "soak compute, record measurer, non-printing"

s = search(None, 0.1, 1, 3000)

trial_result_list = list()
count = 0
for load, loss in pair_list:
    load *= 2
    print "load", load
    count += 1
    duration = s.tdpt * count
    tx = int(load * duration)
    measurement = ReceiveRateMeasurement(duration, load, tx, loss)
    trial_result_list.append(measurement)
    avg, stdev = s.compute(trial_result_list, 37500000.0, duration + 0.5)
    print "avg", avg, "stdev", stdev

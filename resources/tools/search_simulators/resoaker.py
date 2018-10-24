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
from SoakSearch import SoakSearch as search

logging.basicConfig(level=getattr(logging, "DEBUG"))

#pair_list = [
#    (6, 10000000.0, 17997947/6.0),
#    (5, 6997319.66667, 320/5.0),
#    (3, 28098.5778855, 0/3.0),
#    (4, 4352859.9034, 0/4.0),
#]

pair_list = [
    (1, 2*18750000.0, 1868071/1.0),
    (2, 2*188575.137687, 0),
    (3, 2*63372.4593146, 0),
    (4, 2*11492311.5694, 1662963/4.0),
    (5, 2*10970477.8476, 1573545/5.0),
    (6, 2*10075874.7282, 434604/6.0),
    (7, 2*2637427.14401, 0),
    (8, 2*9657980.3772, 423951/8.0),
    (9, 2*9664025.40306, 450378/9.0),
    (10, 2*5933632.77997, 0),
    (11, 2*5809696.42773, 0),
]

print "soak compute, record measurer, non-printing"

s = search(None, 0.1, 1, 3000)

trial_result_list = list()
for count, load, lps in pair_list:
    duration = s.tdpt * count
    tx = int(load * duration)
    loss = round(lps * duration)
    measurement = ReceiveRateMeasurement(duration, load, tx, loss)
    print "measurement", repr(measurement)
    trial_result_list.append(measurement)
    if count in (4,):
        avg, stdev = s.compute(trial_result_list, 37500000.0, 20.0 * (duration + 0.5))
        print "avg", avg, "stdev", stdev

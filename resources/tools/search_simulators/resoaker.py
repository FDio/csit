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

#pair_list = [
#    (18750000.000, 18562820.0000000),
#    (18750000.000, 18145057.5000000),
#    ( 2534125.987,        0.0000000),
#    ( 9677471.750,   643591.0000000),
#    ( 8329906.494,        0.0000000),
#    ( 9355676.750,    21388.5000000),
#    ( 7538936.275,        0.0000000),
#    ( 9344983.000,     1448.2500000),
#    ( 9155206.348,    76782.4444400),
#    ( 9335247.168,      537.3000000),
#    ( 7799688.417,        0.0000000),
#    ( 9334979.018,     4166.0000000),
#    ( 8059454.850,        0.0000000),
#    ( 9332896.518,      267.7142857),
#    ( 8225863.795,        0.0000000),
#    ( 9332763.160,    11787.5000000),
#    ( 8358069.252,        0.0000000),
#    ( 9326869.910,     8859.2222220),
#    ( 8412153.225,        0.0000000),
#    ( 9322440.799,    32790.6000000),
#    ( 8459904.298,        0.0000000),
#    ( 9306045.999,   136483.1364000),
#    (   10000.000,        0.0000000),
#    ( 9237804.931,   328466.9167000),
#    ( 7984881.691,        0.0000000),
#    ( 9073571.973,    60821.2692300),
#    ( 6277588.975,        0.0000000),
#]

pair_list = [
    (6, 10000000.0, 17997947/6.0),
    (5, 6997319.66667, 320/5.0),
    (3, 28098.5778855, 0/3.0),
    (4, 4352859.9034, 0/4.0),
]

print "soak compute, record measurer, non-printing"

s = search(None, 1.0, 1, 3000)

trial_result_list = list()
for count, load, lps in pair_list:
    load *= 2
    duration = s.tdpt * count
    tx = int(load * duration)
    loss = round(lps * duration)
    measurement = ReceiveRateMeasurement(duration, load, tx, loss)
    print "measurement", repr(measurement)
    trial_result_list.append(measurement)
    if count in (3, 4,):
        avg, stdev = s.compute(trial_result_list, 37500000.0, 1.0 * (duration + 0.5))
        print "avg", avg, "stdev", stdev

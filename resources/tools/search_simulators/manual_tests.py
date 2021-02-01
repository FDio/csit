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

#from KeyboardMeasurer import KeyboardMeasurer as measurer
#from RandomMeasurer import RandomMeasurer as measurer
from PromilesMeasurer import PromilesMeasurer as measurer
#from TwoPhaseMeasurer import TwoPhaseMeasurer as measurer
from LoggingMeasurer import LoggingMeasurer as infologging
from TimeTrackingMeasurer import TimeTrackingMeasurer as tracking
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

logging.basicConfig(level=getattr(logging, "DEBUG"))

p = tracking(infologging(measurer(0.001)))

print "optimized search, promiles measurer, printing"
#print "optimized search, two phase measurer, printing"

from resources.libraries.python.MLRsearch.MultipleLossRatioSearch import MultipleLossRatioSearch as my_search
s = my_search(measurer=p)

result = s.narrow_down_ndr_and_pdr(minimum_transmit_rate=1000000, maximum_transmit_rate=30000000, packet_loss_ratio=0.005)

#print "result repr:", repr(result)
print "result string:", str(result)
print "RW:", "NDR", result.ndr_interval.rel_tr_width, "PDR", result.pdr_interval.rel_tr_width
print "search took", p.total_time, "seconds", p.measurements, "measurements"
p.reset()

#with open("smart.txt", "a") as f:
#    f.write(str(result.ndr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.ndr_interval.measured_high.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_high.target_tr))
#    f.write('\n')

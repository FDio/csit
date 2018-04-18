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

#from KeyboardRateProvider import KeyboardRateProvider as provider
#from RandomRateProvider import RandomRateProvider as provider
from PromilesRateProvider import PromilesRateProvider as provider
#from TwoPhaseRateProvider import TwoPhaseRateProvider as provider
from LoggingRateProvider import LoggingRateProvider as infologging
from TimeTrackingRateProvider import TimeTrackingRateProvider as tracking
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

logging.basicConfig(level=getattr(logging, "DEBUG"))

p = tracking(infologging(provider(0.001)))

#print "basic binary search, 10.0 duration, width 20000.0, two phase provider, printing"
#
#s = search(rate_provider=p, duration=60.0, width=20000.0)
#result = s.narrow_down_ndr_and_pdr(fail_rate=20000, line_rate=37000000, allowed_drop_fraction=0.005)
#
##print "result repr:", repr(result)
#print "result string:", str(result)
#print "RW:", "NDR", result.ndr_interval.rel_tr_width, "PDR", result.pdr_interval.rel_tr_width
#print "search took", p.total_time, "seconds", p.measurements, "measurements"
#p.reset()
#sys.exit(0)
##
##with open("binary.txt", "a") as f:
##    f.write(str(result.ndr_interval.measured_low.target_tr) + " ")
##    f.write(str(result.ndr_interval.measured_high.target_tr) + " ")
##    f.write(str(result.pdr_interval.measured_low.target_tr) + " ")
##    f.write(str(result.pdr_interval.measured_high.target_tr))
##    f.write('\n')
##

print "optimized search, promiles provider, printing"
#print "optimized search, two phase provider, printing"

from resources.libraries.python.search.OptimizedSearchAlgorithm import OptimizedSearchAlgorithm as my_search
s = my_search(rate_provider=p)

result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)

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

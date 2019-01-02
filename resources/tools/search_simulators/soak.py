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

from SoakMeasurer import SoakMeasurer as measurer
from LoggingMeasurer import LoggingMeasurer as infologging
from TimeTrackingMeasurer import TimeTrackingMeasurer as tracking
from PLRsearch import PLRsearch as search

logging.basicConfig(level=getattr(logging, "INFO"))

p = tracking(infologging(measurer(10000000, 100000, 1, fast=False)))

print "soak search, soak measurer, printing"

s = search(p, 0.1, 2e-9, 50, 1800)

average, stdev = s.search(1, 10000000)

print "result average={avg}, stdev={stdev}".format(avg=average, stdev=stdev)

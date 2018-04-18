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
import pandas as pd
import numpy as np

#from KeyboardRateProvider import KeyboardRateProvider as provider
#from RandomRateProvider import RandomRateProvider as provider
from TwoPhaseRateProvider import TwoPhaseRateProvider as provider
from LoggingRateProvider import LoggingRateProvider as infologging
from TimeTrackingRateProvider import TimeTrackingRateProvider as tracking

#logging.basicConfig(filename='debug.log', level=getattr(logging, "INFO"))

p = tracking(infologging(provider()))

def stat(s):
    """Print statistics from many runs of algorithm s."""
    # For Pandas magic, see https://stackoverflow.com/a/24913075
    numberOfRows = 1000
    # create dataframe
    df = pd.DataFrame(index=np.arange(0, numberOfRows), columns=('time', 'ndr_lo', 'ndr_hi', 'pdr_lo', 'pdr_hi', 'ndr_rw', 'pdr_rw', 'meas'))
    # now fill it up row by row
    for x in np.arange(0, numberOfRows):
        result = s.narrow_down_ndr_and_pdr(fail_rate=20000, line_rate=37000000, allowed_drop_fraction=0.005)
        ##print "result repr:", repr(result)
        #print "result string:", str(result)
        #print "search took", p.total_time, "seconds"
        #loc or iloc both work here since the index is natural numbers
        ndr = result.ndr_interval
        pdr = result.pdr_interval
        ndr_lo = ndr.measured_low.transmit_rate
        ndr_hi = ndr.measured_high.transmit_rate
        pdr_lo = pdr.measured_low.transmit_rate
        pdr_hi = pdr.measured_high.transmit_rate
        df.loc[x] = [p.total_time,
                     ndr.measured_low.transmit_rate,
                     ndr.measured_high.transmit_rate,
                     pdr.measured_low.transmit_rate,
                     pdr.measured_high.transmit_rate,
                     ndr.rel_tr_width,
                     pdr.rel_tr_width,
                     p.measurements
                    ]
        p.reset()
    #print "min", repr(df.min())
    #print "median", repr(df.median())
    #print "max", repr(df.max())
    print "mean:"
    print df.mean()
    print "standard deviation:"
    print df.std()
    #print "skew", repr(df.skew())
    #print "kurtosis", repr(df.kurt())

#print "basic binary search, width 20000, 10s final duration, two phase provider"
#from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search
#s = search(rate_provider=p, duration=10.0, width=20000.0)
#stat(s)

print "optimized search, 30s final duration, two phase provider"
from resources.libraries.python.search.OptimizedSearchAlgorithm import OptimizedSearchAlgorithm as my_search
s = my_search(rate_provider=p)
stat(s)

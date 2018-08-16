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

#from KeyboardMeasurer import KeyboardMeasurer as measurer
#from RandomMeasurer import RandomMeasurer as measurer
from SingleLossMeasurer import SingleLossMeasurer as measurer
#from TwoPhaseMeasurer import TwoPhaseMeasurer as measurer
from LoggingMeasurer import LoggingMeasurer as infologging
from TimeTrackingMeasurer import TimeTrackingMeasurer as tracking

#logging.basicConfig(filename='debug.log', level=getattr(logging, "INFO"))

p = tracking(infologging(measurer(0.75)))

def stat(s):
    """Print statistics from many runs of algorithm s."""
    # For Pandas magic, see https://stackoverflow.com/a/24913075
    numberOfRows = 2000
    # create dataframe
    df = pd.DataFrame(index=np.arange(0, numberOfRows), columns=('time', 'ndr_lo', 'ndr_hi', 'pdr_lo', 'pdr_hi', 'ndr_rw', 'pdr_rw', 'meas'))
    # now fill it up row by row
    for x in np.arange(0, numberOfRows):
        result = s.narrow_down_ndr_and_pdr(minimum_transmit_rate=20000, maximum_transmit_rate=37000000, packet_loss_ratio=0.005)
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

print "basic binary search, width 20000, 10s final duration, single loss measurer"
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search
s = search(measurer=p, duration=10.0, width=20000.0)
stat(s)

print "optimized search, 30s final duration, single loss measurer"
from resources.libraries.python.MLRsearch.MultipleLossRatioSearch import MultipleLossRatioSearch as my_search
s = my_search(measurer=p)
stat(s)

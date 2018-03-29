# FIXME: License and similar.

import logging
import pandas as pd
import numpy as np

#from KeyboardRateProvider import KeyboardRateProvider as provider
#from RandomRateProvider import RandomRateProvider as provider
from TwoPhaseRateProvider import TwoPhaseRateProvider as provider
from LoggingRateProvider import LoggingRateProvider as infologging
from TimeTrackingRateProvider import TimeTrackingRateProvider as tracking
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

#logging.basicConfig(filename='debug.log', level=getattr(logging, "INFO"))

p = tracking(infologging(provider()))

#print "basic binary search, 7 iterations, random provider, printing"
##print "basic binary search, 7 iterations, two phase provider, printing"
#
#s = search(rate_provider=p, iterations=7, duration=60)
#result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)
#
#print "result repr:", repr(result)
#print "result string:", str(result)
#print "search took", p.total_time, "seconds"
#p.total_time = 0.0
#
#with open("binary.txt", "a") as f:
#    f.write(str(result.ndr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.ndr_interval.measured_high.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_high.target_tr))
#    f.write('\n')
#

def stat(s):
    """Print statistics from 1000 runs of algorithm s."""
    # For Pandas magic, see https://stackoverflow.com/a/24913075
    numberOfRows = 1000
    # create dataframe
    df = pd.DataFrame(index=np.arange(0, numberOfRows), columns=('time', 'ndr_lo', 'ndr_hi', 'pdr_lo', 'pdr_hi', 'ndr_rw', 'pdr_rw'))
    # now fill it up row by row
    for x in np.arange(0, numberOfRows):
        result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)
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
                     pdr.rel_tr_width
                    ]
        p.total_time = 0.0
    #print "min", repr(df.min())
    #print "median", repr(df.median())
    #print "max", repr(df.max())
    print "mean:"
    print df.mean()
    print "standard deviation:"
    print df.std()
    #print "skew", repr(df.skew())
    #print "kurtosis", repr(df.kurt())


print "relative width based search, 60s final duration, two phase provider"
from RelativeWidthBasedSearch import RelativeWidthBasedSearch as my_search
s = my_search(rate_provider=p, final_width=0.02)
stat(s)

print "total time search, 60s final duration, two phase provider"
from TotalTimeBasedSearch import TotalTimeBasedSearch as my_search
s = my_search(rate_provider=p, length=7.75)
stat(s)


#with open("smart.txt", "a") as f:
#    f.write(str(result.ndr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.ndr_interval.measured_high.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_high.target_tr))
#    f.write('\n')

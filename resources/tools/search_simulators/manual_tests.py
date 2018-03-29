# FIXME: License and similar.

import logging

#from KeyboardRateProvider import KeyboardRateProvider as provider
#from RandomRateProvider import RandomRateProvider as provider
from TwoPhaseRateProvider import TwoPhaseRateProvider as provider
from LoggingRateProvider import LoggingRateProvider as infologging
from TimeTrackingRateProvider import TimeTrackingRateProvider as tracking
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

logging.basicConfig(level=getattr(logging, "INFO"))

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

print "total time search, 60s final duration, random provider, printing"
#print "relative width based search, 60s final duration, two phase provider"

#from RelativeWidthBasedSearch import RelativeWidthBasedSearch as my_search
from TotalTimeBasedSearch import TotalTimeBasedSearch as my_search
s = my_search(rate_provider=p, length=7.7)

result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)

#print "result repr:", repr(result)
print "result string:", str(result)
print "search took", p.total_time, "seconds"
p.total_time = 0.0

#with open("smart.txt", "a") as f:
#    f.write(str(result.ndr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.ndr_interval.measured_high.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_low.target_tr) + " ")
#    f.write(str(result.pdr_interval.measured_high.target_tr))
#    f.write('\n')

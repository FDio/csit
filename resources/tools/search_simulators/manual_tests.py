

#from RandomRateProvider import RandomRateProvider as provider
from TwoPhaseRateProvider import TwoPhaseRateProvider as provider
from PrintingRateProvider import PrintingRateProvider as printing
from TimeTrackingRateProvider import TimeTrackingRateProvider as tracking
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search
from MySmartSearchAlgorithm import MySmartSearchAlgorithm as my_search

p = tracking(printing(provider()))

print "basic binary search, 7 iterations, two phase provider, printing"

s = search(rate_provider=p, iterations=7, duration=60)
result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)

print "result repr:", repr(result)
print "result string:", str(result)
print "search took", p.total_time, "seconds"
p.total_time = 0.0

print "my smart search, 60s final duration, two phase provider, printing"

s = my_search(rate_provider=p, final_duration=60)
result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)

print "result repr:", repr(result)
print "result string:", str(result)
print "search took", p.total_time, "seconds"
p.total_time = 0.0


print "basic binary search, 10 iterations, random provider, printing"

#from RandomRateProvider import RandomRateProvider as provider
from TwoPhaseRateProvider import TwoPhaseRateProvider as provider
from PrintingRateProvider import PrintingRateProvider as printing
from TimeTrackingRateProvider import TimeTrackingRateProvider as tracking
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

p = tracking(printing(provider()))
s = search(rate_provider=p, iterations=10, duration=8)
result = s.narrow_down_ndr_and_pdr(fail_rate=1000000, line_rate=30000000, allowed_drop_fraction=0.005)

print "result repr:", repr(result)
print "result string:", str(result)
print "search took", p.total_time, "seconds"

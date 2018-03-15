
print "basic binary search, 10 iterations, random provider, printing"

from RandomRateProvider import RandomRateProvider as provider
from PrintingProvider import PrintingProvider as wrapper
from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

p = wrapper(provider())
s = search(rate_provider=p, iterations=10, duration=1)
ndr_lo, ndr_hi, pdr_lo, pdr_hi = s.narrow_down_ndr_and_pdr(fail_rate=10, line_rate=1000, allowed_drop_fraction=0.1)

print "NDR interval:", ndr_lo, ndr_hi
print "PDR interval:", pdr_lo, pdr_hi

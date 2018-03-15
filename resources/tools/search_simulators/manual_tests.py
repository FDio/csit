
print "basic binary search, 10 iteration, random provider"

from RandomRateProvider import RandomRateProvider as provider
from PrintingProvider import PrintingProvider as wrapper

p = wrapper(provider())

from BasicBinarySearchAlgorithm import BasicBinarySearchAlgorithm as search

s = search(p, 10, 1)

results = s.narrow_down_ndr_and_pdr(line_rate=1000, fail_rate=10, allowed_drop_fraction=0.1)
print results

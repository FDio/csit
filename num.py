import math
from scipy.special import erfc
intermediate = -8.570653177255437
spread = 4882.570535894801
chi0 = 208.70245989122486
log_spread = math.log(spread)
erf_chi = erfc(-chi0)
log_erf_chi = math.log(erfc(-chi0))
result = intermediate + math.log(spread) - math.log(erfc(-chi0))
print "intermediate", repr(intermediate)
print "spread", repr(spread)
print "chi0", repr(chi0)
print "log_spread", repr(log_spread)
print "erf_chi", repr(erf_chi)
print "log_erf_chi", repr(log_erf_chi)
print "result", repr(result)

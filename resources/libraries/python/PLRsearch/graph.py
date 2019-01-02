import math

from log_plus import log_plus, log_minus
from PLRsearch import PLRsearch

mrr = 1000000.0
spread = 20000.0
load_tick = 10000.0
load = load_tick
while load < 2000000.0:
    load += load_tick
    sl = PLRsearch.lfit_stretch(None, load, mrr, spread)
    sa = math.exp(sl)
    el = PLRsearch.lfit_erf(None, load, mrr, spread*3)
    ea = math.exp(el)
    print load, sa, ea, sl, el

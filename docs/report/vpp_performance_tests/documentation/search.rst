Drop rate search algorithms
===========================

NDR and PDR
~~~~~~~~~~~

No Drop Rate (NDR) and Partial Drop Rate (PDR)
are the two quantities to be found by search algorithms.

The search performs multiple trial measurements.
Each trial measurement is performed at some specified duration,
transmit rate, frame size and traffic type.
The search algorithm choses those parameters
in order to find lower and upper bound for the quantity in question.

For most tests the bidirectional traffic is used
and latency is also measured during the trials.

There are other quantities that do not need such search,
for example Maximal Receive rate (MRR).

NDR
---

RFC 1242 and RFC 2544 define Throughput.
No Drop Rate is the same thing, maximal target transmit rate
for which trial measurement sees no dropped frames.

Due to the nature of modern hardware,
trial measurements can have slightly differen results
even if repeated with the same parameters,
search algorithms have to deal with that.

PDR
---

Given a parameter called Loss Tolerance (LT),
Partial Drop Rate is the maximal target transmit rate
for which fraction of dropped frames is not lager than LT.

Most tests use value LT=0.005 (meaning there can be
1 dropped frame in 200 transmitted frames).

PDR results tend to be more stable than NDR results,
as difference in transmit rate usually contributes
to drop fraction more strongly than hardware indeterminism.

Binary Search
~~~~~~~~~~~~~

This algorithm is used for older tests, which measure NDR or PDR.

The trials have constant parameters (including duration)
except the transmit rate parameter.

The algorithm needs minimal and maximal rate.
it assumes those are already valid boundaries for the searched quantity.
The algorithm also needs a so-called threshold parameter.

The algorithm repeatedly measures at the arithmetic average of current boundaries.
Depending on the measurement result (low od high measured drop fraction)
one of the previous boundaries is replaced, resulting in interval of smaller width.

If the width is smaller than the threshold parameter,
the current interval is returned, the lower boundary serving
as a conservative estimate of the searched quantity.

Binary search total run time does not depend on measurement results.
All the trials are done at the full trial duration,
and this algorithm does not attempt to save time in any way.

Optimized search
~~~~~~~~~~~~~~~~

This algorithm has been added in experimental state for 1804 release.

The logic of this algorithm is considerably more complicated than plain binary search,
in attempt to shorten overall search time, while keeping the desirable property
of returning results of specified precision even in worst case.

FIXME: Document all the specifics.

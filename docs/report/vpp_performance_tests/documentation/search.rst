Drop rate search algorithms
===========================

NDR and PDR
~~~~~~~~~~~

No Drop Rate (NDR) and Partial Drop Rate (PDR)
are the two quantities to be found by search algorithms.
There are other performance related quantities that do not need such search,
for example Maximal Receive rate (MRR).

RFC 2544 defines a trial measurement.
The search algorithms perform multiple trial measurements.
Each trial measurement is performed at some specified duration,
transmit rate, frame size and traffic type.
The search algorithm choses some of those parameters
in order to find lower and upper bound for the quantity in question.

When searching for NDR and PDR, a trial measurement result
consists of number of transmitted frames (Tx), and numer of received frames (Rx).
The difference is the number of dropped frames Dx := Tx - Rx.
Drop fraction is defined as Df := Dx / Tx.
Tx divided by trial duration is the measured transmit rate,
which can be slightly different from the target transmit rate (the trial parameter).

For most tests the bidirectional traffic is used
and latency is also measured during the trials.

NDR
---

RFCs 1242 and 2544 define Throughput.
No Drop Rate is the same thing, maximal target transmit rate
for which trial measurement sees no dropped frames.

Due to the nature of modern hardware,
trial measurements can have slightly different results
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

Abstract search algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~

Algorithms described in this document only care about one aspect of the measurement result,
whether Df is larger than the allowed value.

This allows us to define algorithm logic without referring to specific networking definitions.

In the following sections, we are describing such generic algorithms.
After that, we will bring network specific details back.

Common notions
--------------

Abstract algorithms search for a specific value of a generic quantity.
It is assumed that there exists unique "searched value",
and each measurement (at some other value) compares to it.
In practice, measurements can be inconsistent,
but effective search algorithms might never discover the inconsistence.

So an abstract search algorithm
uses trial measurements at values (chosen somehow),
with the measurement only revealing whether the measured value
is larger than the searched value, or not.

If the measured value is measured to be larger,
it can be used as a (valid) upper bound for the searched value.
If the measured value is measured to be not larger,
it can be used as a (valid) lower bound for the searched value.
Multiple measurements can discover multiple bounds,
but only the best fitting bound (largest lower bound and smallest upper bound)
is considered further.
The term "current lower bound" and "current upper bound"
point to such bounds currently best.
A current valid lower bound and a current valid and upper bound
define a mathematical (current, valid) interval of possible candidates for the searched value.

Each new measurement can improve one of the bounds,
"search step" is the proces of single measurement and interval update.

The width of current interval is defined as
its upper bound value minus its lower bound value.
Usually, search algorithms have exit conditions
which stop the search if the current width is low enough.
The search algorithm returns both bounds at that point.
When only one value is needed, usually the lower bound
is taken as a conservative estimate of the searched value,
but the interval width explicitly shows the search resolution.

Any two values can be undestood as a current search interval
(the smaller value being the lower bound),
but the measurement might disprove validity of some bound.
The smaller of the two values which is measured
to be larger than the searched value is called an invalid lower bound.
Similarly, the larger of the two values which is measured to be not larger
than the searched value is called an invalid upper bound.

In principle, both current bounds could be found invalid,
but once again, effective search algorithms might never measure both.

In general, abstract search algorithms track the current search interval
(valid or invalid) and perform search steps until the interval is good enough.

An internal search step is a search step performed when both bounds are valid.
The measured value is chosen from the interval interior
(typically at the arithmeric average of the bounds, although other choices are possible).
The measured value becomes a better bound (upper of lower),
so the interval is updated, its with is halved.
The new interval stays valid.

An external search step is a search step performed when one bound is invalid.
For example if the lower bound is invalid, the measured value is chosen
to be smaller than the invalid lower bound value.
Depending on the measurement result, the measured value either becomes
a valid lower bound, or better but still invalid lower bound.
In either case, the old upper bound becomes a better and valid upper bound.
The distance between the measured value and the invalid bound
is usually chosen in such a way that the new interval
has double the width of the previous interval
(although other choices are possible).

It should be noted that after one external search step,
the new interval has at least one valid bound,
subsequent external search steps either keep it that way or make it a valid interval,
and internal search steps always keep the interval valid.
That means any starting interval (however invalid) eventually becomes valid after enough
external search steps, and narrow enough after enough internal search steps.

(Internal) Binary Search
------------------------

The algorithm needs initial lower and upper bound.
It assumes those are already valid.
The algorithm also needs a so-called threshold parameter.

The algorithm repeatedly performs internal search steps
(at arithmetic average of current bounds),
until the interval width is smaller than the threshold.

The number of trial measurements done by binary search
does not depend on measurement results.

If we describe the initial interval width as some multiple of the threshold,
then the number of trials is equal to the logarithm of that multiple
in base two, rounded up.

External binary search
----------------------

This is a sub-algorithm. Its goal is just to find a valid interval
containing the searched value, without trying to make the interval narrow.

The algorithm needs two arbitrary (but different) values, creating an interval,
probably invalid one.

One of the bounds is measured. If it is valid, the other bound is measured.
If both are valid, the algorithm returns the initial interval.

Otherwise the first bound found invalid starts external search,
doubling the interval width at each search step.
Eventually a valid bound is found and algorithm returns.

The number of measurements the algorithm takes depends on the distance
of the searched value from the other bound than the bound which was found invalid.
For example if Hi is the initial upper bound value, Lo is the initial lower bound value
(which was measured and found invalid), Se is the searched value, and Log2
is the logarithmic function in base two, the number of external search steps is
Es = Log2((2*Hi - Lo - Se)/(Hi - Lo)) - 1, rounded up.
Number of measurements is 2 (if both bounds are valid) or Es + 1
(if the first measured bound is found invalid) or Es + 2 (if the first was valid but the second not).

External-internal binary search
-------------------------------

As the return interval of the external binary search is a valid interval,
it can be used as an input to internal binary search (with some threshold).

This way, executing the two searches in succession will result in an interval
which is both valid and narrow enough.

This combined algorithm has potential to perform smaller number of trials
compared to pure internal binary search over conservatively large initial interval,
if the (possibly invalid) initial interval of the combined search is "close enough" to the searched value.

TODO: Introduce trials at different durations and phases before describing the full optimized search.

Optimized search
~~~~~~~~~~~~~~~~

This algorithm has been added in experimental state for 1804 release.

The logic of this algorithm is considerably more complicated than plain binary search,
in attempt to shorten overall search time, while keeping the desirable property
of returning results of specified precision even in worst case.

FIXME: Document all the specifics.

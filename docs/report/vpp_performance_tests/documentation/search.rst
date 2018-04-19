Drop rate search algorithms
===========================

FIXME: Define "width goal" and use it consistently.

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

Internal Binary Search
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

There is one small optimization available in the compbined algorithm.
The external binary search (as described above) is not aware of the width goal,
so external binary search step always doubles the current interval width.
But it is possible for the combined search to be called on such a narrow interval
where the dobled width is still much smalled that the width goal.

In good case this results in more narrow results, but in bad case
this results in more trial measurements than necessary.
The optimization is simply to increase the extended width to the width goal,
if the doubled current width is smaller than that.

Duration aware algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~

Trial measurements in network performance testing do have configurable trial duration.

For minimizing the overall test duration, trial measurements should be done at as small durations as possible.
But RFC 2544 requires the trial duration to represent the steady state closely enough,
giving 60 seconds as a minimal duration.

The result of an abstract search algorithm is an interval, two bounds.
To satisft RFC 2544, at least the measurements at the two returned bounds should be done at full trial duration.
Unfortunately, each measurement done by internal binary search could end up being one of the two returned values,
so all the trials have to be measured at full duration.

Similarly, each measurement for external search step could end up being a valid bound
and not beind updated by the subsequent internal search.
Overall, each trial measurement of external-internal binary search has to be performed at full duration.

But external-internal search could perform only small number of trial measurements
if its initial interval is close to the searched value. This initial interval can come from any heuristic,
for example it can come from external-internal binary search with trial measurements done in smaller duration.
This preceding search will take some time, but hopefully the time savings from the final search will offset them.

The preceding search duration obviously depends on its trial duration, but it also depends on "quality" of its initial interval.

Multi phase search
------------------

External-internal binary search takes initial interval and turns it into result interval.
The initial interval can be arbitrary, the resulting interval consists of valid bounds,
measured in trials of sufficient duration, and the resulting interval is sufficiently narrow.
We can ciew one external-internal binary search as an iteration of repeated process of improving the current interval.
In order to distinguish this from other iterations (for example search steps),
we call one execution of external-internal binary search a "phase".

In multi phase search, there is an initial phase, some number of intermediate phases and a final phase.
The initial phase results in an interval (perhaps invalid) created by some heuristic
which might not need any interval on input.
Intermediate phases are external-internal binary searches with reduced trial durations and relaxed width requirements.
Final phase is external-internal binary search with the duration and width as required for the final result interval.

The initial phase should be very quick and should use any additional information not visible on abstract search level.

For intermediate phases, the question is on number of phases, trial durations and width requirements.
Optimal trial durations depend on stability of the searched value.
If multiple runs of external interval binary search (at the same duration and width goal)
result in wildly differing intervals, the quality of interval does not affect final phase duration much,
so it is not worth to run many intermediate phases at big-ish durations.
When such multiple runs result in fairly similar intervals, but there is noticable dependency on trial duration,
it is worth to have more intermediate phases to avoid having the final phase start from inapropriate interval.

But contrary to trial duration, there are two natural choices for width goal.

The first choice is to intermediate phases having the same width goal as the final phase.
In the best case scenario, the final phase only re-measures the two bounds,
finds them still valid and returns them.

The second choice is even better, but it deviates from the logic described so far slightly.
The second is to return from previous intermediate phase at double of the width goal,
and at the current phase perform one internal search step before re-measuring the bound.
There are two points for doing that.
First of all, the first choice will perform the internal search step at the end of the previous phase,
and then re-measure at the current phase. So the secon choice saves one previous phase measurement.
The other point is that the internal step results in a valid bound no matter what,
so only the other bound has to be re-measured, which risks finding it invalid and triggering the external search.
The first option risks finding a bound invalid two times.

The downside of the second option is more complicated algorithm logic.
For example the internal search step is not unconditional, as the input to the final phase
might already be narrower than the width goal (if the initial phase creates a very good interval).

Search algorithms with hard limits
----------------------------------

Number of trials for external search depends on the searched value,
but such value can be at infinity (or minus infinity), causing the algorithm to never stop in theory
(or to cause number overflows or underflows in practice).

But in pracice searches usually have some limit apriori.
For example, in network performance tests, the traffic generator has its maximum transmit rate,
so using target transmit rate bigger than that is pointless.
Similarly, when target transmit rate would result in less than one frame being transmitted,
the drop rate cannot be determined.

Intuitively, it is not difficult to see what changes have to be done to an abstract search algorithm
in order to make it avoid trial measurements outside such hard limits.

There are two behaviors such hard limits might introduce.
One behavior is optimistic. If an external search step reaches to (or beyond) such a hard limit,
make the algorithm assume there has been a trial at the limiting value
and its outcome has created a valid bound. This is how the internal binary search algorithm
treats its initial bounds.

The other behavior is pessimistic. If an external search step reaches to (or beyond) such a hard limit,
the algorithm performs the trial measurement at that limit.
If the measurement leads to a valid bound, the search continues normally (with internal search),
but if the measurement is still an invalid bound, the algorithm (or the phase in multi phase algorithm)
return immediatelly, in order for the test to detect the invalid bound and fail
(or the next phase hopefully re-measure and find the bound valid).

Unfortunatelly, these additional conditions tend to make the code look quite complicated,
even though the motivation for the additional conditions is not surprising.

Derivative reported values
--------------------------

The description of internal binary search algorithm used a parameter named threshold
and it was explicit in the exit condition being the current interval width being smaller than this constant.
The older test for finding NDR or PDR have been implemented that way.

The other algorithms were mentioning width goal, without making it clear it is a constant.
The reason is that for some quantities there are more natural exit conditions.

For example, in network performance testing, the quantity we are interested in is target transmit rate
(in frames per second). The searched value might differ significantly between test cases
(each using different routing setup, frame sizes and similar).
If we used the threshold parameter, constant across test cases, we will get
better relative resolution for high resulting rates and worse relative resolution for small resulting rates.

If the *relative* width (defined as the width divided by upper bound value) is the goal,
we can use the same constant across all the test cases.
If internal search steps keeps performing the trial measurements at target transmit rate
still being the arithmetic average of bound values, the lower half interval would have larger
relative width than the upper half.

Mathematically the easiest way around that is to perform the binary search
not for the target transmit rate as the quantity, but for its logarithm.
This is justified by negative rates not making sense anyway, and relative width of the rate
translating into absolute width of logarithm of the rate.

For the implementation, there are multiple possibilities, differing on how do rounding errors
affect the algorithm. The conservative approach is to keep tracking rate values,
but change the way external and internal search steps compute their next trial target transmit rate.
And do the change in such a way that doubling the "width" followed by halving the width
does not increase the resulting width.

Optimized search
~~~~~~~~~~~~~~~~

The multi phase search as described above (with hard limits and relative width goal)
works well as an abstract algorithm. But as drop rates have their specifics,
more improvements can be implemented.

The following sections list such improvements.

Initial phase based on MRR
--------------------------

The full optimized algorithm has (among others) parameters line_rate and fail_rate,
acting as a hard maximum (optimistic) and hard minimum (pessimistic) respectively.

The first trial measurement of initial phase is performed
at minimal duration (1.0 seconds by default) at line_rate.
The measured receive rate is called Maximal Receive Rate (MRR),
as indeed line_rate as the target transmit rate leads to largest receive rate.

The second trial measurement of the initial phase is performed at MRR
(or at line_rate minus the goal width if that is smaller,
or at the fail rate if that is larger).

MRR2 is the transmit rate from the second trial measurement
(or MRR minus the goal width iv that is smaller).
If MRR2 is larger than fail_rate, the third trial measurement is performed at MRR2.

If MRR2 is larger than fail rate, target transmit rates of the third and second trial measurements
are used for as the first intermediat phase initial lower bound and upper bound respectively.
Otherwise, target transmit rates from the second and the first trial measurements are used.

Searching for both NDR and PDR at once
--------------------------------------

Performance tests are interested in finding both NDR and PDR values for the same setup.
The simple approach is to execute two searches in succession, but this is not effective.

Each trial measurements results in some drop fraction, which might be either zero,
or nonzero but not larger than loss tolerance, or larger than loss tolerance.
The first and the last case indicate a valid bound (lower or upper respectively) for both NDR and PDR,
the middle case is a valid upper bound for NDR and valid lower bound for PDR.

Updating both current NDR and current PDR intervals can save some searches
(if the bounds turn out to be the new best fit for both intervals).
Also, this way the search cannot report PDR to be lower than NDR
(which could happen whwen running independent searches on an unstable system).

The logic of updating intervals upon new measurement is the most critical part
of the optimized search algorithm, as the target transmit rate can be wildly different
wrom what external or internal binary search would chode for the given interval
(when the value has been chosen for the other interval instead).

This is the first place where the instability of the underlying system can be made manifest to the algorithm.

As NDR and PDR are to be used as values showing usability of the system,
any inconsistencies in the measured drop fractions should be resolved conservatively.
That means smaller target transmit rate measurement with higher drop fraction
should invalidate previously valid lower bound,
but larger target transmit rate measurement with lower drop fraction
should not invalidate previously valid upper bound.

While there is only one correct and efficient way to update intervals,
there are multiple ways to prioritize which interval should be used
for chosing the target transmit rate for the next trial measurement.
Some of the ways even do not guarantee a non-initial phase will finish in finite number of measurements.
Other ways do guarantee that, but the overall duration can differ significantly.

In the optimized search the following priorities were chosen
(not listing additional conditions for hard limits).
If NDR lower bound is invalid, perform external search step for NDR.
Else if PDR lower bound is invalid, perform external search step for PDR.
Else if NDR upper bound is invalid, perform external search step for NDR.
Else if PDR upper bound is invalid, perform external search step for PDR.
Else if width goal is not reached for both intervals,
perform internal search step for the relatively wider interval (NDR if relative widths are equal).
Else if NDR lower bound has not been measured with the current phase trial duration, re-measure it.
Else if PDR lower bound has not been measured with the current phase trial duration, re-measure it.
Else if NDR upper bound has not been measured with the current phase trial duration, re-measure it.
Else if PDR upper bound has not been measured with the current phase trial duration, re-measure it.

Timeouts
--------

Even though the current implementation of the optimized search is believed to finish after finite time,
the worst case can make the overall search duration to be significantly larger than the good case,
and the final result will be quite unreliable anyway.

For those reasons the optimized search tracks its runiing time,
and it fails if the time is bigger than a "timeout" parameter.

Currently that result in failed test case without any output.
In the future, the current intervals might be returned,
to expose at least a partial information about the searched values.

Default parameter values
------------------------

Loss tolerance (called allowed_drop_fraction): 0.005
final_relative_width: 0.005
final_trial_duration: 30.0 seconds
initial_trial_duration: 1.0 seconds
intermediate_phases: 2
timeout: 600.0 seconds

That means the first intermediate phase has trial duration 1.0 second
and relative width goal 0.0198306291, the second intermediate phase
has trial duration 5.47722557505 second and relative width goal 0.00997,
and the final third phase has duration 30.0 seconds and relative width goal 0.005

Conclusion
----------

The full optimized algorithm has been added in experimental state for 1804 release.

Specific conditions, priorities and default parameter values might change in future
based on gathered test results.


# Introduction to MLRsearch

There is a whole hierarchy of abstraction levels around MLRsearch.
The bottom is the most specific, a certain version of a Python library,
containing all the implementation details.
The top is a "search algorithm".

The best introduction to MLRsearch is to start at the top level of abstraction,
and proceed to lower levels. Each lower level introduces a new concept,
together with details needed to understand it, but leaving out
other details (which will be added in even lower levels of abstraction).

This section ends once there are enough concepts
to discuss the main ways how MLRsearch
addresses the problems from the previous section.

The following subsections are introducing the concepts:
- Measurer as a way to obtain trial results,
- load statistic as a way to group multiple results,
- classifier as a way to classify the load statistic,
- return values as restricted list of classified loads,
- input parameters as a way to specify wanted return values
  (and to regulate some trade-offs related to searching for them).

## Measurer

MLRsearch (as a search procedure) can be described as a series of interactions
of two components. The lower level component is called Measurer,
it is this component that manipulates test equipment,
and offers a simple programmatic interface.

The remaining upper level component works purely in software,
it is also called MLRsearch (as a library) and it transforms input parameters
into return values, while calling Measurer to get the data it needs.

MLRsearch library expects the Measurer to be injected as a callable object,
which when called accepts two arguments,
performs a single trial measurement, and returns two values.

The arguments are the trial intended load and the trial intended duration.
The latter is usually called just "trial duration".
The process of selecting the argument values for next measurer call
is called "load selection" (as the duration part is usually simple).

Measurer is supposed to start the traffic at the constant intended load
and sustain it for the inteded duration. But Measurer may do more,
for example it may need to initialize the SUT and wait some time,
as required by RFC 2544 section 23.
All other values needed for the actual traffic generation (e.g. frame size)
are assumed to be configured on the measurer before the search starts.

The return values are trial (measured) loss ratio and trial cost.
Loss ratio is the number of frames lost divided by the number of frames sent
(with possible caveats discussed in the last section).

Trial cost is an arbitrary value expressing user's preferences in
ending the search. A common choice is the actual time duration
needed to return from Measurer (intended trial time plus any wait times
and other time overheads). The only important property of trial cost
is to be additive, as MLRsearch sums individual trial costs to get
the overal cost of the search so far.

Some quantities can be derived from argument and return values,
for example forwarding rate is computed from loss ratio and intended load.

The measurer call arguments, its returned values, and any derived quantity
of interest form a "trial result".

At this abstraction level, MLRsearch knows about bunch of trial results,
but the load selection is yet unspecified;
as is the relation how do trial results relate to MLRsearch inputs and outputs.

## Load statistic

MLRsearch may decide to perform several trials with the same intended duration.
For that reason, most of MLRsearch logic focuses
on the set their results, called a "load statistic".
Load statistics with zero trial results are never used in MLRsearch.

There is only one acceptable intended trial duration within a load statistic.
If a trial result with different trial intended duration is to be added
to a load statistic, only trials with the largest present trial duration
are kept, all others are forgotten.

Load statistics are never deleted, trial results in them are never deleted
unless when required by their trial duration.

The sum of the trial costs within a load statistic is called the "load cost".

At this abstraction level, MLRsearch tracks several load statistics
and updates them by calling measurer and incorporating each new trial result,
but the load selection is still unspecified.

## Classifier

In order to progress the search, MLRsearch needs a way to "decide" whether
it should focus at, below or above a particular intended load.
A part of code helping with this decision is abstracted as a "classifier".

A classifier (as a logical component instance) takes a load statistic as an input,
and outputs "definitely does satisfy", "definitely does not satisfy",
"maybe does satisfy" or "maybe does not satisfy".

The classification logic is always the same, but is governed by 3 parameter values,
so sometimes this document refers to the 3-tuple of parameter values
also as a "classifier" (instead of "classifier parameters", because
it is harder to form a proper plural of the latter).
The 3 parameters are:
- required cost
- loss ratio goal
- acceptance ratio

In other words, in object orienter programming terminology,
there is a single "classifier class", several possible "classfier instances",
and "classifier" usually means an instance.
MLRsearch usually tracks multiple classifiers, and can relate any load statistic
to any classifier, but usually focuses on a single classifier at a time.

The classification logic works like this:

For each trial result within a load statistic, its observed frame loss ratio
is compared to the classifier's loss ratio goal.
If the goal is the same or higher, the trial is "accepted",
otherwise the trial is "overstepped".
If the load cost is larger than or equal to the classifier's required cost,
the ratio of accepted trials is compared to the classifier's acceptance ratio.
If the acceptance ratio is larger or equal, the classifer output
is "definitely does satisfy", otherwise it is "definitely does not satisfy".

If the load cost is smaller than the classifier's required cost,
the logic is more complicated, and can be described using
two hypothetical load statistics, each created by adding "phantom" trial results
to already present "real" trial results.
Each phantom trial cost is set to the arithmetic average of the real trials' cost.
The number of phantom trials is the minimum to get the load cost
to no longer be below classifier's required cost.
One hypothetical load statistic, called pessimistic,
adds overstepped phantom trials.
The other one is called optimistic, and adds accepted phantom trials.
The hypothetical sets are then classified, and if the result is the same,
it is returned as the result of the original load statistic.

If the hypothetical results do not match, the ratio of accepted real trials
is compared to the classifier's acceptance ratio.
If the acceptance ratio is larger or equal, the classifer output
is "maybe does satisfy", otherwise it is "maybe does not satisfy".

At this abstraction level, MLRsearch not only tracks several load statistics,
but also several classifiers, while focusing on one classifier at time.
It is still not specified how the load classification helps with load selection.

TODO: Introduce bounds, tightest bounds, and "previous cost bounds".

## Return values

Some of the load statistics get returned as parts of MLRsearch output,
as the smallest load definitely not satisfying a classifier,
or the largest load below that definitely satisfying the classifier.

TODO: This paragraph should ne in "input arguments" subsection.
The list of classifiers the user is interested in is provided as part
of MLRsearch input arguments.
There are additional input arguments restricting the possible return values
(e.g. lower bound and upper bound have to be close enough together),
but any algorithm which uses Measurer and classifiers,
and with return values satisfying all above (before this paragraph)
can be called an implementation of MLRsearch.

There is one more property the current MLRsearch implementation holds,
but not sure it should be a strong requirement:
No load below a lower bound classifies as "maybe does not satisfy".

----

Multiple Loss Ratio Search (MLRsearch) is designed to perform search for
throughput meeting multiple packet loss ratio goals, including zero-loss
and non-zero-loss. The search is conducted in a sequence of phases,
each phase governed by its "phase criterion".

Criterion is a generic word for a structure consisting of several fields.
The important fields are "loss ratio goal" and "trial duration",
more fields are described later.
The word "criteria" means not only multiple criterion instances,
but also the ordering between them.

Some MLRsearch input arguments are also in a form of criteria.
MLRsearch transforms "input criteria" into "phase criteria"
and handles the latter in their order.
One input criterion transforms into several "early phase" criteria
and a "final phase" criterion. Those are processed in order,
before the next input criterion's phases.
MLRsearch uses shorter durations in the earlier phases,
and the final trial duration in the final phase.

For each phase criterion, MLRsearch tracks tight enough valid
lower bound and upper bound for the intended load associated with the criterion.
(The set of results of trials measured at the lower bound
does satisfy all the conditions within the phase criterion,
the set of result for the upper bound does not).
The bounds are found by looking at all trial results so far,
selecting the loads which are currently tightest.

Phase criterion also contains a field called "precision goal".
A phase ends once upper and lower bound are close enough according to this goal.
If the bounds are not close enough (or if there is no load acting as
a valid bound), MLRsearch selects (according to various heuristics)
a load to measure at next.
The duration of time required for a "trial" (stored in the phase criterion
as "trial duration" field) is used to perform one or several
sub-trials, obtaining robust information about a load.
After the measurement, the selected load becomes a new bound.
(Upper or lower, but valid and tighter than the older bound.)
When the final phase ends, the bounds become the MLRsearch output
(for given input criterion).

MLRsearch aims to address all problems identified in the previous section,
while also giving users options to control the trade-offs between
overall search time, result precision, repeatability, and RFC 2544 compliance.

{::comment}
Description above is still unclear, introducing many ambiguous terms, including input and phase criteria, with each criterion being a list of fields (or goals). Ordering is not explained. 

And I can't parse a paragraph like this:

"One input criterion transforms into several "early phase" criteria
and a "final phase" criterion. Those are processed in order,
before the next input criterion's phases."

I interpreted above and wrote it down here:

"The search is conducted across a sequence of phases, with each phase 
governed by a set of criteria:

- loss ratio goal, constant across all phases.
- trial duration, shorter in early phases and progressing to the longer duration set for the final phase.
- precision goal, lower in early phases and progressing to the set higher precision set for the final phase."

Per phase lower and upper bounds are found once above criteria are met.
(Add logic explaining how lower and upper bounds from previous phase are validated in the next phase.)

Or is it oversimplifying it too much?
{:/comment}

# MLRsearch Features

MLRsearch is a search algorithm which improves upon binary search by
adding several enhancements. It is useful to describe them individually
focusing on the problems they are aiming to address, even though the
overall effectiveness of MLRsearch is quite sensitive to the way these
enhancements are combined.

## Early phases

{::comment}
I'm not sure I like the current sub-sections structure (What it is),
(Why it is there) and (Relation to other problems), but let's leave it
in place for now to give the content some structure.
{:/comment}

### What it is

https://datatracker.ietf.org/doc/html/rfc2544#section-24
specifies an option of using shorter duration
for trials that are not part of "final determination".
In MLRsearch this is made explicit by using early phases.

Early phases are used to find an approximate result
with shorter trials and coarser precision.
With each subsequent phase, the conditions are approaching the final criteria,
with final phase providing the final search result.
The idea is to quickly get close to the final loads, so only a few loads
need to be measured at full trial duration to confirm the result.

Initial trial is done at the Forwarding Rate at Maximum Offered Load
([RFC2285](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2))
and the forwarding rate measured at it.
Subsequent phases build upon load information known from the previous phases
(and criteria).

### Why it is there

The early phases feature is there primarily to shorten the overall search time.

### How does it relate to other Problems

It is orthogonal to non-zero-loss criteria, it does not help
with result repeatability, and it frequently exposes inconsistent trials
(so the algorithm logic needs to be more complicated to deal with them).
But the overall search duration is so big the trouble is worth it.

## Multiple input goals

TODO: Use "goal" and "goals" instead of "criterion" and "criteria" everywhere.

### What it is

As mentioned before, MLRsearch handles the input criteria one by one,
finding the final bounds for the first input criterion
before starting early phases of the next input criterion.

The most important property is this:
No subsequent trials can change the final bounds for previous criteria.

MLRsearch checks the input criteria (the list as a whole),
and refuses them if it cannot guarantee that important property.
For example, input criteria can never have decreasing loss ratio goal.

{::comment}
In line with my comment in Introducing MLRsearch, I still don't follow
the description of the input and phase criteria, with each criterion
being a list of goals. There is a very high probability other people
will be lost too. The text is ambiguous. Suggestion: instead of talking
about abstracted criteria, start talking about the main three criteria
that everyone familiar with RFC2544 can related to: loss ratio goal,
trial duration and precision goal.
{:/comment}

### Why it is there

The multiple criteria feature is there to directly support
non-zero loss ratio goals.
This is expected to indirectly improve result repeatability and comparability,
as in practice (and for most models of noise),
the larger loss ratio goal, the more stable search result.

### How does it relate to other Problems

Regarding the overall search duration, searching for additional
non-zero-loss criteria adds to the duration,
but users can indirectly affect the increase
by tweaking the precision goal and trial duration for each input criterion.

As each trial result is internally related to each criterion,
it means a significant time is saved, when compared to separate searches
for each input criterion.
For example, a lower bound for a zero-loss criterion
is automatically also a lower bound for ane non-zero-loss criterion
(assuming everything else is equal in the two criterions),
but separate searches would need to spend some time finding that good
non-zero-loss lower bound.

Regarding the inconsistent trials problem, inconsistencies are frequently exposed,
especially against early phase trials of previous criteria.
Still, time savings are worth it (compared to separate searches
which could have simpler code due to not seeing the inconsistencies).

## Sub-trials

### What it is

{::comment}
Shouldn't this describe the concept of trials and sub-trials?
Right now it doesn't, at least in my view.
Instead it talks about input parameters and input criteria, that
themselves are murky and not described well earlier.
{:/comment}

There is an input parameter (a separate one, not part of input criteria)
called "subtrial duration".
(Future MLRsearch version may allow users to specify different
subtrial durations in each input criterion.)

{::comment}
Why different subtrial durations in each input criterion? And what input
criteria does this apply to?
{:/comment}

When MLRsearch assigns shorter duration for a load (e.g. in an earlier phase),
a single sub-trial with the shorter duration is executed.
But when MLRsearch assigns a longer duration, multiple sub-trials are executed
at the sub-trial duration.

{::comment}
Above paragraph doesn't make sense to me.
"earlier" or "early" phase?
{:/comment}

Result of each sub-trial can either honor or overstep the loss goal
(for any criterion). Input parameter (criterion field) "acceptance ratio"
(for each input criterion separately) then governs what ratio
of overstepped sub-trials is still tolerated when declaring
that the whole trial honored the current phase criterion.
In other words, the acceptance ratio is the "acceptable percentage of sub-trials
with loss higher than the goal" (but that is too long for a parameter name).

{::comment}
Shouldn't this describe a simple logic how sub-trial results are
evaluated using the "acceptance ratio" that governs what ratio of
overstepped sub-trials is tolerated?
{:/comment}

### Why it is there

The sub-trial feature is there as another approach to improve result
repeatability and comparability, motivated by DUT or SUT problem.
More directly than with non-zero-loss, sub-trials that overstepped
the loss ratio goal are thought to be affected by SUT noise too much,
so noiseless SUT performance is closer to the remaining sub-trials.

### How does it relate to other Problems

While the usage of multiple sub-trials does not eliminate
the influence of noise entirely, the hope is it will reduce
its impact on the values reported, enough for noticable boost of repeatability.

{::comment}
Doesn't this belong to previous section?
{:/comment}

For example, sub-trials can be a way to implement (a variant of)
Binary Search with Loss Verification as recommended in RFC 9004.

Sub-trials can also improve the overall search duration, as frequently
MLRsearch detects a point when no further sub-trial results can possibly
change the decision, so they can be skipped.
Another time save comes from "upgrading" (see next subsection) the load
from a previous phase, as sub-trials already measured
remain valid for the next phase.

{::comment}
Doesn't this belong to previous section?
{:/comment}

Many traffic analyzers need a quiet period between sub-trials,
because they cannot distinguish late frames from the previous sub-trial
from the frames of the current sub-trial.
The time overhead from quiet periods can be higher than the time saved
by skipping inconsequential sub-trials.

The sub-trial feature does not interfere with non-zero-loss problem,
except that it restricting which combination of input criteria
is acceptable by MLRsearch. (Acceptance ratio cannot decrease.)

Sub-trials complicate the handling of inconsistent trial result even more,
as the algorithm has to deal with "not measured enough" loads
outside otherwise valid bounds.
I.e. there can be loads where the set of sub-trials currently has
overstep ratio larger than the current phase acceptance ratio,
but it is not a clear upper bound yet, as there more sub-trials
will fit into the cuurrent phase trial duration, and after measuring them
the overstep ratio may no longer be above the acceptance ratio.

{::comment}
Unclear paragraph, at least to me.
{:/comment}

Once again, the other benefits make it worth to complicate the algorithm.

## Handling inconsistent trials

### Why it is there

After the final upper bound for zero loss criterion has been found, a higher load
can be seen with zero loss (when processing a non-zero loss criterion).
From RFC 1242 and RFC 2544 definitions, it is not clear whether the new
zero loss load can become the throughput.

In a way, sub-trials expose inconsistency at the same load and duration,
but also give a rule to decide based on acceptance ratio.

But both multiple loss goals and early phases create scenarios
where the search algorithm cannot avoid seeing inconsistent trial results.

After an earlier phase, a previously valid lower (or upper) bound
is no longer significant (it has too short trial or too few sub-trials),
so it has to be re-measured (or upgraded). But after that, the same load
may no longer be the same type of bound, so one bound type may become missing
for bisection purposes.

### What it is

MLRseach in that case starts an "external search", which is a variant
of exponential search. User can tweak the "expansion coefficient"
depending on how close the new valid bound is expected to be on average.

Here, "upgrade" applies to a load already measured with one or few sub-trials,
where more sub-trials need to be measured within the required trial duration.
Re-measure means the older information (at a shorter sub-trial)
is forgotten and replaced with new measurements (at a longer sub-trial).
Future versions of MLRsearch may be able to combine different-length sub-trials.

MLRsearch is "conservative" in this situation, meaning the high load
is never a throughput if there is a (not forgotten) smaller load
with non-zero-loss trial result.
The criterion ordering in MLRsearch relies on this design choice
to ensure the previously completed criteria never need to be re-visited.

{::comment}
TODO Again, I think this should be covered in the sub-section describing the phasing, not in "Handling inconsistent trials".
{:/comment}

In future MLRsearch versions, the behavior can become tweakable,
meaning user can request "progressive" behavior instead.
That means the highest load with zero loss would be reported as the throughput,
regardless of smaller load non-zero loss trials.
(In that case MLRsearch would process criteria from the highest loss ratio goal.)

This feature has no benefits for the main problems,
but needs to be done to allow features that have.

In fact, noisy trial results tend to significantly prolong
the overall search duration by triggering external search at the final phase.
In the worst case, this can make MLRsearch slower than vanilla bisection
(but in practice MLRsearch is still faster).

## RFC 2544 compliance

If the measurer does not honor all (or even not all required) conditions
in RFC 2544, the whole search procedure becomes conditionally compliant
(or even non-compliant) with RFC 2544.
For example RFC 2544 section 23 states at minimum of 7 seconds (total)
waiting around each sub-trial measurement.
(Not sure if that is a MUST or a SHOULD, but it does not really matter
as multiple sub-trials per trial are already non-compliant with RFC 2544).

Possible time-saving behaviors of the measurer (for example only sending
route updates when the previous ones would time-out during sub-trial,
not before each sub-trial as implied by RFC 2544 section 13)
are out of scope of this document.

Besides the Measurer behavior, compliance of the whole search depends
on the criteria used.

The only criterion unconditionally compliant with RFC 2544 is:
Zero loss ratio goal, sub-trial duration equal to final trial duration,
(acceptance ratio zero, but it should not matter as it always must be below one)
and final trial duration of (at least) 60 seconds.
The throughput is the final lower bound for this criterion.

This may restrict which other criteria can be applied in the same search,
but MLRsearch guarantees this one criterion will not be affected
by subsequent trials, and any trial result inconsistency will be resolved
in the same way as if only the compliant criterion was run.

Sadly, the compliant criterion will still have the same low repeatibility
and comparability (and minimal insight to "DUT in SUT" problems)
as vanilla bisection.

It is only the possibility of alternative criteria (non-zero loss goal,
smaller sub-trial duration, or both) that offer improvements in repeatability
and noiseless DUT performance estimation.
But even for the compliant criterion, MLRsearch is worth using
for the greatly reduced overall search time.

# Additional Considerations

RFC 2544 can be understood as having a number of implicit requirements.
They are made explicit in this section
(as requirements for this document, not for RFC 2544).

Recommendations on how to properly address the implicit requirements
are out of scope of this document.

## Reliability of Test Equipment

Both Traffic Generator (TG) and and Traffic Analyzer (TA)
MUST be able to handle correctly every intended load used during the search.
TG and TA are defined in https://datatracker.ietf.org/doc/html/rfc6894#section-4

On TG side, the difference between Intended Load and Offered Load
MUST be small enough.
Intended load: https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.1
Offered load: https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.2

TODO: How small is enough?

(For example, some TGs can send the correct number of frames,
but during longer time than sub-trial duration,
and that time is difficult to measure precisely enough.)

To ensure that, max load has to be set to low enough (safe) value.

Solutions (even problem formulations) for the following open problems
are outside of the scope of this document:
* Detecting when the test equipment operates above its safe load.
* Finding a large but safe load value.
* Correcting any result affected by max load not being a safe load.

This explains why MLRsearch returns intended load values as bounds
(as opposed to offered load values as required by RFC 2889),
as there is no (in-scope) guarantee TG is able to hit
any specific offered load value precisely.

## Very late frames

RFC 2544 requires quite conservative time delays
see https://datatracker.ietf.org/doc/html/rfc2544#section-23
to prevent frames buffered in one trial measurement
to be counted as received in a subsequent trial measurement.

However, for some SUTs it may still be possible to buffer enough frames,
so they are still sending them (perhaps in bursts)
when the next trial measurement starts.
Sometimes, this can be detected as a negative trial loss count, e.g. TA receiving
more frames than TG has sent during this trial measurement. Frame duplication
is another way of causing the negative trial loss count.

https://datatracker.ietf.org/doc/html/rfc2544#section-10
recommends to use sequence numbers in frame payloads,
but generating and verifying them requires test equipment resources,
which may be not plenty enough to suport at high loads.
(Using low enough max load would work, but frequently that would be
smaller than SUT's actual throughput.)

RFC 2544 does not offer any solution to the negative loss count problem,
except implicitly treating negative trial loss counts
the same way as positive trial loss counts.

This document also does not offer any practical solution.

Instead, this document SUGGESTS the Measurer to take any precaution
necessary to avoid very late frames.

This document also REQUIRES any detected duplicate frames to be explicitly
counted as additional lost frames.
This document also REQUIRES any remaining negative trial loss count
to be treated as a positive trial loss count of the same absolute value.

# Sample implementation

This draft currently does not include enough details for benchmarking teams
to implement their own MLRsearch code.

There is https://pypi.org/project/MLRsearch/
which implements more optimizations, mainly to get slightly better
overall duration, most of which have no visible effect on result repeatability.

TODO: Specify which code can be called a MLRsearch implementation
(e.g. PyPI has multiple versions available, with missing or additional features).

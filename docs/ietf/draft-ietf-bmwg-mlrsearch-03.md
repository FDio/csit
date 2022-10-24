---
title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-03
date: 2022-10-31

ipr: trust200902
area: ops
wg: Benchmarking Working Group
kw: Internet-Draft
cat: info

coding: us-ascii
pi:    # can use array (if all yes) or hash here
  toc: yes
  sortrefs:   # defaults to yes
  symrefs: yes

author:
      -
        ins: M. Konstantynowicz
        name: Maciek Konstantynowicz
        org: Cisco Systems
        email: mkonstan@cisco.com
      -
        ins: V. Polak
        name: Vratko Polak
        org: Cisco Systems
        email: vrpolak@cisco.com

normative:
  RFC 2544:

informative:
  FDio-CSIT-MLRsearch:
    target: https://s3-docs.fd.io/csit/rls2110/report/introduction/methodology_data_plane_throughput/methodology_data_plane_throughput.html#mlrsearch-tests
    title: "FD.io CSIT Test Methodology - MLRsearch"
    date: 2021-11
  PyPI-MLRsearch:
    target: https://pypi.org/project/MLRsearch/0.4.0/
    title: "MLRsearch 0.4.0, Python Package Index"
    date: 2021-04

--- abstract

TODO: Update after all sections are ready.

This document proposes improvements upon [RFC 2544], specifically to
throughput search methodology, by defining a new search algorithm
referred to as Multiple Loss Ratio search (MLRsearch for short).
One of the key design principles behind MLRsearch is minimizing the
total test duration and searching for multiple criteria in a single search.

The main motivation behind MLRsearch is the new set of challenges and
requirements posed by NFV (Network Function Virtualization),
specifically software based implementations of NFV data planes. Using
[RFC 2544] in the experience of the authors yields results with poor repeatibility
and comparability, due to a large number of factors that are
out of scope for this draft. MLRsearch offers several way to address
this challenge, giving user configuration options to select their way.

--- middle

{::comment}
    As we use kramdown to convert from markdown,
    we use this way of marking comments not to be visible in rendered draft.
    https://stackoverflow.com/a/42323390
    If other engine is used, convert to this way:
    https://stackoverflow.com/a/20885980
{:/comment}

# Purpose and Scope

The purpose of this document is to describe MLRsearch (Multiple Loss
Ratio search), a throughput search algorithm optimized for software
DUTs.

Applying vanilla RFC 2544 throughput bisection to software DUTs
results in a number of problems:

- Binary search takes too long as most of trials are done far from the
  eventually found throughput.
- The required final trial duration and pauses between trials also
  prolong the overall search duration.
- Software DUTs show noisy trial results (noisy neighbor problem),
  leading to big spread of possible discovered throughput values.
- Throughput requires loss of exactly zero packets, but the industry
  frequently allows for small but non-zero losses.
- The definition of throughput is not clear when trial results are
  inconsistent.

MLRsearch aims to address these problems by applying the following set
of enhancements:

- Multiple phases within one criterion search, early ones need less
  trials.
  - Earlier phases also aim at lesser precision (to save time).
  - Use Forwarding rate at maximum offered load
    ([RFC2285](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2)) 
    to initialize the first early phase.
- Allow searching with multiple search criteria.
  - Each trial result can affect any criterion in principle
    (trial reuse).
- Instead of single long trial, allow the use of multiple shorter
  trials.
  - Allow some percentage of the sub-trials to overstep the target
    packet loss ratio.
- Be conservative when encountering inconsistent results.
  - Search one criterion by one, carefully ordering them.
- Multiple load selection heuristics to save time
  by trying hard to avoid unnecessarily narrow intervals.

MLRsearch algorithm's configuration options are flexible enough to
support both conservative settings (unconditionally compliant with RFC
2544 but longer search duration and worse repeatability) and aggressive
settings (shorter search duration and better repeatability but not
compliant with RFC 2544).

No part of RFC 2544 is intended to be obsoleted by this document.

# Problems

## Long Test Duration

Emergence of software DUTs, with frequent software updates and a
number of different packet processing modes and configurations, drives
the requirement of continuous test execution and bringing down the test
execution time.

In the context of discovering particular DUT's network throughput, this
calls for improving the time efficiency of throughput search. Using
basic binary search as defined in RFC 2544 for finding software DUT's
throughput takes too long.

A vanilla bisection (at 60s trial duration for unconditional RFC 2544
compliance) is slow, because most trials spend time quite far from the
eventual throughput.

RFC 2544 does not specify the stopping condition for throughput search,
so users can trade-off between search duration and precision goal,
but due to exponential behavior of bisection, small improvement
in search duration needs relatively big sacrifice in result precision.

## DUT within SUT

RFC 2285 defines:

- DUT as
  - The network forwarding device to which stimulus is offered and
    response measured.
  - https://datatracker.ietf.org/doc/html/rfc2285#section-3.1.1
- SUT as
  - The collective set of network devices to which stimulus is offered
    as a single entity and response measured.
  - https://datatracker.ietf.org/doc/html/rfc2285#section-3.1.2

RFC 2544 specifies a test setup with an external tester stimulating the
networking system, treating it either as a single DUT, or as a system
of devices, an SUT.

In case of software networking, the SUT consists of a software program
processing packets (device of interest, the DUT),
running on a server hardware and using operating system functions as appropriate,
with server hardware resources shared across all programs
and the operating system.

DUT is effectively "nested" within SUT.

Due to a shared multi-tenant nature of SUT, DUT is subject to
interference (noise) coming from the operating system and any other
software running on the same server. Some sources of noise can be
eliminated (e.g. by pinning DUT program thread(s) to specific CPU core
(s) and isolating those cores to avoid context switching). But some
noise remains after all such reasonable precautions are applied. This
noise does negatively affect DUT's network performance. We refer to it
as an SUT noise.

DUT can also exhibit fluctuating performance e.g. while performing
some "stop the world" internal stateful processing. In many cases this
may be an expected per-design behavior, as it would be observable even
in a hypothetical scenario where all sources of SUT noise are
eliminated. Such behavior affects trial results in a way similar to SUT
noise. We use "noise" as a shorthand covering both DUT fluctuations and
genuine SUT noise.

A simple model of SUT performance consists of a baseline noiseless performance,
and an additional noise. The baseline is assumed to be constant (enough).
The noise varies in time, sometimes wildly. The noise can sometimes be negligible,
but frequently it lowers the observed SUT performance in a trial.

In this model, SUT does not have a single performance value, it has a spectrum.
One end of the spectrum is the noiseless baseline,
the other end is a "noiseful" performance. In practice, trial results
close to the noiseful end of the spectrum happen only rarely.
The worse performance, the more rarely it is seen.

Focusing on DUT, the benchmarking effort should aim
at eliminating only the SUT noise from SUT measurement.
But that is not really possible, as there are no realistic enough models
able to distinguish SUT noise from DUT fluctuations.

However, assuming that a well-constructed SUT has the DUT as its
performance bottleneck, the "DUT noiseless performance" can be defined
as the noiseless end of SUT performance spectrum.(At least for
throughput. For other quantities such as latency there will be an
additive difference.) By this definition, DUT noiseless performance
also minimizes the impact of DUT fluctuations.

{::comment}
Below paragraph doesn't belong here. Not sure, yet, where it belongs
though.

This means that DUT noiseless performance cannot be measured directly,
but can only be inferred (estimated) based on direct measurement trials
performed on SUT.
As throughput search should be quick, the number of trials is limited,
so the estimate may have poor repeatability.
(If more trial results are available, for example from a soak test
https://datatracker.ietf.org/doc/html/rfc8204#section-4
estimates can be more reliable, perhaps even identifying DUT fluctuations.)
{:/comment}

In this document, we reduce the "DUT within SUT" problem to estimating
the noiseless end of SUT performance spectrum from a limited number of
trial results.

Any improvements to throughput search algorithm, aimed for better
dealing with software networking SUT and DUT setup, should employ
strategies recognizing the presence of SUT noise, and allow discovery of
(proxies for) DUT throughput at different levels of sensitivity to SUT noise.

## Repeatability and Comparability

RFC 2544 does not suggest to repeat throughput search, and from just one
throughput value, it cannot be determined how repeatable that value is.
In practice, poor repeatability is also the main cause of poor
comparability, e.g. different benchmarking teams can test the same DUT
but get different throughput values.

RFC 2544 throughput requirements (60s trial, no tolerance to single frame loss)
force the search to converge around the noiseful end of SUT performance
spectrum. And as that end is affected by rare trials of significantly low
performance, the resulting throughput repeatability is poor.

The repeatability problem is the problem of defining a search procedure
which reports more stable results
(even if they can no longer be called "throughput" in RFC 2544 sense).
According to baseline (noiseless) and noiseful model, better repeatability
will be at the noiseless end of the spectrum.
Therefore, solutions to the "DUT within SUT" problem
will help also with the repeatability problem.

Conversely, any alteration to RFC 2544 throughput search
that improves repeatability should be considered
as less dependent on the SUT noise.

An alternative option is to simply run a search multiple times, and report some
statistics (e.g. average and standard deviation). This can be used
for "important" tests, but it makes the search duration problem even
bigger.

## Throughput with Non-Zero Loss

https://datatracker.ietf.org/doc/html/rfc1242#section-3.17
defines throughput as:
    The maximum rate at which none of the offered frames
    are dropped by the device.

and then it says:
    Since even the loss of one frame in a
    data stream can cause significant delays while
    waiting for the higher level protocols to time out,
    it is useful to know the actual maximum data
    rate that the device can support.

Contrary to that, many benchmarking teams settle with non-zero
(small) loss ratio as the criterion for "a throughput".

Motivations are many: modern protocols tolerate frame loss better;
trials nowadays send way more frames within the same duration;
impact of rare noise bursts is smaller as the baseline performance
can compensate somewhat by keeping the loss ratio below the goal;
if SUT noise with "ideal DUT" is known, it can be set as the loss ratio goal.

Regardless of validity of any and all similar motivations,
support for non-zero loss goals makes any search algorithm more user-friendly.
RFC 2544 throughput is not friendly in this regard.

Searching for multiple loss ratio goals also helps to describe the SUT
performance better than a single goal result. Repeated wide gap between
zero and non-zero loss loads indicates the noise has a large impact on
the overall SUT performance.

It is easy to modify the vanilla bisection to find a lower bound
for intended load that satisfies a non-zero-loss goal,
but it is not obvious how to search for multiple goals at once,
hence the support for multiple loss goals remains a problem.

## Inconsistent Trial Results

While performing throughput search by executing a sequence of
measurement trials, there is a risk of encountering inconsistencies
between trial results.

The plain bisection never encounters inconsistent trials.
But RFC 2544 hints about possibility if inconsistent trial results in two places.
The first place is section 24 where full trial durations are required, presumably
because they can be inconsistent with results from shorter trial durations.
The second place is section 26.3 where two successive zero-loss trials
are recommended, presumably because after one zero-loss trial
there can be subsequent inconsistent non-zero-loss trial.

Examples include:

- a trial at the same load (same or different trial duration) results
  in a different packet loss ratio.
- a trial at higher load (same or different trial duration) results
  in a smaller packet loss ratio.

Any robust throughput search algorithm needs to decide how to continue
the search in presence of such inconsistencies.
Definitions of throughput in RFC 1242 and RFC 2544 are not specific enough
to imply a unique way of handling such inconsistencies.

Ideally, there will be a definition of a quantity which both generalizes
throughput for non-zero-loss and other repeatibility enhancements,
while being precise enough to force a specific way to resolve trial
inconsistencies.
But until such definition is agreed upon, the correct way to handle
inconsistent trial results remains an open problem.

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

# IANA Considerations

No requests of IANA.

# Security Considerations

Benchmarking activities as described in this memo are limited to
technology characterization of a DUT/SUT using controlled stimuli in a
laboratory environment, with dedicated address space and the constraints
specified in the sections above.

The benchmarking network topology will be an independent test setup and
MUST NOT be connected to devices that may forward the test traffic into
a production network or misroute traffic to the test management network.

Further, benchmarking is performed on a "black-box" basis, relying
solely on measurements observable external to the DUT/SUT.

Special capabilities SHOULD NOT exist in the DUT/SUT specifically for
benchmarking purposes. Any implications for network security arising
from the DUT/SUT SHOULD be identical in the lab and in production
networks.

# Acknowledgements

Many thanks to Alec Hothan of OPNFV NFVbench project for thorough
review and numerous useful comments and suggestions.

--- back

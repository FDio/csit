---
title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-03
date: 2022-10-14

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
Ratio search), a throughput search algorithm optimized for software networking.

Applying vanilla RFC 2544 throughput bisection to software networking
results in a number of problems:

* Throughput requires loss of exactly zero packets,
  but the industry frequently allow for small but non-zero losses.
* Binary search takes too long when most of trials are done far
  from the evntually found throughput.
* The required final trial duration and pauses between trials
  also prolong the overal search duration.
* Modern DUTs show noisy trial results (noisy neighbor problem), leading to
  big spread of possible discovered throughput.
* The definition of throughput is not clear when trial results are inconsistent.

(The last problem is invisible in vanilla throughput search,
but it appears when some solutions to other problems are applied.)

MLRsearch aims to address these problems by applying the following set
of enhancements:

* Allow searching with multiple search criteria.
 * Each trial result can affect any criterion in principle (trial reuse).
* Be conservative when encountering inconsistent results.
 * Search one criterion by one, carefully ordering them.
* Instead of single long trial, allow the use of multiple shorter trials.
 * Allow some percentage of the sub-trials to overstep the target loss ratio.
* Multiple phases within one criterion search, early ones need less trials.
 * Earlier phases also aim at lesser precision (to save time).
 * Use Forwarding rate at maximum offered load
   ([RFC2285](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2))
   to initialize the first early phase.
* Multiple load selection heuristics to save time
  by trying hard to avoid unnecessarily narrow intervals.

MLRsearch algorithm's configuration options are flexible enough
to support both conservative settings (unconditionally compliant with RFC 2544
but longer search duration and worse repeatability) and aggressive settings
(shorter search duration and better repeatability but not compliant with RFC 2544).

No part of RFC 2544 is intended to be obsoleted by this document.

# Problems

## Long Test Duration

Emergence of software networking, with frequent software updates and
a number of different packet processing modes and configurations, drives the requirement of
continuous test execution and bringing down the test execution time.

In the context of discovering particular DUT's network throughput, this
calls for improving the time efficiency of throughput search. Using
basic binary search as defined in RFC 2544 for finding maximum
throughput just takes too long.

One of the main factors impacting the convergence of throughput search
(and resulting overall execution time) are inconsistent trial results,
often present when testing software networking DUTs.

## Inconsistent Trial Results

While performing throughput search by executing a sequence of
measurement trials, there is a risk of encountering inconsistencies
between trial results.

Examples include:

- a trial at the same load (same or different trial duration) results
  in a different packet loss ratio.
- a trial at higher load (same or different trial duration) results
  in a smaller packet loss ratio.

Any robust throughput search algorithm needs to decide how to continue
the search in presence of such inconsistencies.
Definitions of throughput in RFC 1242 and RFC 2544 are not specific enough
to imply a unique way of handling such inconsistencies.

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
networking system, treating it as an under test target.

In case of software networking, the benchmarked networking system, the
SUT, consists of a software program processing packets (under test
target, the DUT), running on server hardware using operating system
functions as appropriate, with server hardware resources shared across
all programs and operating system running on that server. 

DUT is effectively "nested" within SUT.

Due to a shared multi-tenant nature of SUT, DUT is subject to
interference (noise) coming from the operating system and any other
software running on the same server. This noise does negatively affect
DUT's network performance. We refer to it as an SUT noise.

One approach to this problem is to limit the noise coming from the
interactions with other components of the SUT. But as RFC 2544 is an
SUT measurement, it is not really possible to filter out the noise
(no realistic enough model of the noise is known). 

This means that DUT noiseless performance can not be measured, but can
only be inferred (estimated) based on direct measurement tests
performed on SUT.

Any improvements to throughput search algorithm, aimed for better
dealing with software networking SUT and DUT setup, should employ
strategies recognizing the presence of SUT noise and allow discovery of
DUT's throughput at different levels of sensitivity to this noise.

## Repeatability and Comparability

Throughput of software DUTs in general is sensitive to server resource
allocation by operating system during runtime and SUT noise including
any interrupts or other interference with software threads involved in
frame processing. In practice this means low repeatability of
throughput results with specified precision goal.

Any alteration to RFC 2544 throughput search that improves repeatability
should be considered as less dependent on the SUT noise.

RFC 2544 does not suggest to repeat throughput search, and from just one
throughput value, it cannot be determined how repeatable that value is.
In practice, poor repeatability is also the main cause of poor
comparability, e.g. different benchmarking teams can test the same DUT
but get different throughput values.

Another option is to simply run a search multiple times, and report some
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

With software DUTs, running on shared COTS servers (SUTs), being
sensitive to any interference with server resource allocation, many
benchmarking teams settle with non-zero small packet loss ratio as the
criterion for
"a throughput".

In order to better assess the actual performance of software DUT, both
zero packet loss ratio and (small) non-zero packet loss ratio goals can
be used as throughput search criteria. Corresponding Non-Drop Rate
(NDR) and Partial-Drop Rate (PDR) throughput values, intuitively,
should be not far from each other for a well behaving SUT and DUT setup.

Repeated wide gap between NDR and PDR indicates either large amount of
interference (SUT noise) or a fundamental problem with the DUT (e.g. DUT
interupts itself while performing some internal stateful processing).

# Introducing MLRsearch

Multiple Loss Ratio Search (MLRsearch) is designed to perform search for
maximum load with respect to multiple loss ratio goals, including zero-loss
and non-zero-loss. In fact, there are other input parameters packed
with loss ratio goal to form a search "criterion":

- Loss ratio goal.
- Final precision goal.
- Final trial duration.
- Acceptable percentage of sub-trials with loss higher than the goal.
- Number of intermediate phases.
- Expansion coefficient.

MLRsearch accepts an ordered list of criteria.
For each criterion, MLRsearch returns tight enough valid
lower bound and upper bound for the intended load associated with the criterion
(the lower bound satisfies the loss ratio goal within the acceptable percentage,
the upper bound does not).
Depending on SUT behavior, a load can end up acting as a lower bound
for multiple criteria (and an upper bound for some more criteria).

MLRsearch employs multiple search phases (for each criterion separately)
to optimize the time required to get to interesting search region,
using shorter durations in the earlier phases,
and the target duration in the final phase.
Adjective "final" us used for quantities related specifically for the final
determination phase, to make clear earlier phases may use different quantities.

The duration of time assigned for a "trial" is used to perform
one or several sub-trials, obtaining robust information about a load
before the search decides which criteria can be satisfied with this load.
The sub-trial is the unit that has to satisfy restrictions
from RFC 2544 (sections 23 and 24).

MLRsearch aims to address all identified problems,
while also giving users options to control the trade-offs between
overall search time, result precision and repeatability, and RFC 2544 compliance.

# MLRsearch Functionality

MLRsearch can be seen as a search algorithm which improves upon binary search
by adding several enhancements. While the overall effectiveness of MLRsearch
is quite sensitive to the way the enhancements are combined,
it is useful to describe key features of MLRsearch in isolation,
and how do they address the problems described in the first section.

Some features are hardcoded, other features are tweakable.

## Early phases

https://datatracker.ietf.org/doc/html/rfc2544#section-24
already mentions the possibity of using shorter duration
for trials that are not part of "final determination".

In MLRsearch this is made explicit by using phases.
The final phase will be giving the final search result (for given criterion),
but earlier phases are trying to find an approximate result
with shorter trials and coarser precision.
The idea is to get close to the final loads, so only a few loads
need to be measured at full trial duration to confirm the result.

The very first phase for the first criterion
(instead of bisecting the whole load spectrum)
uses Forwarding rate at maximum offered load
([RFC2285](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2))
and the forwarding rate measured at it.
All the other phases build upon load information known from the previous phases
(and criteria) and return new bounds valid
for the improved trial duration and precision goal.

The early phases feature is there primarily to shorten the overall search time.
It is orthogonal to non-zero-loss criteria, it does not help
with result repeatability, and it frequently exposes inconsistent trials
(so the algorithm logic needs to be more complicated to deal with them).
The overall search duration is so big the trouble is worth it.

## Multiple search criteria

MLRsearch handles the criteria one by one, finding the final bounds for the first
criterion before starting early phases of the next criterion.

The most important property is this:
No subsequent trials can change the final bounds for previous criteria.

MLRsearch checks the criteria, and refuses them if it cannot guarantee
that important property.
For example, criteria can never have decreasing loss ratio goal,
decreasing overstep ratio, nor increasing final trial duration.

Zero-loss (if present) is thus the first criterion handled.

The multiple criteria feature is there to directly support
non-zero loss ratio goals, thus indirectly improving
result repeatability and comparability.
(Experience shows: the larger loss ratio goal, the more stable search result.)
Searching for additional non-zero-loss criteria adds to the overall search duration,
but each criterion has its own tweakable precision goal and trial duration.
The fact each trial is internally related to each criterion means
significant time is saved (compared to separate searches for each criterion).
Inconsistent trials are frequently exposed, especially against
early phase trials of previous criteria.
Still, time savings are worth the complications in the algorithm.

## Sub-trials

An input parameter for any search criterion is "subtrial duration".
When MLRsearch assigns shorter duration for a load (e.g. in an earlier phase),
single trial with the shorter duration is executed.
But when MLRsearch assigns a longer duration, multiple sub-trials are executed
at the sub-trial duration.

Each sub-trial can either honor or overstep the loss goal (for each criterion).
Input parameter "overstep ratio" (for each criterion separately)
then governs what ratio of overstepped sub-trials is still tolerated
when declaring that the whole trial honored the criterion.
In other words, the overstep ratio is the "acceptable percentage of sub-trials
with loss higher than the goal" mentioned in the overview
(but that is too long for a parameter name).

The sub-trial feature is there as another approach to improve result
repeatability and comparability.

While the usage of multiple sub-trials does not eliminate the influence of noise,
the hope is it will reduce its impact on the values reported.
This is especially useful when the real quantity of interest is aimed at DUT
(not the rest of SUT), for example sub-trials can be a way to implement
Binary Search with Loss Verification as recommended in RFC 9004.

Sub-trials also improve the overall search duration, as frequently
MLRsearch can detect a point when no further sub-trial results can possibly
change the decision, so they can be skipped.
Another time save comes from "upgrading" the load from a previous phase,
as sub-trials alrady measured remain valid for the next phase.

This assumes the time ovehead between trials is no too great,
as most traffic analyzers need a quiet period, because they cannot distinguish
late frames from the previous trial from the current trial frames.

Sub-trial feature does not interfere with non-zero-loss critera search,
except restricting which combination MLRsearch accept.

Sub-trials complicate the handling of inconsistent trial result even more,
as the algorithm has to deal with "not measured enough" loads
outside otherwise valid bounds.
Once again, the other benefits make it worth to complicate the algorithm.

## Handling inconsistent trials

The plain bisection never encounters inconsistent trials.
But RFC 2544 hints about possibility if inconsistent trial results in two places.
The first place is section 24 where full trial durations are required,
because they can be inconsisted with results from shorter trial durations.
The second place is section 26.3 where two successive zero-loss trials
are recommended, because after one zero-loss trial there can be subsequent
inconsistent non-zero-loss trial.

In a way, sub-trials expose inconsistency at the same load and duration,
but also give a rule to decide based on overstep ratio.

But both multiple loss goals and early phases create scenarios
where the search algorithm cannot ignore inconsistent trial results.

After an earlier phase, a previously valid lower (or upper) bound
is no longer significant (it has too short trial or too few sub-trials),
so it has to be re-measured (or upgraded). But after that, the same load
may no longer be the same type of bound, so one bound type is missing
for bisection purposes.
MLRseach in that case starts an "external search", which is a variant
of exponential search. User can tweak the "expansion coefficient"
depending on how close the new valid bound is expected to be on average.

Here, "upgrade" applies to a load already measured with one or few sub-trials,
where more sub-trials need to be measured within the assigned trial duration.
Re-measure means the older information (at a shorter sub-trial)
is forgotten and replaced with new measurements (at a longer sub-trial).
Future versions of MLRsearch may be able to combine different-length-subtrials.

After the final upper bound for zero loss criterion has been found, a higher load
can be seen with zero loss (when processing a non-zero loss criterion).
From RFC 1242 and RFC 2544 definitions, it is not clear whether the new
zero loss load can become the throughput.
MLRsearch is "conservative" in this situation, meaning the high load
is never a throughput if there is a (not forgotten) smaller load
with non-zero-loss trial result.
The criterion ordering in MLRsearch relies on this design choice
to ensure the previously completed criteria never need to be re-visited.

In future MLRsearch versions, the behavior can become tweakable,
meaning user can request "progressive" behavior instead.
That means the highest load with zero loss would be reported as the throughput,
regardless of smaller load non-zero loss trials.
(In that case MLRsearch would process criteria from the highest loss ratio goal.)

This feature has no benefits for the main problems,
but needs to be done to allow features that have.

## Measurer

The process of performing a sub-trial is abstracted as a Measurer.
Measurer is a callable object, which when called accepts two arguments
and returns two values.
The arguments are the sub-trial intended load and the sub-trial intended duration.
The return values are sub-trial measured loss ratio and sub-trial overall duration
(the latter includes any waiting required by RFC 2544 section 23).

Forwarding rate (for initial phase) can be computed from loss ratio
and intended load.

All other values needed for the actual traffic generation (e.g. frame size)
are assumed to be configured on the measurer before the search starts.
MLRsearch will keep calling the measurer with the same arguments
until it becomes clear no further sub-trials within the time assigned
for this trial can change the current algorithm decision.

If the measurer does not honor all (or even not all required) conditions
in RFC 2544, the whole search procedure becomes conditionally compliant
(or even non-compliant) with RFC 2544.

Possible time-saving behaviors of the measurer (for example only sending
route updates when the previous ones would time-out during sub-trial,
not before each sub-trial as implied by RFC 2544 section 13)
are out of scope of this document.

This feature does not address any problems,
but makes the algorithm itself more easily testable and extensible,
e.g. it simplifies integration with third-party measurers (ol algorithms).

# RFC 2544 compliance

Besides the measurer behavior, compliance of the whole search depends
on the criteria used.

The only criterion unconditionally compliant with RFC 2544 is:
Zero loss ratio goal, sub-trial duration equal to final trial duration,
(overstep ratio zero, but it should not matter as it always must be below one)
and final trial duration of (at least) 60 seconds.
The throughput is the final lower bound for this criterion.

This may restrict which other criteria can be applied in the same search,
but MLRsearch guarantees this one criterion will not be affected
by subsequent trials, and any trial result inconsistency will be resolved
in the same way as if only the compliant criterion was run.

Sadly, the compliant criterion will still have the same low repeatibility
and comparability as vanilla bisection.

It is only the possibility of alternative criteria (non-zero loss goal,
smaller sub-trial duration, or both) that offer improvements in repeatability.
But even for the compliant criterion, MLRsearch is worth using
for the greatly reduced overall search time.

# Additional Considerations

RFC 2544 can be understood as having a number of implicit requirements.
They are made explicit in this section
(as requirements for this document, not for RFC 2544).

Recommendations on how to properly address the implicit requirements
are out of scope of this document.

## Reliability of Test Equipment

Both Traffic Gemerator (TG) and and Traffic Analyzer (TA)
MUST be able to handle correctly every intended load used during the search.

On TG side, the difference between Intended Load and Offered Load
MUST be small enough.

TODO: How small is enough?

To ensure that, max load has to be set to low enough value.

Solutions (even problem formulations) for the following open problems
are outside of the scope of this document:
* Detecting when the test equipment operates above its safe load.
* Finding a large but safe load value.
* Correcting any result affected by max load value not being a safe load.

This explains why MLRsearch returns intended load values as bounds
(as opposed to offered load values as required by RFC 2889),
as there is no (in-scope) guarantee TG is able to hit any specific offered load.

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
This document also REQUIRES, any remaining negative trial loss count
to be treated as positive trial loss count of the same absolute value.

# Sample implementation

This draft currently does not include enough details for benchmarking teams
to implement their of MLRsearch code.

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

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
        role: editor
        email: mkonstan@cisco.com
      -
        ins: V. Polak
        name: Vratko Polak
        org: Cisco Systems
        email: vrpolak@cisco.com

normative:
  RFC2544:

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

This document proposes changes to [RFC2544], specifically to packet
throughput search methodology, by defining a new search algorithm
referred to as Multiple Loss Ratio search (MLRsearch for short). Instead
of relying on binary search with pre-set starting offered load, it
proposes a novel approach discovering the starting point in the initial
phase, and then searching for packet throughput based on defined packet
loss ratio (PLR) input criteria and defined final trial duration time.
One of the key design principles behind MLRsearch is minimizing the
total test duration and searching for multiple packet throughput rates
(each with a corresponding PLR) concurrently, instead of doing it
sequentially.

The main motivation behind MLRsearch is the new set of challenges and
requirements posed by NFV (Network Function Virtualization),
specifically software based implementations of NFV data planes. Using
[RFC2544] in the experience of the authors yields often not repetitive
and not replicable end results due to a large number of factors that are
out of scope for this draft. MLRsearch aims to address this challenge
in a simple way of getting the same result sooner, so more repetitions
can be done to describe the replicability.

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
  big spread of possible discovered throughput (lack or repeatability).
* The definition of throughput is not clear when trial results are inconsistent.

(The last problem is invisible in vanilla throughput search,
but it appears when some solutions to other problems are applied.)

MLRsearch aims to address these problems by applying the following set
of enhancements:

* Allow searching with multiple search criteria.
 * Each trial result can affect any criterion in principle (trial reuse).
* Be conservative when encountering inconsistent results.
 * Search one criterion by one, carefully ordering them.
* Instead of single long trial, use multiple short trials.
 * Allow some percentage of the trials to overstep the target loss ratio.
* Multiple phases within one criterion search, early ones need less trials.
 * Earlier phases also aim at lesser precision (to save time).
 * Use Forwarding rate at maximum offered load
  ([RFC2285](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2))
  to initialize early phases.
* External search when previous bound becomes invalid.
* Relative width goals, so the default supports any scale.
* Multiple load selection heuristics to save time
 by trying hard to avoid unnecessarily narrow intervals.

{::comment}
    This document also introduces new terminology (e.g. ratio loss load),
    so the motivations can be formulated more easily.
{:/comment}

MLRsearch algorithm's configuration options are flexible enough
to support both conservative settings (unconditionally compliant with RFC2544
but longer search duration and worse repeatability) and aggressive settings
(shorter search duration and better repeatability but not compliant with RFC2544).

No part of RFC2544 is intended to be obsoleted by this document.

# Problems

## Repeatability and Comparability

RFC2544 does not suggest to repeat throughput search,
{::comment}probably because the full set of tests already takes long{:/comment}
and from just one throughput value, it cannot be determined
how repeatable that value is, i.e. how likely it is
for a repeated throughput search to end up with a value
less then the precision goal away from the first value.

Depending on SUT behavior, different benchmark teams
can report significantly different througput values,
even when using identical SUT and test equipment,
just because of minor differences in their search algorithm
(e.g. different max load value).

While repeatability can be addressed by repeating the search several times,
the differences in the comparability scenario may be systematic,
i.e. seeming like a bias in one or both benchmark teams.

This document RECOMMENDS to repeat a selection of "important" tests
ten times, so users can ascertain the repeatability of the results.

TODO: How to report? Average and standard deviation?

If a specific search algorithm (including values for tweakable parameters)
becomes a de facto standard, it will leave less freedom
for the benchmark teams to encounter the comparability problem.

At the moment, more research is needed to determine
which exact algorithm is worth standardizing on.

{::comment}
    Possibly, the old DUTs were quite sharply consistent in their performance,
    and/or precision goals were quite large in order to save overall search time.

    With software DUTs and with time-efficient search algorithms,
    nowadays the repeatability of throughput can be quite low,
    as in standard deviation of repeated Througput results
    is considerably higher than the precision goal.
{:/comment}

{::comment}
    TODO: Unify with PLRsearch draft.
    TODO: No-loss region, random region, lossy region.
    TODO: Tweaks with respect to non-zero loss ratio goal.
    TODO: Duration dependence?

    Both RFC2544 and MLRsearch return throughput somewhere inside the random region,
    or at most the precision goal below it.
{:/comment}

## Non-Zero Loss Ratio Goals

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

{::comment}
    While this may still be true for some protocols,
    research has been performed...

    TODO: Add this link properly: https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-Y.1541-201112-I!!PDF-E&type=items
    TODO: List values from that document, from 10^-3 to 4*10^-6.

    ...on other protocols and use cases,
    resulting in some small but non-zero loss ratios being considered
    acceptable. Unfortunately, the acceptable value depends on use case
    and properties such as TCP window size and round trip time,
    so no single value of loss ratio goal (other than zero)
    is considered to be universally applicable.
{:/comment}

TODO: Separate "noisy" insto a subsection, the current two can then refer.

New "software DUTs", traffic forwarding programs running on
commercial off-the-shelf (COTS) compute server hardware,
frequently exhibit quite low repeatability of throughput results.

This is due to throughput of software DUTs (programs) being sensitive (in general)
to server resource allocation by operating system during runtime,
as well as any interrupts or other interference with software threads involved
in frame processing.

{::comment}
    What is worse, some benchmark groups (which groups?; citation needed)
    started reporting loads that achieved only "approximate zero loss",
    while still calling that a throughput (and thus becoming non-compliant
    with RFC2544).
{:/comment}

{::comment}
    Ideally, modern protocols (and modern usage of old protocols) would evolve
    to tolerate small trial loss ratios, thus decreasing the importance of zero loss.
    Is there any document proving this is happening?
{:/comment}

# Solution ideas

This document gives several independent ideas on how to address
the problems above, while keeping the (average) overall search duration short.

Unless explicitly stated otherwise, all of the solution ideas
keep the search procedure unconditionally compliant with RFC2544.

Only limited research has been done into the question of which combination
of ideas achieves the best compromise with respect to overal search time,
high repeatability and high comparability.

## Short duration trials

https://datatracker.ietf.org/doc/html/rfc2544#section-24
already mentions the possibity of using shorter duration
for trials that are not part of "final determination".

Obviously, the upper and lower bound from a smaller duration trial
can be used as the initial upper and lower bound candidates
for the final determination.

MLRsearch makes it clear a re-measurement is always needed
if no tighter bound was found with the longer duration.
It also specifies what to do if the longer trial is no longer a valid bound
of the expected type, e.g. start the external search.
Additionaly one halving can be saved during the shorter duration search.

### TODO: External search

TODO: Uper bound, lower bound, tightest bound, invalid bound, final interval,
expansion coefficient, ...

{::comment}
Uncomment if external search description needs this:

### Re-measurement

An act of conducting a new trial at intended load identical to what
an old trial used, but with increased trial duration.
{:/comment}

## FRMOL as reasonable start

TODO expand: Overal search ends with "final determination" search,
preceded by "shorter duration search" preceded by "bound initialization",
where the bounds can be considerably different from min and max load.

For SUTs with high repeatability, the FRMOL is usually a good approximation
of throughput. But for less repeatable SUTs, forwarding rate (TODO define)
is frequently a bad approximation to throughput, therefore halving
and other robust-to-worst-case approaches have to be used.
Still, forwarding rate at FRMOL load can be a good initial bound.

## Non-zero loss ratios

See the "Non-Zero Loss Ratio Goals" section above.

TODO: Reformulate.
To deal with that, this document recommends
searching for multiple ratio loss loads of interest
for software DUTs that run on general purpose COTS servers:
* zero loss ratio load (the usual throughput),
* and at least one non-zero loss ratio load.

In our (whose?) experience, the higher the loss ratio goal is,
the better is the repeatability of the corresponding throughput rate.

This document RECOMMENDS the benchmark teams to search with
at least one non-zero loss ratio goal (regardless of DUT type).
This document does not suggest any particular non-zero loss ratio goal value
to search the corresponding load for.


A search for a load corresponding to a non-zero loss ratio goal
is very similar to a search for throughput,
just the criterion when to increase or decrease the intended load
for the next trial measurement uses the comparison of trial loss ratio
to the loss ratio goal (instead of comparing loss count to zero)
Any search algorithm that works for throughput can be easily used also for
non-zero loss ratios, perhaps with small modifications
in places where the measured forwarding rate is used.

## Trial reuse (was Concurrent ratio search)

A single trial measurement result can act as an upper bound for a lower
loss ratio goal, and as a lower bound for a higher loss ratio goal
at the same time. This is an example of how
it can be advantageous to search for all loss ratio goals "at once",
or at least "reuse" trial measurement result done so far.

Even when a search algorithm is fully deterministic in load selection
while focusing on a single loss ratio and trial duration,
the choice of iteration order between loss ratio goals and trial durations
can affect the obtained results in subtle ways.
MLRsearch offers one particular ordering.

{::comment}
    It is not clear if the current ordering is "best",
    it is not even clear how to measure how good an ordering is.
    We would need several models for bad SUT behaviors,
    bug-free implementations of different orderings,
    simulator to show the distribution of rates found,
    distribution of overall search durations,
    and a criterion of which rate distribution is "bad"
    and whether it is worth the time saved.
{:/comment}

## Load selection heuristics and shortcuts

Aside of the two heuristics already mentioned (FRMOL based initial bounds
and saving one halving when increasing trial duration),
there are other tricks that can save some overall search time
at the cost of keeping the difference between final lower and upper bound
intentionally large (but still within the precision goal).

TODO: Refer implementation subsections on:
* Uneven splits.
* Rounding the interval width up.
* Using old invalid bounds for interval width guessing.

The impact on overall duration is probably small,
and the effect on result distribution maybe even smaller.
TODO: Is the two-liner above useful at all?

# Non-compliance with RFC2544

It is possible to achieve even faster search times by abandoning
some requirements and suggestions of RFC2544,
mainly by reducing the wait times at start and end of trial.

Such results are therefore no longer compliant with RFC2544
(or at least not unconditionally),
but they may still be useful for internal usage, or for comparing
results of different DUTs achieved with an identical non-compliant algorithm.

TODO: Refer to the subsection with CSIT customizations.

# Additional Requirements

RFC2544 can be understood as having a number of implicit requirements.
They are made explicit in this section
(as requirements for this document, not for RFC2544).

Recommendations on how to properly address the implicit requirements
are out of scope of this document.

{::comment}

    Although some (insufficient) ideas are proposed.

{:/comment}

{::comment}

    TODO: highlight importance of results consistency
    for SUT performance trending and anomaly detection.

{:/comment}

## Reliability of Test Equipment

Both TG and TA MUST be able to handle correctly
every intended load used during the search.

On TG side, the difference between Intended Load and Offered Load
MUST be small.

TODO: How small? Difference of one packet may not be measurable
due to time uncertainties.

{::comment}

    Maciek: 1 packet out of 10M, that's 10**-7 accuracy.

    Vratko: For example, TRex uses several "worker" threads, each doing its own
    rounding on how many packets to send, separately per each traffic stream.
    For high loads and durations, the observed number of frames transmitted
    can differ from the expected (fractional) value by tens of frames.

{:/comment}

TODO expand: time uncertainty.

To ensure that, max load (see Terminology) has to be set to low enough value.
Benchmark groups MAY list the max load value used,
especially if the throughput value is equal (or close) to the max load.

{::comment}

    The following is probably out of scope of this document,
    but can be useful when put into a separate document.

    TODO expand: If it results in smaller throughput reported,
    it is not a big issue. Treat similarly to bandwidth and PPS limits of NICs.

    TODO expand: TA dropping packets when loaded only lowers throughput,
    so not an issue.

    TODO expand: TG sending less packets but stopping at target duration
    is also fine, as long as the forwarding rate is used as throughput value,
    not the higher intended load. But MLRsearch uses intended load...

    TODO expand: Duration stretching is not fine.
    Neither "check for actual duration" nor "start+sleep+stop"
    are reliable solutions due to time overheads and uncertainty
    of TG starting/stopping traffic (and TA stopping counting packets).

{:/comment}

Solutions (even problem formulations) for the following open problems
are outside of the scope of this document:
* Detecting when the test equipment operates above its safe load.
* Finding a large but safe load value.
* Correcting any result affected by max load value not being a safe load.

{::comment}

    TODO: Mention 90% of self-test as an idea:
    https://datatracker.ietf.org/doc/html/rfc8219#section-9.2.1

    This is pointing to DNS testing, nothing to do with throughput,
    so how is it relevant here?

{:/comment}

{::comment}

    Part of discussion on BMWG mailing list (with small edits):

    This is a hard issue.
    The algorithm as described has no way of knowing
    which part of the whole system is limiting the performance.

    It could be SUT only (no problem, testing SUT as expected),
    it could be TG only (can be mitigated by TG self-test
    and using small enough loads).

    But it could also be an interaction between DUT and TG.
    Imagine a TG (the Traffic Analyzer part) which is only able
    to handle incoming traffic up to some rate,
    but passes the self-test as the Generator part has maximal rate
    not larger than that. But what if SUT turns that steady rate
    into long-enough bursts of a higher rate (with delays between bursts
    large enough, so average forwarding rate matches the load).
    This way TA will see some packets as missing (when its buffers
    fill up), even though SUT has processed them correctly
    (albeit with latency jitter).

{:/comment}

### Very late frames

{::comment}

    In CSIT we are aggressive at skipping all wait times around trial measurement,
    but few of DUTs have large enough buffers.
    Or there some is another reason why we are seeing negative loss counts.

{:/comment}

RFC2544 requires quite conservative time delays
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

RFC2544 does not offer any solution to the negative loss count problem,
except implicitly treating negative trial loss counts
the same way as positive trial loss counts.

This document also does not offer any practical solution.

Instead, this document SUGGESTS the search algorithm to take any precaution
necessary to avoid very late frames.

This document also REQUIRES any detected duplicate frames to be counted
as additional lost frames.
This document also REQUIRES, any negative trial loss count
to be treated as positive trial loss count of the same absolute value.

{::comment}

    !!! Make sure this is covered elsewere, at least in better comments. !!!

    ## TODO: Bad behavior of SUT

    (Highest load with always zero loss count can be quite far from lowest load
    with always nonzero loss count.)
    (Non-determinism: warm up, periodic "stalls", perf decrease over time, ...)

    Big buffers:
    http://www.hit.bme.hu/~lencse/publications/ECC-2017-B-M-DNS64-revised.pdf
    See page 8 and search for the word "gaming".

{:/comment}

# Terminology

TODO: Search procedure?
TODO: "The search" can then be one run of the search procedure.

## Existing

* DUT and SUT: see the definitions in sections 3.1.1 and 3.1.2 of:
  https://datatracker.ietf.org/doc/html/rfc2285
* Intended load: https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.1
* Offered load: https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.2
* Maximum offered load (MOL): see
  https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.3
* Forwarding rate at maximum offered load (FRMOL)
  https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2
* Traffic Generator (TG) and Traffic Analyzer (TA): see
  https://datatracker.ietf.org/doc/html/rfc6894#section-4

## Introduced

These notions are useful when discussing any search procedure.

### A Safe Load

A value for intended load, such that any trial
with this intended load is correctly handled by both TG and TA,
regardless of trial duration and SUT behavior,
e.g. offered load is not too different from intended load.

Frequently, it is not known what the maximal safe load is.

### Max Load

Maximal intended load to be used during the search.

Benchmarking team decides which value is low enough
to guarantee values reported by TG and TA are reliable.
It has to be a safe load, but it can be lower than a safe load (estimate)
for added safety.

This value MUST NOT be higher than MOL, which itself MUST NOT
be higher than Maximum Frame Rate
https://datatracker.ietf.org/doc/html/rfc2544#section-20

TODO: SHOULD this value be reported? MUST if equal to throughput?

### Min Load

Minimal intended load to be used during the search.

Benchmarking team decides which value is high enough
to guarantee the trial outcomes are reliable.
E.g. considerable overall search time can be saved by declaring SUT faulty
if too high trial loss ratio is seen at the min load.

Zero frames per second is usually not a valid min load value,
especially if relative width is used as a stopping condition.

### Trial Loss Count

The absolute value of the difference between
the number of frames transmitted from TG
and the number of frames received by TA.

Negative difference of counts is possible, e.g. when SUT duplicates some frames,
or when some frames arrived extremely late after the previous trial.
The absolute value is there to treat such anomalies as lost frames.

This is one of outcomes of a single trial.

### Trial Loss Ratio

Trial loss count divided by the number of frames transmitted from TG.

This is one of outcomes of a single trial.

Strictly speaking, this is undefined if the number of frames transmitted from TG
is zero. Any search procedure that does not prevent this case
(e.g. by using high enough min rate) SHOULD consider this outcome
as zero trial loss ratio.

Min load SHOULD be high enough to ensure this does not happen.

{::comment}
    For bi-directional throughput tests, the aggregate ratio is calculated,
    based on the aggregate number of frames transmitted and received.
    If the trial loss count is negative, its absolute value MUST be used
    to keep compliance with RFC2544.
{:/comment}

RFC 1242 defines (and RFC 2544 clarifies) a similar notion
of Frame Loss Rate. It differs from trial loss ratio by being a percentage,
and by not avoiding negative values.

This document discourages the usage of "frame loss rate", as the word "rate"
usually describes how an absolute quantity is being applied over a unit time
"at a steady rate".

### Loss Ratio Goal

{::comment}
    FIXME: Code calls this a Target Loss Ratio. Unify.
{:/comment}

A value acting as one of optional inputs for the search.
The search procedure may accept multiple loss ratio goals.

The search is trying to achieve trial loss ratios close to this goal value.
Loss ratio goal of zero characterizes the search for RFC 2544 throughput.

{::comment}
### Final Trial Duration

A value specifying a duration, so that trials with shorter trial duration
cannot directly affect values reported by the search procedure.
This is one of required inputs for the search procedure.
This is the quantity RFC 2544 recommends 60 seconds for.

The search will base its results on trials of this trial duration,
but the search may use shorter durations in preparation, in order to select
promising intended loads for the final trials.
{:/comment}

### Trials Duration

Maximal allowed sum of trial durations performed by trials at the same
intended load. Upon reaching this, the search has to decide
if the load is upper or lower bound for the current criterion.
The search can decide before the maximum is reached,
if it is clear no further trial results can alter the decision.

### Theoretical Ratio Loss Load

{::comment}
    FIXME: Define (Limit) Search Criterion.
    FIXME: Should be something like Theoretical Limit Criterion Load.
{:/comment}

This is not a single notion with the word "ratio" in its name.
This is a separate notion for any possible numeric ratio value.
Examples: Theoretical zero loss load; theoretical 0.5% loss load.

For a given loss ratio goal (and final trial duration),
it is the largest offered load, that guarantees
any trial performed at this load and final trial duration
gets trial loss ratio smaller than or equal to the loss ratio goal.

{::comment}
    For a practical levels of "guarantee".
    Quantum mechanics says the probability of encountering a device with non-zero
    theoretical ratio loss load in our universe is equal to zero.
{:/comment}

Theoretical zero loss load is what RFC 1242 happens to define as throughput.

### Estimates

As the search procedure conducts trials at various offered loads
and trial durations, outcomes of those trials provide evidence related to
the theoretical ratio loss loads.

#### Upper bound

TODO: Offered load or trial outcome.
TODO: Ordering.
TODO: Dependency on trial duration.
TODO: Tightest and second tightest.

#### Lower bound

TODO: All upper bounds (within duration) have to be higher.
TODO: Effective trial loss ratio?

### Interval

Any two real numbers define a real interval in mathematics.
The two real numbers are called endpoints of the interval
(when treated as an unordered pair) or bounds (when ordered
into lower bound and upper bound).

Intended loads (in appropriate units, such as frames per second) are real numbers.
Each trial has its intended load, so trials can be used to define
load intervals.

{::comment}
In statistics, there are interval estimators,
and at each point of the search, the estimate for what the ratio loss load will be
is the interval between tightest lower bound and tightest upper bound
for that ratio.
{:/comment}

Those are motivations for this document to talk about intervals
and their endpoints and bounds (instead of pairs or similar).

#### Absolute Interval Width

Upper value minus lower value.

For trial endpoints, this is the difference in intended load,
so it is a dimensional quantity (needs a unit, for example frames per second).

#### Relative Interval Width

Absolute interval width divided by the upper value.

For trial endpoints, this is a dimensionless quantity (as the units cancel out).

As the intended load is always positive (and assuming upper value is
really the larger intended load), relative interval width is always a real number,
larger than zero and smaller than one.

### Stopping conditions

A search procedure is typically described as an interative algorithm,
so it needs some conditions to decide when to stop iterating.

#### Final Width Goal

For each loss ratio goal separately (or for all globally), user could specify
relative width value.

TODO: It seems we really need to define tightest bounds.
TODO: Mention this is "the precision".

If at final trial duration the interval between the tightest lower bound
and the tightest upper bound has relative interval width of that value or less,
that ratio loss load is known with enough precision and seach can focus
on other loss ratio goals (or return if all loss ratio goals are handled).

For the purpose of stopping, trial with max rate and final duration
acts as an upper bound even if it has smaller effective trial loss ratio.
Similarly, trial with min rate and final duration acts as a lower bound
even if it has larger effective trial loss ratio.

That means, if the ratio loss load returned is the max rate or the min rate,
it may be an invalid bound. In case of max rate it is not an issue,
SUT performs better than TG and TA are able to test.
But for min rate it probably means SUT is misconfigured or otherwise faulty.

TODO: What MUST or MAY be done in this case?

{::comment}
    #### Timeout

    TODO: Rename into "max overall duration" or similar.

    If MLRsearch detects it started more than this value ago, it SHOULD return
    in a way that signals a failure, but it still MAY return its current
    tightest lower bounds.

    This is a way to prevent spending too much time when testing an SUT.

    Benchmarking teams may want to set this value aggressively low
    so they can decide what to do with failed searches after all tests.
    Retest if failures are rare; investigate and perhaps retest with
    different input values if failures are frequent.
{:/comment}

### Ratio Loss Load

This is not a single notion with the word "ratio" in its name.
This is a separate notion for any possible numeric ratio value.
Examples: Zero loss load; 0.5% loss load.

#### Definition

For a given loss ratio goal and the set of trials done in one search run,
the ratio loss load is the largest intended load,
used in a trial conducted with the final trial duration that got
its trial loss ratio smaller or equal to the loss ratio goal,
such that no other trial conducted with the final trial duration
and a smaller or equal offered load got its trial loss ratio larger
than the loss ratio goal.

{::comment}
TODO: It is the tightest lower bound, but that requires effective loss ratio.
{:/comment}

#### Discussion

Ratio loss load is intended to be an estimate of the theoretical ratio loss load.

Zero loss load is what RFC 2544 determines as throughput
(assuming the search never tries loads larger or equal to any non-zero loss trial,
which most search procedures do, but RFC 2544 does not force this assumption).

Any final duration trial with higher loss than goal puts a hard upper bound
on what the theoretical ratio loss load can be.
There is no way to get a lower bound on the theoretical ratio loss load,
any finite set of trials might just "be lucky", and the "true" theoretical
value may be way smaller.

Seeing a trial of no larger loss ratio (below the hard upper bound)
becomes a lower bound only if we assume SUT is deterministic.
For throughput and bisection search it does not matter,
loads are selected in a way that does not reveal non-determinism.
But when searching with multiple loss ratio goals,
it becomes possible to encounter a trial with higher intended load
but smaller loss ratio.

This is why the definition is not just "largest load with small loss",
but has to care about interwening high loss trials.

# RFC2544

## Throughput search

It is useful to restate the key requirements of RFC2544
using the new terminology (see section Terminology).

The following sections of RFC2544 are of interest for this document.

* https://datatracker.ietf.org/doc/html/rfc2544#section-20
  Mentions the max load SHOULD not be larger than the theoretical
  maximum rate for the frame size on the media.

* https://datatracker.ietf.org/doc/html/rfc2544#section-23
  Lists the actions to be done for each trial,
  it also mentions loss rate as an example of trial outcome.

* https://datatracker.ietf.org/doc/html/rfc2544#section-24
  Mentions "full length trials" leading to the throughput found,
  as opposed to shorter trial durations, allowed in an attempt
  to minimize "the length of search procedure".
  This document talks about "final trial duration" and aims to
  minimize "average overall search time".

* https://datatracker.ietf.org/doc/html/rfc2544#section-26.1
  with https://www.rfc-editor.org/errata/eid422
  finaly states requirements for the search procedure.
  It boils down to "increase intended load upon zero trial loss ratio
  and decrease intended load upon non-zero trial loss ratio".

No additional constraints are placed on the load selection,
and there is no mention of an stopping conditions, i.e. when there is enough
trial measurements to proclaim the largest load with zero trial loss
(and final trial duration) to be the throughput found.

{::comment}
    The following section is probably not useful enough.

    ## Generalized search

    Note that the throughput search can be restated as a "conditional
    load search" with a specific condition.

    "increase intended load upon trial result satisfying the condition
    and decrease intended load upon trial result not satisfying the condition"
    where the throughput condition is "trial loss count is zero".

    This works for any condition that can be evaluated from a single
    trial measurement result, and is likely to be true at low loads
    and false at high loads.

    MLRsearch can incorporate multiple different conditions,
    as long as there is total logical ordering between them
    (e.g. if a condition for a target loss ratio is not satisfied,
    it is also not satisfied for any other condition which uses
    larger target loss ratio).

{:/comment}

{::comment}
    TODO: Not sure if this subsection is needed anywhere.

    ## Simple bisection

    There is one obvious and simple search algorithm which conforms
    to throughput search requirements: simple bisection.

    Input: absolute width goal, in frames per second.

    Procedure:

    1. Chose min load to be zero.
       1. No need to measure, loss count has to be zero.
       2. Use the zero load as the current lower bound.
    2. Chose max load to be the max value allowed by bandwidth of the medium.
       1. Perform a trial measurement (at the full length duration) at max load.
       2. If there is zero trial loss count, return max load as throughput.
       3. Use max load as the current upper bound.
    3. Repeat until the difference between lower bound and upper bound is
       smaller or equal to the absolute width goal.
       1. If it is, return the current lower bound as throughput.
       2. Else: Chose new load as the arithmetic average of lower and upper bound.
       3. Perform a trial measurement (at the full length duration) at this load.
       4. If the trial loss count is zero, consider the load as new lower bound.
       5. Else consider the load as the new upper bound.
       6. Jump back to the repeat at 3.

    Another possible stop condition is the overal search time so far,
    but that is not really a different condition, as the time for search to reach
    the precision goal is just a function of precision goal, trial duration
    and the difference between max and min load.

    While this algorithm can be accomodated to search for multiple
    target loss ratios "at the same time" (see somewhere below),
    it is still missing multiple improvements which give MLRsearch
    considerably better overal search time in practice.

{:/comment}

# Example Algorithm

MLRsearch.

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

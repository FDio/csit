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
  but the industry frequently allow for small but non-zero losses. (Call for non-zero loss throughput measurements.)
* Binary search takes too long when most of trials are done far
  from the evntually found throughput. (Overall test duration too long.)
* The required final trial duration and pauses between trials
  also prolong the overal search duration. (Overall test duration too long.)
* Modern DUTs show noisy trial results (noisy neighbor problem), leading to
  big spread of possible discovered throughput. (Lack of repeatability).
* The definition of throughput is not clear when trial results are inconsistent. (Handling of inconsistent trial results.)

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

{::comment}
mkonstan TODO: Update this section to align with the 1st set of points in [Purpose and Scope](#purpose-and-scope) => 4 problems?
{:/comment}

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

# MLRsearch Overview

Before we describe how MLRsearch addresses the problems,
it is useful to give a high-level overview of MLRsearch
to introduce specific terminology it uses.

## High level

As the name Multiple Loss Ratio Search implies, MLRsearch is able
to perform search for multiple loss ratio goals.

In fact, there are several input parameters tied together with loss ratio goal.
One set of such parameter values is called Search Criterion,
or just "criterion" for short.
Ordered list where each element is a criterion is called "criteria".

MLRsearch is finding which load values act as tightest lower and upper bound
for a given criterion, one criterion at a time in the given order,
until bounds for all criteria are found.
But MLRsearch imposes conditions on allowed order of criteria,
to ensure that search for next criterion cannot invalidate bounds
found for all the previous criteria.

When deciding whether a particular intended load can be a lower or upper bound
for a particular criterion, a "trial" is performed, which may consist
of one or several "sub-trials". The sub-trial is the unit that has to
satisfy restrictions from RFC 2544 (sections 23 and 24).

At various phases, MLRsearch assigns varying amount of time for the trial.
......

## Input Parameters

Some parameters are specific for a single ratio goal,
one set of such parameter values is called Search Criterion,
or just "criterion" for short. Other parameters have to affect
all criteria at once, so they act as global parameters.

### Global Parameters

Debug, max search duration, warmup duration.

#### Measurer

#### Max load

#### Min load

#### Min trial duration

#### Subtrial duration

### Criteria

#### Loss ratio goal

#### Overstep ratio

#### Final trial duration

#### Relative width goal

#### Intermediate phases

#### Expansion coefficient

## Initial Phase
## Non-Initial Phases
## Outputs

# MLRsearch properties

MLRsearch can be seen as a search algorithm which improves upon binary search
by adding several enhancements. While the overall effectiveness of MLRsearch
is quite sensitive to the way the enhancements are combined,
it is useful to describe key properties of MLRsearch in isolation,
and how do they address the problems described in the first section.

Some properties are hardcoded, other properties are tweakable.

## Early phases

This property is there primarily to shorten the overall search time.

https://datatracker.ietf.org/doc/html/rfc2544#section-24
already mentions the possibity of using shorter duration
for trials that are not part of "final determination".

In MLRsearch this is made explicit by using phases.
The final phase will be giving the search result,
but earlier phases are trying to find an approximate result
with shorter trials and coarser precision.

The idea is to get close to the final loads, so only a few loads
need to be measured at full trial duration to confirm the result.

The very first phase (instead of bisecting the whole load spectrum)
uses Forwarding rate at maximum offered load ([RFC2285](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2))
and forwarding rate measured at it.
All the other phases use upper and lower bound from the previous phase
and return new bounds valid for the improved trial duration and precision goal.

This property keeps MLRsearch unconditionally compliant with RFC2544,
unless user tweaks final trial duration to a lower value
(in which case it is still conditionally compliant).

## Multiple search criteria

This property is there to directly support non-zero loss ratio goals,
thus indirectly improving result repeatability and comparability.

MLRsearch remains unconditionally compliant as long as the user
keeps "zero loss, 60s trial" as one of the criteria.
MLRsearch handles the criteria one by one, zero-loss is the first handled,
and no subsequent trials can change the zero-loss result.

Searching for additional non-zero-loss criteria adds to the overall search duration,
but each criterion has its own tweakable precision goal and trial duration.

## Sub-trials

{::comment}
    TODO: Link to ETSI as an inspiration.
{:/comment}

This property is another approach to improve result repeatability and comparability.
Usage of any criteria that allow two or more sub-trials per load (for the zero loss goal)
makes the result non-compliant with RFC2544.

An input parameter for any search criterion is "subtrial duration".
When MLRsearch assigns shorter duration for a load (e.g. in an earlier phase),
single trial with the shorter duration is executed.
But when MLRsearch assigns longer duration, multiple sub-trials are executed
at subtrial duration.

Each sub-trial can either honor or overstep the loss goal (for each criterion).
Input parameter "overstep ratio" (for each criterion separately)
then governs what ratio of overstepped subtrials is still tolerated
when declaring that the whole trial honored the criterion.

While the usage of multiple sub-trials does not eliminate the influence of noise,
the hope is it will reduce its impact on the value reported.

Sub-trials also improve the overall search duration, as frequently
MLRsearch can detect a point when no further sub-trial results can possibly
change the decision, so they can be skipped.
Another time save comes from "upgrading" the load from a previous phase,
as sub-trials alrady measured remain valid for the next phase.

This assumes the time ovehead between trials is no too great,
as most traffic analyzers need a quiet period, because they cannot distringuish
late frames from the previous trial from the current trial frames.

## Handling inconsistent trials

The plain bisection never encounters inconsistent trials.
In a way, sub-trials expose inconsistency at the same load and duration,
but also give a rule to decide based on overstep ratio.

But both multiple loss goals and early phases create scernarios
where the search algorithm cannot ignore inconsistent trial results.

After an earlier phase, a previously valid lower (or upper) bound
is no longer significant (it has too short trial or too few subtrials),
so it has to be re-measured (or upgraded). But after that, the same load
may no longer be the same type of bound, so one bound type is missing
for bisection purposes.
MLRseach in that case starts an "external search", which is a variant
of exponential search. User can tweak "expansion coefficient"
depending on how close the new valid bound is expected to be on average.

With non-zero loss criterion, a higher load can be seen with zero loss.
From RFC1242 and RFC2544 definitions, it is not clear whether the new
zero loss load can become the throughput.
MLRsearch is "conservative" in this situation
(at least at the same trial duration), meaning the high load
is never a throughput if there is a smaller load with non-zero-loss trial result.
The criterion ordering in MLRsearch relies on this design choice
to ensure the previously completed crteria never need to be re-visited.

In future MLRsearch versions, the behavior can become tweakable,
meaning uer can request "progressive" behavior instead,
meaning the highest load with zero loss will be reported as the throughput,
regardless of smaller load non-zero loss trials.

==HERE==

# Additional Requirements

{::comment}
mkonstan TODO: Change title to "Additional Considerations". Moved somewhere else, but not sure where to, yet.
{:/comment}

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

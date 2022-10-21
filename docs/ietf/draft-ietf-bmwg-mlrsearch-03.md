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
  but the industry frequently allow for small but non-zero losses.
  (Call for non-zero loss throughput measurements.)
* Binary search takes too long when most of trials are done far
  from the evntually found throughput. (Overall test duration too long.)
* The required final trial duration and pauses between trials
  also prolong the overal search duration. (Overall test duration too long.)
* Modern DUTs show noisy trial results (noisy neighbor problem), leading to
  big spread of possible discovered throughput. (Lack of repeatability).
* The definition of throughput is not clear when trial results are inconsistent.
  (Handling of inconsistent trial results.)

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
to support both conservative settings (unconditionally compliant with RFC2544
but longer search duration and worse repeatability) and aggressive settings
(shorter search duration and better repeatability but not compliant with RFC2544).

No part of RFC2544 is intended to be obsoleted by this document.

# Problems

## Repeatability and Comparability

RFC2544 does not suggest to repeat throughput search,
and from just one throughput value, it cannot be determined
how repeatable that value is, i.e. how likely it is
for a repeated throughput search to end up with a value
less then the precision goal away from the first value.

In practice, poor repeatability is also the main cause
of poor comparability, e.g. different benchmarking teams
can test the same DUT but get different throughput values.
Additional considerations affecting comparability usually have smaller impact.

Software networking DUTs, with traffic forwarding programs running on
commercial off-the-shelf (COTS) compute server hardware,
frequently exhibit quite low repeatability of throughput results.

This is due to the throughput of software DUTs being sensitive
(in general) to server resource allocation by operating system during
runtime, as well as any interrupts or other interference with software
threads involved in frame processing.

Some benchmarking teams are trying to focus on the performance
of the main DUT, limiting the "noise" coming from interactions
with other components od SUT.
As RFC2544 is a black-box SUT measurement, it is not really possible
to filter out the noise (no realistic enough model of the noise is known).
But any alteration to RFC2544 throughput search that improves repeatability
can considered less dependent on SUT-DUT noise.

{::comment}
This document RECOMMENDS to repeat a selection of "important" tests
ten times, so users can ascertain the repeatability of the results.

TODO: How to report? Average and standard deviation?
{:/comment}

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

With software DUTs running on shared COTS servers being sensitive to any
interference with server resource allocation, many benchmarking teams
settle with non-zero small packet loss ratio as the criterion for
"a throughput".

In order to better assess the actual performance of DUT, both zero and
(small) non-zero packet loss ratio goals can be used. Intuitively both
values should be not far from each other.
Repeated wide gap between NDR and PDR indicates either
large amount interference (noisy neighbor problem)
or a fundamental problem with the DUT system (e.g. DUT interups itself
while performing some internal stateful processing).


{::comment}
    What is worse, some benchmark groups (which groups?; citation needed)
    started reporting loads that achieved only "approximate zero loss",
    while still calling that a throughput (and thus becoming non-compliant
    with RFC2544).

    Combines with:

    Ideally, modern protocols (and modern usage of old protocols) would evolve
    to tolerate small trial loss ratios, thus decreasing the importance of zero loss.
    Is there any document proving this is happening?
{:/comment}

## Long Test Duration

Long throughput search test duration becomes a problem especially when
applied to software DUTs/programs and when used as part of the
development pipeline of those programs.

Frequent test execution (e.g. per patch or nightly), number of different
tests (e.g. many different forwarding modes the DUT offers),
limited amount of physical server resources to execute those
tests, all drive the requirement to improve the search efficiency and
reduce the time taken to execute a successful throughput search.

The goal for any throughput search algorithm should be to reduce the
overall test duration, while addressing other problems.

## Inconsistent Trial Results

While RFC2544 throughput search is usually implemented as a binary search,
where each trial becomes a "hard" bound for subsequent trials,
other parts of RFC2544 suggest DUT may not always behave consistently.
......

TODO: Doesn't this belong to [Repeatability and Comparability] section?

# MLRsearch Overview

Before we describe how MLRsearch addresses the problems,
it is useful to give a high-level overview of MLRsearch
to introduce specific terminology it uses.

As the name Multiple Loss Ratio Search implies, MLRsearch is able
to perform search for multiple loss ratio goals.

In fact, there are several input parameters tied together with loss ratio goal.
One set of such parameter values is called "search criterion",
or just "criterion" for short.
Ordered list where each element is a criterion is called "criteria".

MLRsearch is finding which load values act as tightest lower and upper bound
for a given criterion (this includes the precision goal),
one criterion at a time in the given order,
until bounds for all criteria are found.
But MLRsearch imposes conditions on allowed order of criteria,
to ensure that search for next criterion cannot invalidate bounds
found for all the previous criteria.

When deciding whether a particular intended load can be a lower or upper bound
for a particular criterion, a "trial" is performed, which may consist
of one or several "sub-trials". The sub-trial is the unit that has to
satisfy restrictions from RFC 2544 (sections 23 and 24).

At various phases, MLRsearch assigns varying amount of time for the trial.

# MLRsearch features

MLRsearch can be seen as a search algorithm which improves upon binary search
by adding several enhancements. While the overall effectiveness of MLRsearch
is quite sensitive to the way the enhancements are combined,
it is useful to describe key features of MLRsearch in isolation,
and how do they address the problems described in the first section.

Some features are hardcoded, other features are tweakable.

## Early phases

This feature is there primarily to shorten the overall search time.

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
and the forwarding rate measured at it.
All the other phases use upper and lower bound from the previous phase
and return new bounds valid for the improved trial duration and precision goal.

## Multiple search criteria

This feature is there to directly support non-zero loss ratio goals,
thus indirectly improving result repeatability and comparability.
(Experience shows: the larger loss ratio goal, the more stable search result.)

MLRsearch handles the criteria one by one, zero-loss is the first handled,
and no subsequent trials can change the zero-loss result.

Searching for additional non-zero-loss criteria adds to the overall search duration,
but each criterion has its own tweakable precision goal and trial duration.

## Sub-trials

{::comment}
    TODO: Link to ETSI as an inspiration.
{:/comment}

This feature is another approach to improve result repeatability and comparability.

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
as most traffic analyzers need a quiet period, because they cannot distinguish
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
meaning user can request "progressive" behavior instead,
meaning the highest load with zero loss will be reported as the throughput,
regardless of smaller load non-zero loss trials.

## RFC 2544 compliance

The only criterion unconditionally compliant with RFC2544 is:
Zero loss ratio goal, subtrial duration equal to final trial duration,
(overstep ratio does not matter as it always myst be below one)
and final trial duration of (at least) 60 seconds.

This may restrict which other criteria can be applied in the same search,
but MLRsearch guarantees this one criterion will not be affected
by subsequent trials, and any trial result inconsistency will be resolved
in the sae way as if only the compliant criterion was run.

Sadly, the compliant criterion will still have the same low repeatibility
and comparability as vanilla bisection.
It is only the possibility of alternative criteria (non-zero loss goal,
smaller subtrial duration, or both) that offer improvements in this area.
But even for the comliant criterion, MLRsearch is worth using
for the smaller overall search time.

TODO: Pluggable measurer, sub-trial time overheads.

==HERE==

# Additional Considerations

RFC2544 can be understood as having a number of implicit requirements.
They are made explicit in this section
(as requirements for this document, not for RFC2544).

Recommendations on how to properly address the implicit requirements
are out of scope of this document.

## Reliability of Test Equipment

Both Traffic Gemerator (TG) and and Traffic Analyzer (TA)
MUST be able to handle correctly every intended load used during the search.

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

To ensure that, max load (see Input Parameters) has to be set to low enough value.
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
    
    Big buffers:
    http://www.hit.bme.hu/~lencse/publications/ECC-2017-B-M-DNS64-revised.pdf
    See page 8 and search for the word "gaming".

{:/comment}


# MLRsearch specifics

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

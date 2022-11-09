---
title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-03
date: 2022-11-09

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
    target: https://pypi.org/project/MLRsearch/0.3.0/
    title: "MLRsearch 0.3.0, Python Package Index"
    date: 2021-04

--- abstract

This document proposes improvements to [RFC 2544] throughput search by
defining a new methodology called Multiple Loss Ratio search
(MLRsearch). The main objectives for MLRsearch are to minimize the
total test duration, search for multiple loss ratios and improve
results repeatibility and comparability.

The main motivation behind MLRsearch is the new set of challenges and
requirements posed by testing Network Function Virtualization
(NFV) systems and other software based network data planes.

MLRsearch offers several ways to address these challenges, giving user
configuration options to select their way.

--- middle

{::comment}
    As we use kramdown to convert from markdown,
    we use this way of marking comments not to be visible in rendered draft.
    https://stackoverflow.com/a/42323390
    If other engine is used, convert to this way:
    https://stackoverflow.com/a/20885980
{:/comment}

# Purpose and Scope

The purpose of this document is to describe Multiple Loss Ratio search
(MLRsearch), a throughput search methodology optimized for software
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

- Allow searching with multiple loss ratio goals.
  - Each trial result can affect any criterion in principle
    (trial reuse).
- Multiple phases within one loss ratio goal search, middle ones need
  to spend less time on trials.
  - Middle phases also aim at lesser precision.
  - Use Forwarding Rate (FR) at maximum offered load
    [RFC2285, FR](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2)
    to initialize the first middle phase.
- Be conservative when encountering inconsistent results.
  - Search one criterion by one, carefully ordering them.
- Apply several load selection heuristics to save even more time
  by trying hard to avoid unnecessarily narrow intervals.

MLRsearch configuration options are flexible enough to
support both conservative settings (unconditionally compliant with RFC
2544, but longer search duration and worse repeatability) and aggressive
settings (shorter search duration and better repeatability but not
compliant with RFC 2544).

No part of RFC 2544 is intended to be obsoleted by this document.

# Problems

## Long Test Duration

Emergence of software DUTs, with frequent software updates and a
number of different packet processing modes and configurations, drives
the requirement of continuous test execution and bringing down the test
execution time.

In the context of characterising particular DUT's network performance, this
calls for improving the time efficiency of throughput search.
A vanilla bisection (at 60sec trial duration for unconditional RFC 2544
compliance) is slow, because most trials spend time quite far from the
eventual throughput.

RFC 2544 does not specify any stopping condition for throughput search,
so users can trade-off between search duration and precision goal.
But, due to exponential behavior of bisection, small improvement
in search duration needs relatively big sacrifice in the result precision.

## DUT within SUT

RFC 2285 defines:

- *DUT* as
  - The network forwarding device to which stimulus is offered and
    response measured
    [RFC2285, DUT](https://datatracker.ietf.org/doc/html/rfc2285#section-3.1.1).
- *SUT* as
  - The collective set of network devices to which stimulus is offered
    as a single entity and response measured
    [RFC2285, SUT](https://datatracker.ietf.org/doc/html/rfc2285#section-3.1.2).

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
eliminated (e.g. by pinning DUT program threads to specific CPU cores
and isolating those cores to avoid context switching). But some
noise remains after all such reasonable precautions are applied. This
noise does negatively affect DUT's network performance. We refer to it
as an *SUT noise*.

DUT can also exhibit fluctuating performance itself, e.g. while performing
some "stop the world" internal stateful processing. In many cases this
may be an expected per-design behavior, as it would be observable even
in a hypothetical scenario where all sources of SUT noise are
eliminated. Such behavior affects trial results in a way similar to SUT
noise. We use *noise* as a shorthand covering both *DUT fluctuations* and
genuine SUT noise.

A simple model of SUT performance consists of a baseline *noiseless performance*,
and an additional noise. The baseline is assumed to be constant (enough).
The noise varies in time, sometimes wildly. The noise can sometimes be negligible,
but frequently it lowers the observed SUT performance in a trial.

In this model, SUT does not have a single performance value, it has a spectrum.
One end of the spectrum is the noiseless baseline,
the other end is a *noiseful performance*. In practice, trial results
close to the noiseful end of the spectrum happen only rarely.
The worse performance, the more rarely it is seen.

Focusing on DUT, the benchmarking effort should aim
at eliminating only the SUT noise from SUT measurement.
But that is not really possible, as there are no realistic enough models
able to distinguish SUT noise from DUT fluctuations.

However, assuming that a well-constructed SUT has the DUT as its
performance bottleneck, the "DUT noiseless performance" can be defined
as the noiseless end of SUT performance spectrum. (At least for
throughput. For other quantities such as latency there will be an
additive difference.) By this definition, DUT noiseless performance
also minimizes the impact of DUT fluctuations.

In this document, we reduce the "DUT within SUT" problem to estimating
the noiseless end of SUT performance spectrum from a limited number of
trial results.

Any improvements to throughput search algorithm, aimed for better
dealing with software networking SUT and DUT setup, should employ
strategies recognizing the presence of SUT noise, and allow discovery of
(proxies for) DUT noiseless performance
at different levels of sensitivity to SUT noise.

## Repeatability and Comparability

RFC 2544 does not suggest to repeat throughput search, and from just one
throughput value, it cannot be determined how repeatable that value is.
In practice, poor repeatability is also the main cause of poor
comparability, e.g. different benchmarking teams can test the same DUT
but get different throughput values.

RFC 2544 throughput requirements (60s trial, no tolerance to single frame loss)
force the search to converge around the noiseful end of SUT performance
spectrum. As that end is affected by rare trials of significantly low
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

[RFC 1242, Throughput](https://datatracker.ietf.org/doc/html/rfc1242#section-3.17)
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
(small) loss ratio as the goal for a "throughput rate".

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
but it is not that obvious how to search for multiple goals at once,
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
throughput for non-zero-loss (and other possible repeatibility enhancements),
while being precise enough to force a specific way to resolve trial
inconsistencies.
But until such definition is agreed upon, the correct way to handle
inconsistent trial results remains an open problem.

# MLRsearch Approach

The following description intentionally leaves out some important implementation
details. This is both to hide complexity that is not important for overall
understanding, and to allow future improvements in the implementation.

## Terminology

- *trial duration*: Amount of time over which frames are transmitted
  towards SUT and DUT in a single measurement step.
  - **MLRsearch input parameter** for final MLRsearch measurements.
- *loss ratio*: Ratio of the count of frames lost to the count of frames
  transmitted over a trial duration, a.k.a. packet loss ratio. Related
  to [RFC 1242, packet loss rate](https://datatracker.ietf.org/doc/html/rfc1242#section-3.6).
  In MLRsearch loss ratio can mean either a trial result or a goal:
  - *trial loss ratio*: Loss ratio measured during a trial.
  - *loss ratio goal*: **MLRsearch input parameter**.
    - If *trial loss ratio* is smaller or equal to this,
      the trial **satisfies** the loss ratio goal.
- *load*: Constant offered load stimulating the SUT and DUT. Consistent
  with offered load [RFC 2285 Oload](https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.2).
  - MLRsearch works with intended load instead, as it cannot deal with
    situations where the offered load is considerably different than
    intended load.
- *throughput*: The maximum load at which none of the offered frames are
  dropped by the SUT and DUT. Consistent with
  [RFC 1242, Throughput](https://datatracker.ietf.org/doc/html/rfc1242#section-3.17).
- *conditional throughput*: The forwarding rate measured at the maximum
  load at which a list of specified conditions are met i.e. loss ratio
  goal and trial duration.
  - Throughput is then a special case of conditional throughput
    for zero loss ratio goal and long enough trial duration.
  - Conditional throughput is aligned with forwarding rate
    [RFC 2285 FR](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.1)
    adding trial duration to offered load (derived from loss ratio)
    required when reporting FR.
- *lower bound*: One of values tracked by MLRsearch during the search runtime.
  It is specific to the current trial duration and current loss ratio goal.
  It represents a load value with at least one trial result available.
  If the trial satisfies the current loss ratio goal,
  it is a *valid* bound (else *invalid*).
- *upper bound*: One of values tracked by MLRsearch during the search runtime.
  It is specific to the current trial duration and current loss ratio goal.
  It represents a load value with at least one trial result available.
  If the trial satisfies the current loss ratio goal,
  it is an *invalid* bound (else *valid*).
- *interval*: The span between lower and upper bound loads.
- *precision goal*: **MLRsearch input parameter**, acting as a search
  stop condition, given as either absolute or relative width goal. An
  interval meets precision goal if:
  - The difference of upper and lower bound loads (in pps)
    is not more than the absolute width goal.
  - The difference as above, divided by upper bound load (in pps)
    is not more than the relative width goal.

## Description

The MLRsearch approach to address the identified problems is based
on the following main strategies:

- MLRsearch main inputs include the following search goals and parameters:
  - One or more **loss ratio goals**.
    - e.g. a zero-loss goal and one (or more) non-zero-loss goals.
  - **Target trial duration** condition governing required trial duration
    for final measurements.
  - **Target precision** condition governing how close final lower and
    upper bound load values must be to each other for final
    measurements.
- Search is executed as a sequence of phases:
  - *Initial phase* initializes bounds for the first middle phase.
  - *Middle phase*s narrow down the bounds, using shorter trial
    durations and lower precision goals. Several middle phases can
    precede each final phase.
  - *Final phase* (one per loss ratio goal) finds bounds matching input
    goals and parameters to serve as the overal search output.
- Each search phase produces its *ending* upper bound and lower bound:
  - Initial phase may produce invalid bounds.
  - Middle and final phases produce valid bounds.
  - Middle or final phases needs at least two values to act as 
    *starting* bounds (may be invalid).
  - Each phase may perform several trial measurements, until phase's
    ending conditions are all met.
  - Trial results from previous phases may be re-used.
- Initial phase establishes the starting values for bounds, using
  forwarding rates
  [RFC 2285, FR](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.1)
  from a few trials of minimal duration, as follows:
  - 1st trial is done at *maximum offered load (MOL)*
    [RFC 2285, MOL](https://datatracker.ietf.org/doc/html/rfc2285#section-3.5.3),
    resulting in Forwarding rate at maximum offered load (FRMOL)
    [RFC 2285, FRMOL](https://datatracker.ietf.org/doc/html/rfc2285#section-3.6.2).
  - 2nd trial is done at *FRMOL*, resulting in forwarding rate at FRMOL (FRFRMOL),
    newly defined here.
  - 3rd trial is done at *FRFRMOL*, so its results are available for the next phase.
  - By default, FRMOL is used as an upper bound, FRFRMOL as a lower bound.
    - Adjustments may apply here for some cases e.g. when 2nd trial got
      zero loss or if FRFRMOL is too close to FRMOL.
- Middle phases are producing ending bounds by improving upon starting bounds:
  - Each middle phase uses the same loss ratio goal as the final phase it precedes.
    - Called *current loss ratio goal* for upper and lower bound purposes.
  - Each middle phase has its own *current trial duration*
    and *current precision goal* parameters, computed from
    MLRsearch input parameters.
    As phases progress, these parameters approach MLRsearch main input values.
    - Current trial duration starts from a configurable minimum (e.g. 1 sec)
      and increases in a geometric sequence.
    - Current precision goal always allows twice as wide intervals
      as the following phase.
  - The starting bounds are usually the ending bounds from the preceding phase.
    - Unless there are many previous trial results that are more promising.
  - Each middle phase operates in a sequence of four actions:
    1. Perform trial at the load between the starting bounds.
      - Depending on the trial result this becomes the first
        new valid upper or lower bound for current phase.
    2. Re-measure at the remaining starting lower or upper (respectively) bound.
    3. If that did not result in a valid bound, start an *external search*.
      - That is a variant of exponential search.
        - The "growth" is given by input parameter *expansion_coefficient*.
      - This action ends when a new valid bound is found.
        - Or if an already existing valid bound becomes close enough.
    4. Repeatedly bisect the current interval until the bounds are close enough.
- Final search phase operates in exactly the same way as middle phases.
  There are two reasons why it is named differently:
  - The current trial duration and current precision goal are taken directly
    from MLRsearch input parameters, e.g they are equal
    to the target trial duration and target precision.
  - The forwarding rates of the ending bounds become the output of MLRsearch.
    - Specifically, the forwarding rates of the final lower bounds
      are the conditional throughput values per given loss ratio goals.

## Enhancement: Multiple trials per load

An enhancement of MLRsearch is to introduce a *noise tolerance* input parameter.
The idea is to perform several medium-length trials (instead of a single long trial)
and tolerate a configurable fraction of them to not-satisfy the loss ratio goal.

MLRsearch implementation with this enhancement exists in FD.io CSIT project
and test results of VPP and DPDK (testpmd, l3fwd) DUTs look promising.

This enhancement would make the description of MLRsearch approach
considerably more complicated, so this document version only describes
MLRsearch without this enhancement.

# How the problems are addressed

Configurable loss ratio goals are in direct support for non-zero-loss conditional througput.
In practice the conditional throughput results' stability
increases with higher loss ratio goals.

Multiple trials with noise tolerance enhancement will also indirectly
increase result stability and it will allow MLRsearch
to add all the benefits of Binary Search with Loss Verification,
as recommended in
[RFC 9004](https://datatracker.ietf.org/doc/html/rfc9004#section-6.2)
and specified in
[TST009](https://www.etsi.org/deliver/etsi_gs/NFV-TST/001_099/009/03.04.01_60/gs_NFV-TST009v030401p.pdf).

The main factor improving the overall search time is the introduction
of middle phases. The full implementation can bring a large number of
heuristics related to how exactly should the next trial load be chosen,
but the impact of those is not as big.

The Description subsection lacks any details on how to handle inconsistent
trial results. In practice, there tend to be a three-way trade-off
between i) short overall search time, ii) result stability
and iii) how simple the definition of the returned conditional throughput can be.
The third one is important for comparability between different MLRsearch
implementations.

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

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

# MLRsearch Approach

## Terminology

- *trial_duration*: This is the intended amount of time over which
  frames are transmitted in a single measurement step.
- *loss_ratio*: Also known as packet loss ratio. It is the ratio of the count of
  frames lost divided by the count of frames transmitted, over a trial duration.
  This quantity can be used in two similar but different ways:
  - *trial_loss_ratio*: The loss ratio as measured during a trial.
  - *loss_ratio_goal*: Part of MLRsearch inputs. If a trial loss ratio
    is smaller or equal to this, we say the trial satisfies the loss ratio goal.
- *load*: Constant intended offered load (RFC 2285) stimulating the SUT and DUT.
- *throughput*: The largest load at which the trial (of suffucient duration)
  got zero loss ratio.
- *lower_bound*: One of values tracked by MLRsearch during the search.
  It is always relative to a "current" trial duration and current loss ratio goal.
  It is always a load value with (at least one) trial result available.
  If the trial satisfies the loss ratio goal, it is a valid bound (else invalid).
- *upper_bound*: One of values tracked by MLRsearch during the search.
  It is always relative to a "current" trial duration and current loss ratio goal.
  It is always a load value with (at least one) trial result available.
  If the trial satisfies the loss ratio goal, it is an invalid bound (else valid).
- *lower_upper_interval*: span between *lower_bound* and *upper_bound* loads.

## Description

The MLRsearch approach to address the identified problems is based
on the following main strategies:

- The main inputs include the following search goals and parameters:
  - One or more *loss_ratio_goals*
    - e.g. a zero-loss goal and one (or more) non-zero-loss goals.
  - Conditions governing required trial durations.
  - Conditions governing how close do the final upper and lower bounds must be
    (referred to as "precision goal"s).
- Search is executed as a sequence of phases:
  - Initial phase initialize (perhaps invalid) bounds for the next phase.
  - Intermediate phases narrow down bounds close, using short trial durations
    and low precision goals. Several intermediate phases precede each final phase.
  - Final phase (one per goal) finds bounds matching input goals and parameters
    to serve as the overal search output.
- Each search phase produces its upper bound and lower bound.
  - Initial phase may produce invalid bounds, all other phases produce valid bounds.
  - Intermediate and final phases need at least two values to track as bounds
    (may be invalid). Other trial results from previous phases
    may also be re-used.
- The single initial phase establishes the starting values for bounds, using
  forwarding rate of few trials of minimal duration (perhaps corrected
  if the first loss ratio goal is not zero):
  - 1st trial is done at max load, resulting in FRMOL, called MRR.
  - 2nd trial is done at MRR, resulting in MRR2.
  - 3rd trial is done at MRR2 so its results are available for the next phase.
  - By default, MRR is used as an upper bound, MRR2 as a lower bound.
    - Values can be manipulated here, e.g. when 2nd trial got zero loss
      or if MRR2 is too close to MRR.
......
- Middle search phases execute optimized throughput search
  - Each phase uses two common search algorithms
    - Binary search within valid lower and upper bounds
    - Variant of exponential search if one of the bounds becomes invalid
  - Each phase has *phase_trial_duration* and *phase_precision_goal* parameters set to fixed values
    - As phases progress, these parameters converge to their respective targets 
    - *phase_trial_duration*, converges from minimum (e.g. 1 sec.) towards *target_trial_duration* (e.g. 60 sec.)
    - *phase_precision_goal*, converges from minimum (e.g. 10^-1 or 200 kPPS) towards *target_precision_goal* (e.g. 10^-4 or 10 kPPS)
  - Each phase at given *phase_trial_duration* and *phase_precision_goal*
    - Iterates through *packet_loss_ratio_goals* (PLRs) in increasing order (i.e. from lower to higher PLR)
    - At given *packet_loss_ratio_goal*, searches for valid *phase_lower_bound* and *phase_upper_bound* values that meet *phase_precision_goal*
- Final search phase executes throughput search using main input parameters
  - *phase_trial_duration* is set to *target_trial_duration*, *phase_precision_goal* is set to *target_precision_goal*
  - Iterates through *packet_loss_ratio_goals* in increasing order
  - At given *packet_loss_ratio_goal*, searches for valid *phase_lower_bound* and *phase_upper_bound* values that meet *target_precision_goal*
- Final search phase produces MLRsearch results
  - Throughput is the final *phase_lower_bound* value for *packet_loss_ratio_goal* equal to zero. For compliance with RFC 2544 *target_trial_duration* must be set to 60 sec.
  - Throughput-with-PLR is the final valid *phase_lower_bound* value for each input *packet_loss_ratio_goal*

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

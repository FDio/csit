---
title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-05
date: 2023-10-xx

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
  RFC1242:
  RFC2285:
  RFC2544:
  RFC9004:

informative:
  TST009:
    target: https://www.etsi.org/deliver/etsi_gs/NFV-TST/001_099/009/03.04.01_60/gs_NFV-TST009v030401p.pdf
    title: "TST 009"
  FDio-CSIT-MLRsearch:
    target: https://csit.fd.io/cdocs/methodology/measurements/data_plane_throughput/mlr_search/
    title: "FD.io CSIT Test Methodology - MLRsearch"
    date: 2022-11
  PyPI-MLRsearch:
    target: https://pypi.org/project/MLRsearch/0.4.0/
    title: "MLRsearch 0.4.0, Python Package Index"
    date: 2021-04

--- abstract

This document proposes improvements to [RFC2544] throughput search by
defining a new methodology called Multiple Loss Ratio search
(MLRsearch). The main objectives for MLRsearch are to minimize the
total test duration, search for multiple loss ratios and improve
results repeatibility and comparability.

The main motivation behind MLRsearch is the new set of challenges and
requirements posed by testing Network Function Virtualization
(NFV) systems and other software based network data planes.

MLRsearch offers several ways to address these challenges, giving user
configuration options to select their preferred way.

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

Applying vanilla [RFC2544] throughput bisection to software DUTs
results in a number of problems:

- Binary search takes too long as most of trials are done far from the
  eventually found throughput.
- The required final trial duration (and pauses between trials) also
  prolong the overall search duration.
- Software DUTs show noisy trial results (noisy neighbor problem),
  leading to big spread of possible discovered throughput values.
- Throughput requires loss of exactly zero packets, but the industry
  frequently allows for small but non-zero losses.
- The definition of throughput is not clear when trial results are
  inconsistent.

MLRsearch aims to address these problems by applying the following set
of enhancements:

- Allow multiple shorter trials instead of one big trial per load.
  - Optionally, tolerate a percentage of trial result with higher loss.
- Allow searching for multiple search goals, with differing goal loss ratios.
  - Any trial result can affect each search goal in principle.
- Multiple preceding targets for each search goal, earlier ones need
  to spend less time on trials.
  - Earlier targets also aim at lesser precision.
  - Use Forwarding Rate (FR) at maximum offered load
    [RFC2285] (section 3.6.2) to initialize the initial targets.
- Take care when dealing with inconsistent trial results.
  - Reported throughput is smaller than smallest load with high loss.
  - Smaller load candidates are measured first.
- Apply several load selection heuristics to save even more time
  by trying hard to avoid unnecessarily narrow bounds.

MLRsearch configuration options are flexible enough to
support both conservative settings (unconditionally compliant with [RFC2544],
but longer search duration and worse repeatability) and aggressive
settings (shorter search duration and better repeatability but not
compliant with [RFC2544]).

No part of [RFC2544] is intended to be obsoleted by this document.

{::comment}

    ## Document structure

    As commonly used terms (such as throughput) are used in the context
    of the conservative settings, a new terminology is needed
    to properly introduce analogues of such terms valid also for aggressive settings.
    While detailed description of open problems can be given without
    the new terminology, the detailed description of the proposed solutions
    needs to use the new terminology.

    TODO: Finish explaining the chapter ordering.

{:/comment}

# Problems

## Long Test Duration

Emergence of software DUTs, with frequent software updates and a
number of different packet processing modes and configurations, drives
the requirement of continuous test execution and bringing down the test
execution time.

In the context of characterising particular DUT's network performance, this
calls for improving the time efficiency of throughput search.
A vanilla bisection (at 60sec trial duration for unconditional [RFC2544]
compliance) is slow, because most trials spend time quite far from the
eventual throughput.

[RFC2544] does not specify any stopping condition for throughput search,
so users can trade-off between search duration and achieved precision.
But, due to exponential behavior of bisection, small improvement
in search duration needs relatively big sacrifice in the throughput precision.

## DUT within SUT

[RFC2285] defines:
- *DUT* as
  - The network forwarding device to which stimulus is offered and
    response measured [RFC2285] (section 3.1.1).
- *SUT* as
  - The collective set of network devices to which stimulus is offered
    as a single entity and response measured [RFC2285] (section 3.1.2).

[RFC2544] specifies a test setup with an external tester stimulating the
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
The worse performance, the more rarely it is seen in a trial.

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

[RFC2544] does not suggest to repeat throughput search. And from just one
throughput value, it cannot be determined how repeatable that value is.
In practice, poor repeatability is also the main cause of poor
comparability, e.g. different benchmarking teams can test the same SUT
but get different throughput values.

[RFC2544] throughput requirements (60s trial, no tolerance to single frame loss)
force the search to fluctuate close the noiseful end of SUT performance
spectrum. As that end is affected by rare trials of significantly low
performance, the resulting throughput repeatability is poor.

The repeatability problem is the problem of defining a search procedure
which reports more stable results
(even if they can no longer be called "throughput" in [RFC2544] sense).
According to baseline (noiseless) and noiseful model, better repeatability
will be at the noiseless end of the spectrum.
Therefore, solutions to the "DUT within SUT" problem
will help also with the repeatability problem.

Conversely, any alteration to [RFC2544] throughput search
that improves repeatability should be considered
as less dependent on the SUT noise.

An alternative option is to simply run a search multiple times, and report some
statistics (e.g. average and standard deviation). This can be used
for "important" tests, but it makes the search duration problem even
more pronounced.

## Throughput with Non-Zero Loss

[RFC1242] (section 3.17) defines throughput as:
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
[RFC2544] throughput is not friendly in this regard.

Searching for multiple goal loss ratios also helps to describe the SUT
performance better than a single goal result. Repeated wide gap between
zero and non-zero loss conditional throughputs indicates
the noise has a large impact on the overall SUT performance.

It is easy to modify the vanilla bisection to find a lower bound
for intended load that satisfies a non-zero-loss goal,
but it is not that obvious how to search for multiple goals at once,
hence the support for multiple loss goals remains a problem.

## Inconsistent Trial Results

While performing throughput search by executing a sequence of
measurement trials, there is a risk of encountering inconsistencies
between trial results.

The plain bisection never encounters inconsistent trials.
But [RFC2544] hints about possibility if inconsistent trial results in two places.
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
Definitions of throughput in [RFC1242] and [RFC2544] are not specific enough
to imply a unique way of handling such inconsistencies.

Ideally, there will be a definition of a quantity which both generalizes
throughput for non-zero-loss (and other possible repeatibility enhancements),
while being precise enough to force a specific way to resolve trial
inconsistencies.
But until such definition is agreed upon, the correct way to handle
inconsistent trial results remains an open problem.

# Introduction to MLRsearch

This chapter focuses on motivations and skips over some important details.
See the following chapter for those.

The MLRsearch algorithm has been developend in a code-first approach,
a Python library has been created, debugged and used in production
before first descriptions (even informal) were published.
In fact, multiple version were used in production over past few years,
and later code was usually not compatible with earlier descriptions.

This document aspires to describe MLRsearch class of algorithms
in a way that captures the important parts related to comparability,
while keeping time optimizations vague enough, so that multiple implementations
(including future versions of MLRsearch Python library) can freely add
(or remove) optimizations while staying compatible with this document.

This chapter also skims over details that are important
for declaring (some configurations of) MLRsearch as compliant with RFC 2544,
for example maximum frame rate from RFC 2544 section 20,
as those details are not as important from explainability point of view.

As the history of MLRsearch development can be seen as a process
of continued generalization of MLRsearch throughput search procedure,
this chapter also introduces new features of MLRsearch as such generalizations
(although chronologically the earlier versions of MLRsearch library
were adopting the new features in a different order, with multiple takebacks).

## Exit condition

RFC 2544 prescribes that after performing one trial at a specific offered load,
the next offered load should larger or smaller, based on frame loss.

The usual implementation uses binary search. Here a lossy trial becomes
a new tightest upper bound, a lossless trial becomes a new tightest lower bound,
and after each trial the distance between the bounds halves.
After some number of trials, the tightest lower bound becomes the throughput.

RFC 2544 does not specify when (if ever) should the search stop.
MLRsearch introduces the concept of width. The search stops
when the distance between the tightest upper bound and the tightest lower bound
is smaller than some user-configured value, called "width" from now on.

## Load Classification

MLRsearch keeps the basic logic (tracking bounds, measuring at the middle),
perhaps with a minor technical clarifications.
The algorithm chooses an intended load (as opposed to offered load),
interval between bounds does not need to be split exactly in two equal halves,
and the final reported value is the conditional throughput
(related to forwarding rate, defined later).

The biggest difference is that in order to classify a load
as an upper or lower bound, MLRsearch may need more than one trial
(depending on configuration options) to be performed using the same load.

As a consequence, even if a load already does have few trial results,
it still may be classified as undecided, neither a lower bound nor an upper bound.

## Loss ratios

Next difference is in goals of the search. RFC 2544 has a single goal,
based on classifying full-length trials as either loss-less or lossy.

As the name suggests, MLRsearch can seach for multiple goals, differing in their
loss ratios. Precise definition of goal loss ratio will be given later.
The RFC 2544 throughput goal then simply becomes a zero goal loss ratio.
Different goals also may have different goal width.

A set of trial results for one specific intended load value
can classify the load as an upper bound for some goals, but a lower bound
for some other goals, and undecided for the rest of the goals.

Therefore, the load classification depends not only on the load value,
but also on the goal. The overall search procedure becomes more complicated,
but most of the complications do not affect the final result,
except for one phenomenon, loss inversion.

## Loss inversion

In RFC 2544 throuhput search using bisection, any load with lossy trial
becomes a hard upper bound, meaning every subsequent trials have smaller loads.

But in MLRsearch, a load that is classified as an upper bound for one goal
may still be a lower bound for another goal, and due to that other goal
MLRsearch will probably perform trials at even higher loads.
What to do when all such higher load trials happen to have zero loss?
Does it mean the earlier upper bound was not real?
Does it mean the later lossless trials are not considered a lower bound?
Surely we do not want to have an upper bound at a load smaller than a lower bound.

MLRsearch is conservative in these situations.
The earlier upper bound is considered real, the later lossless trials
are considered to be a coincidence, at least when computing the final result.

This is formalized using new notions, "relevant upper bound" and
"relevant lower bound".
Load classification is still based just on the set of trial results
at a given intended load (trials at other loads are ignored),
making it possible to have a lower load classified as an upper bound
and a higher load classified as a lower bound (for the same goal).
The relevant upper bound (for a goal) is the smallest load classified
as an upper bound. But the relevant lower bound is not simply
the larget amongst lower bounds. It is the largest load among loads
that are lower bounds while also being smaller than the relevant upper bound.

With these definitions, the relevant lower bound is always smaller
than the relevant upper bound (if both exist), and the two relevant bounds
are used analogously as the two tightest bounds in the binary search.
(When they are less than width apart, the relevant lower bound is used for output.)

## Exceed ratio

The idea of performing multiple trials at the same load comes from
a model where some trial results (those with high loss) are affected
by infrequent effects, causing poor repeatability of RFC 2544 throughput results.
See the discussion about noisy and noiseless ends of SUT performance spectrum.

MLRsearch is able to do such trial result filtering, but it needs
a configuration option to tell it how much frequent is "infrequent".
This option is called exceed ratio. It tells MLRsearch what ratio of trials
(more exactly what ratio of trial seconds) can have trial loss ratio
larger than goal loss ratio and still be classified as a lower bound.
Zero exceed ratio means all trials have to have trial loss ratio
equal to or smaller than the goal loss ratio.

For explainability, the recommended value for exceed ratio is 0.5,
as it simplifies some later concepts by relating them to the concept of median.

## Duration sum

When more than one trial is needed to classify a load,
MLRsearch needs something that controlls the number of trials needed.
Therefore, each goals also has an attribute called duration sum.

The meaning of a goal duration sum is that when a load has trials
(at full trial duration, details later)
whose trial durations when summed up give a value at least this,
the load is guaranteed to be classified as an upper bound or a lower bound
for the goal.

## Short trials

Section 24 of RFC 2544 already anticipates possible time savings
when short trials (shorter than full length trials) are used.

MLRsearch requires each goal to specify its final trial duration.
Full-length trial is the short name for a trial which intended trial duration
is equal to the goal final trial duration.

Any MLRsearch implementation may include its own configuration options
which control when and how MLRsearch chooses to use shorter trial durations.

For explainability reasons, when exceed ratio of 0.5 is used,
it is recommended for the goal duration sum to be an odd multiple
of the full trial durations, so conditional throughput becomes identical to
a median of a particular set of forwarding rates.

Presence of shorter trial results complicates load classification.
Full details are given later. In short, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the relevant lower bound
(below what would classification say when considering full-length trials only).

For explainability reasons, it is RECOMMENDED users use such configurations
that guarantee all trials have the same length.
Alas, such configurations are usually not compliant with RFC 2544 requirements
(or not time-saving enough).

## Optimizations

The main motivation for MLRsearch was to have an algorithm that spends less time
finding a throughput, either the RFC 2544 compliant one,
or some generalization thereof. The art of achieving short search times
is mainly in smart selection of intended loads (and intended durations)
for the next trial to perform.

While there is an indirect impact of the load selection on the reported values
(mainly through different probabilities of triggering the inversion loss scenario
at lower or higher loads), in practice such impact tends to be small,
even for SUTs with quite broad performance spectrum.

Therefore, this document remains quite vague on load selection
and other optimisations (and configuration attributes related to them).
The definition of the tightest lower bound
should be strict enough to ensure result repeatability
(and comparability between different implementations)
while not restricting future implementations much.

## Conditional throughput

As testing equipment takes intended load as input parameter
for a trial measurement, any "load search" algorithm needs to deal
with intended load values internally.

But in presence of goals with non-zero loss ratio, the intended load
usually does not match the user intuition of what a throughput is.
The forwarding rate (as defined in RFC 2285 section 3.6.1) is better,
but it is not obvious how to generalize it
for loads with multiple trial results,
especially with non-zero goal exceed ratio.

MLRsearch defines one such generalization, called conditional throughput.
It is the forwarding rate from one of the trials performed at the load
in question. Specification of which trial exactly is quite technical
(see next subsection).

Conditional throughput is partially related to load classification.
If a load is classified as a lower bound for a goal,
the conditional throughpt can be calculated,
and guaranteed to show (effective) loss ratio no larger than goal loss ratio.

## Technical details

TODO: Separate motivations from pure definitions,
so the definitions may get referenced from next chapter.

### Performance spectrum

There are several equivalent ways to define conditional throughput computation.
One of the ways relies on an object called the performance spectrum.
First, two heavy definitions are needed.

Take an intended load value, and a (finite) set of trial results, all trials
measured at that load value. The performance spectrum is the function that maps
any non-negative real number into a sum of trial durations among all trials
in the set that have that number as their forwarding rate
(e.g. map to zero if no trial has that particular forwarding rate).

A related function (defined if there is at least one trial in the set)
is the performance spectrum divided by sum of durations of all trials in the set.
That function is called a performance probability function, as it satisfies
all the requirements for probability mass function function
of a discrete probability distribution,
the one-dimensional random variable being the trial forwarding rate.

These functions are related to the SUT perfomance spectrum,
as sampled by the trials in the set.

As for any other probability function, we can talk about percentiles
(and other quantiles, such as the median)
of the performance probability function. The conditional throughput will be
one such quantile value for a specific set of trials.

Take a set of all full-length trials performed at the load in question.
The sum of durations of those trials may be less than goal duration sum, or not.
If it is less, add an imaginary trial result with zero forwarding rate
such that the new sum of durations is equal to the goal duration sum.
This is the set of trials to use. The q value for the quantile
is the goal exceed ratio. If the quantile touches two trials,
the larger forwarding rate is used.

First example. For zero exceed ratio, the conditional throughput
is the smallest forwarding rate among the trials, so zero if the imaginary
trial has been added.

Second example. Exceed ratio 50%, goal duration sum two seconds,
one trial present with duration one second and zero loss.
Imaginary trial is added with duration one second and zero forwarding rate.
Median would touch both trials, so the conditional throughput
is the forwarding rate of the one non-imaginary trial.
As that had zero loss, the value is equal to the offered load.

### Load classification details

The classification does not need the whole performance spectrum,
only few duration sums.

A trial is called bad (according to a goal) if its trial loss ratio
is larger than the goal loss ratio. Trial that is not bad is called good.

#### Single trial duration

When goal attributes are chosen in such a way that every trial has the same
intended duration, the load classification is sipler.

The following description looks technical, but it follows the motivation
of goal loss ratio, goal exceed ratio and goal duration sum.
If sum of durations of all trials (at given load) is less than the goal
duration sum, imagine best case scenario (all subsequent trials having zero loss)
and worst case scenario (all subsequent trials having 100% loss).
If even in the best case scenario the load exceed ratio would be larger
than the goal exceed ratio, the load is an upper bound.
If even in the worst case scenario the load exceed ratio would not be larger
than the goal exceed ratio, the load is a lower bound.

Even more specifically.
Take all trials measured at a given load.
Sum of durations of all bad full-length trials is called the bad sum.
Sum of durations of all good full-length trials is called the good sum.
The result of adding bad sum plus the good sum is called the measured sum.
The larger of the measured sum and the goal duration sum is called the whole sum.
The whole sum minus the measured sum is called the missing sum.
Optimistic exceed ratio is the bad sum divided by the whole sum.
Pessimistic exceed ratio is the bad sum plus the missing sum, that divided by
the whole sum.
If optimistic exceed ratio is larger than the goal exceed ratio,
the load is classified as an upper bound.
If pessimistic exceed ratio is not larger than the goal exceed ratio,
the load is classified as a lower bound.
Else, the load is classified as undecided.

The definition of pessimistic exceed ratio matches the logic in
the conditional throughput computation, so a load is a lower bound
if and only if the conditional throughput effective loss ratio
is not larger than the goal loss ratio.
If it is larger, the load is either an upper bound or undecided.

#### Shorter trial durations

Trials with intended duration smaller than the goal final trial duration
are called short trials.
The motivation for load classification logic in presence of short trials
is based around a counter-factual scenario: What would the trial result be
if a short trial has been measured at goal final trial duration instead?

On one hand, the user had their reason for not configuring shorter goal
final trial duration. Perhaps SUT has buffers that may get full at longer
trial durations. Perhaps SUT shows periodic decreases of performance
the user does not want to treat as noise. In any case, many good short trials
may became bad full-length trial in the counter-factual scenario.

On the other hand, when there is a frame loss in a short trial,
the counter-factual full-length trial is expected to lose at least as many
frames. And in practice, bad short trials are rarely turning into
good full-length trials.

On third hand, some SUTs are quite indifferent to trial duration.
Performance probability function constructed from short trial results
is likely to be similar to performance probability function constructed
from full-length trial results (perhaps with smaller dispersion,
but without big impact on quantiles).

MLRsearch picks a particular logic for load classification
in presence of short trials, but it is still RECOMMENDED to use configurations
that imply no short trials, so the possible inefficiencies in that logic
do not affect the result, and the result has better explainability.

With thas said, the logic differs from the single trial duration case
only in different definition of bad sum.
Good sum is still the sum across all good full-length trials.

Few more notions are needed for definig the new bad sum.
Sum of durations of all bad full-length trials is called the bad long sum.
Sum of durations of all bad short trials is called the bad short sum.
Sum of durations of all good short trials is called the good short sum.
One minus the goal exceed ratio is called the inceed ratio.
The goal exceed ratio divided by the inceed ratio is called the exceed coefficient.
The good short sum multiplied by the exceed coefficient is called the balancing sum.
The bad short sum minus the balancing sum is called the excess sum.
If the excess sum is non-positive, the bad sum is equal to the bad long sum.
Else, the bad sum is equal to the bad long sum plus the excess sum.

TODO: Spell out how this logic addresses all three hands.

#### Longer trial durations

If there are trial results with intended duration larger
than the goal trial duration, the classification logic is intentionally undefined.

The implementations MAY treat such longer trials as if they were full-length.
In any case, presence of such longer trials in either the relevant lower bound
or the relevant upper bound SHOULD be mentioned.

## Inputs and outputs

TODO: And overview of equired and optional attributes will be here.
Perhaps mov it elsewehre, so "other specifics" can be referenced.

## Other specifics

TODO: Units!

TODO: Bidirectional (and multi-port in general) value.

TODO: Cases where offered load differs from intended load are out of scope.

TODO: Max load and its requirements from other RFCs.

TODO: Min load.

TODO: Frame verification (RFC 2544 section 10) is out of scope in general.

TODO: Absolute or relative width.

TODO: Logarithmic loads.

TODO: Fast fail.

TODO: Timeout.

TODO: Trial duration with overheads?

TODO: Review which settings are compliant with RFC 2544 here?

TODO: More recommendations on which settings are nice:
* Longer duration sum for PDR can destabilize previously found NDR.
* Really try to avoid mismatching final trial durations.
* Stick to integer durations, so floating point rounding errors
  cannot mess with the conditional throughput computation.

TODO: Recommendations for implementations:
* Be really careful around floating point rounding of load and width values.
* Logging?

TODO: Do not forget about Optimization recommendation section somewhere.
* Strategies (including halving and bounded external search).
* Global width.
* Uneven interval splits.

# Definitions

This chapter focuses on technical definitions needed for evaluating
whether a particular test procedure belongs to a class of MLRsearch algorithms.
For motivations, explanations, and other comments see the previous chapter.

Some definitions are direct copies from other documents.
Other are intended only for internal use in this ducument,
whether the terms are new, or just generalizations of terms defined elsewhere.

## SUT

As defined in RFC 2285:
The collective set of network devices to which stimulus is offered
as a single entity and response measured.

## Trial

A trial is the part of test described in RFC 2544 section 23.

## Load

Intended constant load for a trial, usually in frames per second.

Load is the general quantity implied by Constant Load of RFC 1242,
Data Rate of RFC 2544 and Intended Load of RFC 2285.
All three specify this value applies to one (input or output) interface.

## Duration

Intended duration of the traffic for a trial, usually in seconds.

This general quantity does not include any preparation nor waiting
described in section 23 of RFC 2544.

## Trial Forwarding Ratio

Dimensionless floating point value assumed to be
between 0.0 and 1.0, both including.
It is computed as the number of frames forwarded by SUT, divided by
the number of frames that should have been forwarded during the trial.

Note that, contrary to load, frame counts used to compute
trial forwarding ratio are aggregates over all SUT ports.

## Trial Loss Ratio

One minus the trial forwarding ratio.

## Trial Forwarding Rate

Load multiplied by trial forwarding ratio.

Note that this is very similar, but not identical to Forwarding Rate
as defined in RFC 2285 section 3.6.1, as that definition
is specific to one output interface, while trial forwarding ratio
is based on frame counts aggregated over all SUT interfaces.

## MLRsearch Architecture

MLRsearch architecture consists of three main components:
the manager, the controller and the measurer.
Presence of other components (mainly the SUT) is also implied.

While the manager and the measurer can be seen a abstractions
present in any testing procedure

### Manager

The manager is the component that initializes SUT, traffic generator
(called tester in RFC 2544), the measurer and the controller
with intended configurations. It then hands over the execution
to the controller and receives its result.

Creation of reports of appropriate format can also be understood
as the responsibility of the manager.

### Measurer

The measurer is the component which performs one trial
as described in RFC 2544 section 23, when requested by the controller.

Specifically, one call to the measurer turns trial load and trial duration,
into trial loss ratio.

It is responsibility of the measurer to uphold any requirements.
Implementers have some freedom, for example in the way they deal with
duplicated frames, or what to return if tester sent zero frames towards SUT.

### Controller

The controller is the component of MLRsearch architecture
that is called by the manager (usually just once), calls the measurer
(usually multiple times in succession),
and returns the Search Result to the manager.

While the manager and the measurer can be seen a abstractions
present in any testing procedure, the behavior of the controller
is what distinguishes MLRsearch class of algorithms from others.

The only required argument in the call to the controller
is a list of search goals (defined below).

## Search goal

A composite consisting of several attributes, some of them are required.
Implementations are free to add their own attributes.

Subsections list all required attributes.

### Goal loss ratio

A threshold value for trial loss ratios.
MUST be non-negative and smaller than one.

### Goal final trial duration

A threshold value for trial durations.
MUST be positive.

### Goal duration sum

A threshold value for a particular sum of trial durations.
MUST be positive.

### Goal exceed ratio

A threshold value for particular ratio of duration sums.
MUST be non-negative and smaller than one.

### Goal width

A value used as a threshold for telling when two trial load values
are close enough.

Absolute difference and relative difference are two popular options,
but implementations may choose otherwise.
In extreme, this can be implemented as an injectable function accepting
two load values.

## Search result

This is a single composite object returned from the controller to the manager.
It is a mapping from the search goals (the same list as the controller got
as its required arument) into goal results (defined in the next subsection).

Each search goal instance is mapped to a goal result instance.
Multiple search goal instances may map to the same goal result instance.

## Goal result

A composite object consisting of several attributes, all related to
one search goal (the one the search result is mapping to this instance).

Some of the attributes are required, some are recommended,
implementations are free to add their own.

The subsections define attributes for regular goal result.
Implementations are free to define their own irregular goal results,
but the manager MUST report them clearly as not regular according to this section.

### Relevant lower bound

The intended load value that got classified (after all trials) as the relevant
lower bound (see TODO) for this goal. This is a REQUIRED attribute.

### Relevant upper bound

The intended load value that got classified (after all trials) as the relevant
upper bound (see TODO) for this goal. This is a RECOMMENDED attribute.

The distance between relevant lower bound and the relevant upper bound
cannot be larger than the goal width.

Note: While any reasonable implementation of MLRsearch does track
the relevant upper bound value, some implementations may omit returning it
for brevity reasons.

TODO: Make REQUIRED so that hitting max load is an irregular goal result.

### Conditional throughput

The conditional throughput (see TODO) as evaluated at the relevant lower bound.
This is a RECOMMENDED attribute.

Note: While the conditional throughput gives more intuitive-looking values,
the actual definition is more complicated than the definition of the relevant
lower bound. In future, other values may become popular,
but they are unlikely to supersede the relevant lower bound
as the most fitting value for comparability purposes,
therefore the relevant lower bound remains the only required attribute
of the goal result structure.

{::comment}

    The following subsections are still likely to be useful for some TODO.

    ?? Units

    In practice, it is required to know which unit of measurement
    is used to accompany a numeric value of each quantity.
    The choice of a particular unit of measurement is not important
    for MLRsearch specification though, so specific units
    mentioned in this document are just examples or recommendations,
    not requirements.

    When reporting, it is REQUIRED to state the units used.

    ?? Width

    The motivation for the name comes from binary search.
    The binary search tries to approximate an unknown value
    by repeatedly bisecting an interval of possible values
    until the interval becomes narrow enough.
    Width of the interval is a specific quantity
    and the termination condition compares that
    to another specific quantity acting as the threshold value.
    The threshold value does not have a specific interval associated with it,
    but corresponds to a 'size' of the compared interval.
    As 'size' is a word already used in definition of frame size,
    a more natural word describing interval is width.

    The MLRsearch specification does use (analogues of) upper bound
    and lower bound, but does not actually need to talk about intervals.
    Still, the intervals are implicitly there, so width is the natural name.

    In practice, there are two popular options for defining width.
    Absolute width is based on load, the value is the higher load
    minus the lower load.
    Relative width is dimensionless, the value is the absolute width
    divided by the higher load. As intended loads for trials are positive,
    relative width is between 0.0 (including) and 1.0 (excluding).

    Relative width as a threshold value may be useful for users
    who do not presume what is the typical performance of SUT,
    but absolute width may be a more familiar concept.

    MLRsearch specification does not prescribe which width has to be used,
    but widths MUST be either all absolute or all relative,
    and it MUST be clear from report which option was used
    (it is implied from the unit of measurement of any width value).

    ?? Traffic profile

    Any other configuration values needed by the measurer to perform a trial.

    The measurer needs both trial input and traffic profile to perform the trial.
    As trial input contains the only values that vary during one the search,
    traffic profile remains constant during the search.

    Traffic profile when understood as a composite is REQUIRED by RFC 2544
    to contain some specific quantities (for example frame size).
    Several more specific quantities may be RECOMMENDED.

    Depending on SUT configuration (e.g. when testing specific protocols),
    additional values need to be included in the traffic profile
    and in the test report. (See other IETF documents.)

    ?? Max load

    Max load is a specific quantity based on load.
    No trial load is ever higher than this value.

    RFC 2544 section 20 defines maximum frame rate
    based on theoretical maximum rate for the frame size on the media.
    RFC 2285 section 3.5.3 specifies Maximum offered load (MOL)
    which may be lower than maximum frame rate.
    There may be other limitations preventing high loads,
    for examples resources available to traffic generator.

    The manager is expected to provide a value that is not greater
    than any known limitation. Alternatively, the measurer
    is expected to work at max load, possibly reporting as lost
    any frames that were not able to leave Traffic Generator during the trial.

    From the controller point of view, this is merely a global upper limit
    for any trial load candidates.

    ?? Min load

    Min load is a specific quantity based on load.
    No trial load is ever lower than this value.

    The motivation of this quantity is to prevent trials
    with too few frames sent to SUT.

    Also, practically, if a SUT is able to reach only very small
    forwarding rates (min load indirectly serves as a threshold for how small),
    it may be considered faulty (or perhaps the test is misconfigured).

{:/comment}

# How The Problems Are Addressed

TODO: Does this have to go last? It mentions notions from Optimization,
but those may be made more vague.

## Long Test Duration

TODO: Multiple unspecified Optimization.

TODO: Short trial durations.

TODO: Goal duration sum remains the best way to get even shorter searches.

TODO: Small gain also from multiple trials per load.

TODO: The farther the goal exceed ratio is from 0.5, the less predictable
the overal search duration becomes.

TODO: Width parameter does not change search duration much in practice.

TODO: Mention duration with overheads here?

TODO: Be more explicit on waits between trials (RFC 2544 requirements)?

## DUT within SUT

TODO: Big improvements when multiple trials and moderate exceed ratios are used.

TODO: Conditional throughput has somewhat intuitive meaning
when described using performance spectrum.

TODO: Multiple trials can save time also when the noisy end of
the preformance spectrum needs to be examined, e.g. for RFC 9004.

## Repeatability and Comparability

TODO: Multiple trials improve repeatability, depending on exceed ratio.

TODO: In practice, 1s trial with exceed ratio 0.5 is good enough.

TODO: Not clear whether higher exceed ratios are better.

TODO: Prepare some simulator results for presentation
(using PLRsearch fitting functions),
but I bet different SUTs have different ideal exceed ratios.

TODO: Is the v8 conditional throughput more repeatable than lowerbound for PDR?
lowerbound is discretized, which can be both good and bad thing.

TODO: Larger adoption needed to claim comparability,
but I do not expect big differences from repeatability.

## Throughput with Non-Zero Loss

TODO: Done by goal loss ratio. Improves repeatability as expected.

## Inconsistent Trial Results

TODO: MLRsearch is conservative wherever possible,
this is built into the definition of conditional throughput.

TODO: This is consistent with RFC 2544 zero loss tolerance motivation.

TODO: Implementations may be configurable to be more progressive,
but for comparability one option should be preferred,
and conservative approach s more user fiendly.

TODO: Not investigated using simulator yet.

{::comment}

    Another batch of copyable text.

    Configurable loss ratio in MLRsearch search goals are there
    in direct support for non-zero-loss conditional throughput.
    In practice the conditional throughput results' stability
    increases with higher loss ratio goals.

    Multiple trials with noise tolerance enhancement,
    as implemented in MLRsearch using non-zero goal exceed ratio value,
    also indirectly increases the result stability.
    That allows MLRsearch to achieve all the benefits
    of Binary Search with Loss Verification,
    as recommended in [RFC9004] (section 6.2)
    and specified in [TST009] (section 12.3.3).

    The main factor improving the overall search time is the introduction
    of preceding targets. Less impactful time savings
    are achieved by pre-initial trials, halving mode
    and smart splitting in bisecting mode.

    In several places, MLRsearch is "conservative" when handling
    (potentially) inconsistent results. This includes the requirement
    for the relevant lower bound to be smaller than any upper bound,
    the unequal handling of good and bad short trials,
    and preference to lower load when choosing the winner among candidates.

    While this does no guarantee good search stability
    (goals focusing on higher loads may still invalidate existing bounds
    simply by requiring larger min duration sums),
    it lowers the change of SUT having an area of poorer performance
    below the reported conditional througput loads.
    In any case, the definition of conditional throughput
    is precise enough to dictate "conservative" handling
    of trial inconsistencies.

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

---
title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-05
date: 2023-10-23

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
    date: 2023-10
  PyPI-MLRsearch:
    target: https://pypi.org/project/MLRsearch/0.4.1/
    title: "MLRsearch 0.4.1, Python Package Index"
    date: 2021-07

--- abstract

This document proposes extensions to [RFC2544] throughput search by
defining a new methodology called Multiple Loss Ratio search
(MLRsearch). The main objectives of MLRsearch are to minimize the
total search duration, to support searching for multiple loss ratios
and to improve results repeatability and comparability.

The main motivation behind extending [RFC2544] is the new set of challenges
and requirements posed by evaluating and testing software based networking
systems, specifically their data planes.

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
(MLRsearch), a data plane throughput search methodology optimized for software
networking DUTs.

Applying vanilla [RFC2544] throughput bisection to software DUTs
results in a number of problems:

- Binary search takes too long as most of trials are done far from the
  eventually found throughput.
- The required final trial duration and pauses between trials also
  prolong the overall search duration.
- Software DUTs show noisy trial results,
  leading to a big spread of possible discovered throughput values.
- Throughput requires loss of exactly zero frames, but the industry
  frequently allows for small but non-zero losses.
- The definition of throughput is not clear when trial results are inconsistent.

MLRsearch library aims to address these problems by applying the following set
of enhancements:

- Allow multiple shorter trials instead of one big trial per load.
  - Optionally, tolerate a percentage of trial result with higher loss.
- Allow searching for multiple search goals, with differing loss ratios.
  - Any trial result can affect each search goal in principle.
- Insert multiple coarse targets for each search goal, earlier ones need
  to spend less time on trials.
  - Earlier targets also aim for lesser precision.
  - Use Forwarding Rate (FR) at maximum offered load
    [RFC2285] (section 3.6.2) to initialize the initial targets.
- Take care when dealing with inconsistent trial results.
  - Reported throughput is smaller than smallest load with high loss.
  - Smaller load candidates are measured first.
- Apply several load selection heuristics to save even more time
  by trying hard to avoid unnecessarily narrow bounds.

Some of these enhancements are formalized as MLRsearch specification,
the remaining enhancements is treated as implementation details,
thus achieving high comparability without limiting future improvements.

MLRsearch configuration options are flexible enough to
support both conservative settings (unconditionally compliant with [RFC2544],
but longer search duration and worse repeatability) and aggressive
settings (shorter search duration and better repeatability but not
even conditionally compliant with [RFC2544]).

No part of [RFC2544] is intended to be obsoleted by this document.

# Problems before MLRsearch

This chapter describes the problems affecting usability
of various preformance testing methodologies,
mainly a binary search for [RFC2544] unconditionally compliant throughput.

The last chapter will summarize how the problems are addressed,
the middle chapters provide explanations and definitions needed for that.

## Long Search Duration

Emergence of software DUTs, with frequent software updates and a
number of different frame processing modes and configurations,
has increased both the number of performance tests requred to verify DUT update
and the frequency of running those tests.
This makes the overall test execution time even more important than before.

In the context of characterising particular DUT's network performance,
this calls for improving the time efficiency of throughput search.
A vanilla bisection (at 60sec trial duration for unconditional [RFC2544]
compliance) is slow, because most trials spend time quite far from the
eventual throughput.

[RFC2544] does not specify any stopping condition for throughput search,
so users can trade-off between search duration and achieved precision.
But, due to logarithmic nature of bisection, even small improvement
in search duration needs relatively big sacrifice in the precision of the
discovered throughput.

## DUT in SUT

[RFC2285] defines:
- DUT as
  - The network forwarding device to which stimulus is offered and
    response measured [RFC2285] (section 3.1.1).
- SUT as
  - The collective set of network devices to which stimulus is offered
    as a single entity and response measured [RFC2285] (section 3.1.2).

[RFC2544] specifies a test setup with an external tester stimulating the
networking system, treating it either as a single DUT, or as a system
of devices, an SUT.

In case of software networking, the SUT consists nt only of the DUT
as a software program processing frames, but also of
a server hardware and operating system functions,
with server hardware resources shared across all programs
and the operating system running on the same server.

The DUT is effectively nested within the rest of the SUT.

Due to a shared multi-tenant nature of SUT, DUT is subject to
possible interference coming from the operating system and any other
software running on the same server. Some sources of such interference
can be to some degree eliminated, e.g. by pinning DUT program threads
to specific CPU cores and isolating those cores to avoid context switching.
But some level of adverse effects may remain even after
all such reasonable precautions are applied.
These effects affect DUT's network performance negatively.
As the effects are hard to predict in general, they have impact similar to
what other engineering disciplines define as a noise.
Thus, all such effects are called an SUT noise.

DUT can also exhibit fluctuating performance itself, for reasons
not related to the rest of SUT, for example due to pauses in execution
as needed for internal stateful processing. In many cases this
may be an expected per-design behavior, as it would be observable even
in a hypothetical scenario where all sources of SUT noise are eliminated.
Such behavior affects trial results in a way similar to SUT noise.
As the two phenomenons are hard to destinguish,
this document uses the word noise as a shorthand covering both
this internal DUT performance fluctuations and genuine SUT noise.

A simple model of SUT performance consists of an idealized noiseless performance,
and additional noise effects. The noiseless performance is assumed to be constant,
all observed performance variations are due to noise.
The impact of the noise can vary in time, sometimes wildly,
even within a single trial.
The noise can sometimes be negligible, but frequently
it lowers the observed SUT performance as observed in trial results.

In this model, SUT does not have a single performance value, it has a spectrum.
One end of the spectrum is the idealized noiseless performance value,
the other end can be called a noiseful performance. In practice, trial results
close to the noiseful end of the spectrum happen only rarely.
The worse the performance value is, the more rarely it is seen in a trial.
Therefore, the extreme noiseful end of SUT spectrum is not really observable
among trial results. Also, the extreme noiseless end of SUT spectrum
is unlikely to be observable, this time because some small noise effects
are likely to occur multiple times during a trial.

Unless specified otherwise, this document talks about potentially observable
ends of the SUT performance spectrum, not about the extreme ones.

Focusing on DUT, the benchmarking effort should aim
at eliminating only the SUT noise from SUT measurements.
In practice that is not really possible, as based on authors experience
and available literature, there are no realistic enough models
able to distinguish SUT noise from DUT fluctuations.

However, assuming that a well-constructed SUT has the DUT as its
performance bottleneck, the DUT ideal noiseless performance can be defined
as the noiseless end of SUT performance spectrum. At least for
throughput. For other performance quantities such as latency there may be an
additive difference.

Note that by this definition, DUT noiseless performance
also minimizes the impact of DUT fluctuations, as much as realistically possible
for a given trial duration.

In this document, we reduce the DUT in SUT problem to estimating
the noiseless end of SUT performance spectrum from a limited number of
trial results.

Any improvements to throughput search algorithm, aimed for better
dealing with software networking SUT and DUT setup, should employ
strategies recognizing the presence of SUT noise, and allow discovery of
(proxies for) DUT noiseless performance
at different levels of sensitivity to SUT noise.

## Repeatability and Comparability

[RFC2544] does not suggest to repeat throughput search. And from just one
discovered throughput value, it cannot be determined how repeatable that value is.
In practice, poor repeatability is also the main cause of poor
comparability, that is different benchmarking teams can test the same SUT
but get throughput values differing more than expected from search precision.

[RFC2544] throughput requirements (60 seconds trial and
no tolerance of a single frame loss) affect the throughput results
in the following way.
The SUT behavior close to the noiseful end of its performance spectrum
consists of rare occasions of significantly low performance,
but the long trial duration makes those occasions not so rare on the trial level.
Therefore, the binary search results tend to wander away from the noiseless end
of SUT performance spectrum, more frequently and more widely than shorter
trials would, thus resulting in poor throughput repeatability.

The repeatability problem can be addressed by defining a search procedure
which reports more stable results,
even if they can no longer be called throughput in [RFC2544] sense.
According to the SUT performance spectrum model, better repeatability
will be at the noiseless end of the spectrum.
Therefore, solutions to the DUT in SUT problem
will help also with the repeatability problem.

Conversely, any alteration to [RFC2544] throughput search
that improves repeatability should be considered
as less dependent on the SUT noise.

An alternative option is to simply run a search multiple times, and report some
statistics (e.g. average and standard deviation). This can be used
for a subset of tests deemed more important,
but it makes the search duration problem even more pronounced.

## Throughput with Non-Zero Loss

[RFC1242] (section 3.17) defines throughput as:
    The maximum rate at which none of the offered frames
    are dropped by the device.

Then, it says:
    Since even the loss of one frame in a
    data stream can cause significant delays while
    waiting for the higher level protocols to time out,
    it is useful to know the actual maximum data
    rate that the device can support.

Contrary to that, many benchmarking teams settle with small, non-zero
loss ratio as the goal for a their load search.

Motivations are many:

- Modern protocols tolerate frame loss better,
  compared to the time when [RFC1242] and [RFC2544] were specified.

- Trials nowadays send way more frames within the same duration,
  increasing the chance small SUT performance fluctuatios
  is enough to cause frame loss.

- Small bursts of frame loss caused by noise have otherwise smaller impact
  on the average frame loss ratio ovserved in the trial,
  as during other parts of the same trial the SUT may work mroe closely
  to its noiseless performance, thus perhaps lowering the trial loss ratio
  below the goal loss ratio value.

- If an approximation of the SUT noise impact on the trial loss ratio is known,
  it can be set as the goal loss ratio.

Regardless of validity of any and all similar motivations,
support for non-zero loss goals makes any search algorithm more user friendly.
[RFC2544] throughput is not user friendly in this regard.

Assuming users are allowed to specify the goal loss ratio value,
the usefulness is enhanced even more if users can specify multiple
loss ratio values, especially when a single search can find all relevant bounds.

Searching for multiple search goals also helps to describe the SUT performance
spectrum better than a single search goal result.
For example, repeated wide gap between zero and non-zero loss loads
indicates the noise has a large impact on the observed performance,
which is not evident from a single goal load search procedure result.

It is easy to modify the vanilla bisection to find a lower bound
for intended load that satisfies a non-zero goal loss ratio.
But it is not that obvious how to search for multiple goals at once,
hence the support for multiple search goals remains a problem.

## Inconsistent Trial Results

While performing throughput search by executing a sequence of
measurement trials, there is a risk of encountering inconsistencies
between trial results.

The plain bisection never encounters inconsistent trials.
But [RFC2544] hints about possibility of inconsistent trial results,
in two places in its text.
The first place is section 24, where full trial durations are required,
presumably because they can be inconsistent with results
from shorter trial durations.
The second place is section 26.3, where two successive zero-loss trials
are recommended, presumably because after one zero-loss trial
there can be subsequent inconsistent non-zero-loss trial.

Examples include:

- A trial at the same load (same or different trial duration) results
  in a different packet loss ratio.
- A trial at higher load (same or different trial duration) results
  in a smaller packet loss ratio.

Any robust throughput search algorithm needs to decide how to continue
the search in presence of such inconsistencies.
Definitions of throughput in [RFC1242] and [RFC2544] are not specific enough
to imply a unique way of handling such inconsistencies.

Ideally, there will be a definition of a new quantity which both generalizes
throughput for non-zero-loss (and other possible repeatibility enhancements),
while being precise enough to force a specific way to resolve trial result
inconsistencies.
But until such definition is agreed upon, the correct way to handle
inconsistent trial results remains an open problem.

# MLRsearch Explanations

This chapter focuses on intuitions and motivations
and skips over some important details.
This allows the subsequent chapters to focus more on required details
without digressing that far into explanations.

## MLRsearch libraries

The MLRsearch algorithm has been developed in a code-first approach,
a Python library has been created, debugged and used in production
before first descriptions (even informal) were published.
In fact, multiple versions of the library were used in production
over past few years, and later code was usually not compatible
with earlier descriptions.

The code in (any version of) MLRsearch library fully determines
the search process (for given configuration parameters),
leaving no space for deviations.
MLRsearch as a name for a broad class of possible algorithms
leaves plenty of space for future improvements, at the cost
of poor comparability of results of different MLRsearch implementations.

This document aspires to prescribe a MLRsearch specification
in a way that restricts the important parts related to comparability,
while leaving other parts vague enough so implementations can improve freely.

## Exit condition

[RFC2544] prescribes that after performing one trial at a specific offered load,
the next offered load should be larger or smaller, based on frame loss.

The usual implementation uses binary search. Here a lossy trial becomes
a new upper bound, a lossless trial becomes a new lower bound.
The span of values between the tightest lower bound and the tightest upper bound
forms an interval of possible results,
and after each trial the width of that interval halves.

Usually the binary search implementation tracks only the two tightest bounds,
simply calling them bounds, but the old values still remain valid bounds,
just not as tight as the new ones.

After some number of trials, the tightest lower bound becomes the throughput.
[RFC2544] does not specify when (if ever) should the search stop.

MLRsearch library introduces a concept of goal width. The search stops
when the distance between the tightest upper bound and the tightest lower bound
is smaller than a user-configured value called goal width from now on.
In other words, interval width has to be smaller than goal width
at the end of the search.

This goal width value therefore determines the precision of the result.
As MLRsearch specification requires a particular structure of the result,
the result itself does contain enough information to determine its precision,
thus it is not required to report the goal width value.

This allows MLRsearch implementations to use exit conditions
different from goal width.
The MLRsearch specification only REQUIRES the search procedure
to always finish in a finite time, regardless of possible trial results.

## Load Classification

MLRsearch keeps the basic logic of binary search (tracking tightest bounds,
measuring at the middle), perhaps with minor technical clarifications.
The algorithm chooses an intended load (as opposed to offered load),
the interval between bounds does not need to be split exactly in two equal halves,
and the final reported structure specifies both bounds
(optionally also the conditional throughput at the lower bound, defined later).

The biggest difference is that in order to classify a load
as an upper or lower bound, MLRsearch may need more than one trial
(depending on configuration options) to be performed at the same intended load.

As a consequence, even if a load already does have few trial results,
it still may be classified as undecided, neither a lower bound nor an upper bound.

For repeatability and comparability reasons, it is important that
given a set of trial results, all implementations of MLRsearch
classify the load in an equivalent way.

## Loss ratios

Next difference is in goals of the search. [RFC2544] has a single goal,
based on classifying full-length trials as either loss-less or lossy.

As the name suggests, MLRsearch can seach for multiple goals, differing in their
loss ratios. Precise definition of goal loss ratio will be given later.
The [RFC2544] throughput goal then simply becomes a zero goal loss ratio.
Different goals also may have different goal width.

A set of trial results for one specific intended load value
can classify the load as an upper bound for some goals, but a lower bound
for some other goals, and undecided for the rest of the goals.

Therefore, the load classification depends not only on ttrial results,
but also on the goal. The overall search procedure becomes more complicated
(compared to binary search with a single goal),
but most of the complications do not affect the final result,
except for one phenomenon, loss inversion.

## Loss inversion

In [RFC2544] throuhput search using bisection, any load with lossy trial
becomes a hard upper bound, meaning every subsequent trial has smaller
intended load.

But in MLRsearch, a load that is classified as an upper bound for one goal
may still be a lower bound for another goal, and due to that other goal
MLRsearch will probably perform trials at even higher loads.
What to do when all such higher load trials happen to have zero loss?
Does it mean the earlier upper bound was not real?
Does it mean the later lossless trials are not considered a lower bound?
Surely we do not want to have an upper bound at a load smaller than a lower bound.

MLRsearch is conservative in these situations.
The upper bound is considered real, and the lossless trials at higher loads
are considered to be a coincidence, at least when computing the final result.

This is formalized using new notions, "relevant upper bound" and
"relevant lower bound".
Load classification is still based just on the set of trial results
at a given intended load (trials at other loads are ignored),
making it possible to have a lower load classified as an upper bound
and a higher load classified as a lower bound (for the same goal).
The relevant upper bound (for a goal) is the smallest load classified
as an upper bound. But the relevant lower bound is not simply
the largest among lower bounds. It is the largest load among loads
that are lower bounds while also being smaller than the relevant upper bound.

With these definitions, the relevant lower bound is always smaller
than the relevant upper bound (if both exist), and the two relevant bounds
are used analogously as the two tightest bounds in the binary search.
When they are less than goal width apart, the relevant bounds are used in output.

One consequence is that every trial result can have an impact on the search result.
That means if your SUT (or your traffic generator) needs a warmup,
be sure to warm it up before starting the search.

## Exceed ratio

The idea of performing multiple trials at the same load comes from
a model where some trial results (those with high loss) are affected
by infrequent effects, causing poor repeatability of [RFC2544] throughput results.
See the discussion about noiseful and noiseless ends of SUT performance spectrum.
Stable results are closer to the noiseless end of SUT preformance spectrum,
so MLRsearch may need to allow some frequency of high-loss trials
to ignore the reare but big effects near the noisefull end.

MLRsearch is able to do such trial result filtering, but it needs
a configuration option to tell it how much frequent can the infrequent big loss be.
This option is called exceed ratio. It tells MLRsearch what ratio of trials
(more exactly what ratio of trial seconds) can have trial loss ratio
larger than goal loss ratio and still be classified as a lower bound.
Zero exceed ratio means all trials have to have trial loss ratio
equal to or smaller than the goal loss ratio.

For explainability reasons, the RECOMMENDED value for exceed ratio is 0.5,
as it simplifies some later concepts by relating them to the concept of median.

## Duration sum

When more than one trial is needed to classify a load,
MLRsearch also needs something that controlls the number of trials needed.
Therefore, each goal also has an attribute called duration sum.

The meaning of a goal duration sum is that when a load has trials
(at full trial duration, details later)
whose trial durations when summed up give a value at least this,
the load is guaranteed to be classified as an upper bound or a lower bound
for the goal.

As the duration sum has a big impact on the overall search duration,
and [RFC2544] prescibes wait intervals around trial traffic,
the MLRsearch algorithm may sum durations that are different
from the actual trial traffic durations.

## Short trials

Section 24 of [RFC2544] already anticipates possible time savings
when short trials (shorter than full length trials) are used.

MLRsearch requires each goal to specify its final trial duration.
Full-length trial is the short name for a trial whose intended trial duration
is equal to the goal final trial duration.

Any MLRsearch implementation may include its own configuration options
which control when and how MLRsearch chooses to use shorter trial durations.

For explainability reasons, when exceed ratio of 0.5 is used,
it is recommended for the goal duration sum to be an odd multiple
of the full trial durations, so conditional throughput becomes identical to
a median of a particular set of forwarding rates.

Presence of shorter trial results complicates the load classification logic.
Full details are given later. In short, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the relevant lower bound
(below what would classification say when considering full-length trials only).

For explainability reasons, it is RECOMMENDED users use such configurations
that guarantee all trials have the same length.
Alas, such configurations are usually not compliant with [RFC2544] requirements,
or not time-saving enough.

## Conditional throughput

As testing equipment takes intended load as input parameter
for a trial measurement, any load search algorithm needs to deal
with intended load values internally.

But in presence of goals with non-zero loss ratio, the intended load
usually does not match the user intuition of what a throughput is.
The forwarding rate (as defined in [RFC2285] section 3.6.1) is better,
but it is not obvious how to generalize it
for loads with multiple trial results,
especially with non-zero goal exceed ratio.

MLRsearch defines one such generalization, called the conditional throughput.
It is the forwarding rate from one of the trials performed at the load
in question. Specification of which trial exactly is quite technical,
see the Definitions chapter and Appendix B.

Conditional throughput is partially related to load classification.
If a load is classified as a lower bound for a goal,
the conditional throughpt can be calculated,
and guaranteed to show effective loss ratio no larger than goal loss ratio.

While the conditional throughput gives more intuitive-looking values
than the relevant lower bound, especially for non-zero goal loss ratio values,
the actual definition is more complicated than the definition of the relevant
lower bound. In future, other intuitive values may become popular,
but they are unlikely to supersede the definition of the relevant lower bound
as the most fitting value for comparability purposes,
therefore the relevant lower bound remains a required attribute
of the goal result structure.

Note that comparing best and worst case, the same relevant lower bound value
may result in the conditional throughput differing up to the goal loss ratio.
Therefore it is rarely needed to set the goal width (if expressed
as relative difference of loads) below the goal loss ratio.
In other words, setting the goal width below the goal loss ratio
may cause the conditional throughput for a larger loss ratio to became smaller
than a conditional throughput for a goal with a smaller goal loss ratio,
which is counter-intuitive, considering they come from the same search.
Therefore it is RECOMMENDED to set the goal width to a value no smaller
than the goal loss ratio.

## Search time

The main motivation for MLRsearch was to have an algorithm that spends less time
finding a throughput, either the [RFC2544] compliant one,
or some generalization thereof. The art of achieving short search times
is mainly in smart selection of intended loads (and intended durations)
for the next trial to perform.

While there is an indirect impact of the load selection on the reported values,
in practice such impact tends to be small,
even for SUTs with quite broad performance spectrum.

A typical example of two approaches to load selection leading to different
relevant lower bounds is when the interval is split in a very uneven way.
An implementation chosing loads very close to the current relevant lower bound
are quite likely to eventually stumble upon a trial result
with poor performance (due to SUT noise).
For an implementation chosing load very close to the current relevant upper bound
this is unlikely, as it examines more loads that can see a performance
close to the noiseless end of the SUT performance spectrum.
The reason why it is unlikely to have two MLRsearch implementation showing
this kind of preference in load selection is precisely
in the desire to have short searches.
Even splits are the best way to achive the desired precision,
so the more optimized a search algorithm is for the overall search duration,
the better the repeatability and comparability
of its results will be, assuming the user configuration remains the same.

Therefore, this document remains quite vague on load selection
and other optimisation details, and configuration attributes related to them.
Assuming users prefer libreries that achieve short overall search time,
the definition of the relevant lower bound
should be strict enough to ensure result repeatability
and comparability between different implementations,
while not restricting future implementations much.

Sadly, different implementations may exhibit their sweet spot of
best repeatability at given search duration at different goals attribute values,
especially with respect to optional goal attributes
such as initial trial duration.
Thus, this document does not comment much on which configurations
are good for comparability between different implementations.
For comparability between different SUTs using the same implementation,
refer to configurations recommended by that particular implementation.

## [RFC2544] compliance

The following search goal ensures unconditional compliance with
[RFC2544] throughput search procedure:

- Goal loss ratio: zero.

- Goal final trial duration: 60 seconds.

- Goal duration sum: 60 seconds.

- Goal exceed ratio: zero.

Presence of other search goals does not affect compliance of this goal result.
The relevant lower bound and the conditional throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

If the 60 second quantity is replaced by a smaller quantity in both attributes,
the conditional throughput is still conditionally compliant with
[RFC2544] throughput.

# Selected Functional Details

This chapter continues with explanations,
but this time more precise definitions are needed
for readers to follow the explanations.
The definitions here are wordy, implementers can look into the next chapter
for more concise definitions.

The two areas of focus in this chapter are the load classification
and the conditional throughput, starting with the latter.

## Performance spectrum

There are several equivalent ways to define the conditional throughput computation.
One of the ways relies on an object called the performance spectrum.
First, two heavy definitions are needed.

Take an intended load value, and a finite set of trial results, all trials
measured at that load value. The performance spectrum is the function that maps
any non-negative real number into a sum of trial durations among all trials
in the set that have that number as their forwarding rate,
e.g. map to zero if no trial has that particular forwarding rate.

A related function, defined if there is at least one trial in the set,
is the performance spectrum divided by sum of durations of all trials in the set.
That function is called the performance probability function, as it satisfies
all the requirements for probability mass function function
of a discrete probability distribution,
the one-dimensional random variable being the trial forwarding rate.

These functions are related to the SUT performance spectrum,
as sampled by the trials in the set.

As for any other probability function, we can talk about percentiles,
of the performance probability function, and bout other quantiles
such as the median. The conditional throughput will be
one such quantile value for a specifically chosen set of trials.

Take a set of all full-length trials performed at the load in question.
The sum of durations of those trials may be less than goal duration sum, or not.
If it is less, add an imaginary trial result with zero forwarding rate
such that the new sum of durations is equal to the goal duration sum.
This is the set of trials to use. The q-value for the quantile
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

The classification does not need the whole performance spectrum,
only few duration sums.

A trial is called bad (according to a goal) if its trial loss ratio
is larger than the goal loss ratio. Trial that is not bad is called good.

## Single trial duration

When goal attributes are chosen in such a way that every trial has the same
intended duration, the load classification is sipler.

The following description looks technical, but it follows the motivation
of goal loss ratio, goal exceed ratio and goal duration sum.
If sum of durations of all trials (at given load) is less than the goal
duration sum, imagine best case scenario (all subsequent trials having zero loss)
and worst case scenario (all subsequent trials having 100% loss).
Here we assume there is as many subsequent trials as needed
to make the sum of all trials to become equal to the goal duration sum.
As the exceed ratio is defined just using sums of durations
(number of trials does not matter), it does not matter whether
the "subsequent trials" can consist of integer number of full-length trials.

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

## Short trial scenarios

Trials with intended duration smaller than the goal final trial duration
are called short trials.
The motivation for load classification logic in presence of short trials
is based around a counter-factual case: What would the trial result be
if a short trial has been measured as a full-length trial instead?

There are three main scenarios where human intuition guides
the intended behavior of load classification.

Scenario one. The user had their reason for not configuring shorter goal
final trial duration. Perhaps SUT has buffers that may get full at longer
trial durations. Perhaps SUT shows periodic decreases of performance
the user does not want to treat as noise. In any case, many good short trials
may became bad full-length trial in the counter-factual case.
In extreme case, there are no bad short trials.
In this scenario, we want the load classification NOT to classify the load
as a lower bound, despite the abundance of good short trials.
Effectively, we want the good short trials to be ignored, so they
do not contribute to comparisons with the goal duration sum.

Scenario two. When there is a frame loss in a short trial,
the counter-factual full-length trial is expected to lose at least as many
frames. And in practice, bad short trials are rarely turning into
good full-length trials. In extreme case, there are no good short trials.
In this scenario, we want the load classification
to classify the load as an upper bound just based on abundance
of short bad trials. Effectively we want the bad short trials
to contribute to comparisons with the goal duration sum,
so the load can be classified sooner.

Scenario three. Some SUTs are quite indifferent to trial duration.
Performance probability function constructed from short trial results
is likely to be similar to performance probability function constructed
from full-length trial results (perhaps with smaller dispersion,
but overall without big impact on the median quantiles).
For moderate goal exceed ratio values, this may mean there are both
good short trials and bad short trials.
This scenario is there just to invalidate a simple heuristic
of always ignoring good short trials and never ignoring bad short trials.
That simple heuristic would be too biased. Yes, the short bad trials
are likely to turn into full-length bad trials in the counter-factual case,
but there is no information on what would the good short trials turn into.
The only way to decide is to do more trials at full length,
the same as in scenario one.

## Short trial logic

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
If the excess sum is negative, the bad sum is equal to the bad long sum.
Else, the bad sum is equal to the bad long sum plus the excess sum.

Here is how the new definition of the bad sum fares in the three scenarios,
where the load is close to what would relevant bounds be
if only full-length trials were used for the search.

Scenario one. If duration is too short, we expect to see higher frequency
of good short trials. This could lead to negative excess sum,
which has no impact, hence the load classification is given just by
full-length trials.
Thus, MLRsearch using too short trials has no detrimental effect
on result comparability in this scenario.
But also using short trials does not help with overall search duration,
proably making it worse.

Scenario two. Settings with small exceed ratio have small exceed coefficient,
so the impact of good short sum is small and the bad short sum
is almost wholly converted into excess sum, thus bad short trials
have almost as big impact as full-length bad trials.
The same conclusion applies for moderate exceed ratio values
when the good short sum is small.
Thus, short trials can cause a load to get classified as an upper bound earlier
bringing time savings (while not affecting comparability).

Scenario three. Here excess sum is small in absolute value, as balancing sum
is expected to be be similar to the bad short sum.
Once again, full-length trials are needed for final load classification,
but usage of short trials probably means MLRsearch needed shorter search time
before selecting this load for measurement, bringing time savings
(while not affecting comparability).

## Longer trial durations

If there are trial results with intended duration larger
than the goal trial duration, the classification logic is intentionally undefined.

The implementations MAY treat such longer trials as if they were full-length.
In any case, presence of such longer trials in either the relevant lower bound
or the relevant upper bound SHOULD be mentioned, as for sume SUTs
it is likely to affect comparability.

# MLRsearch specification

This chapter focuses on technical definitions needed for evaluating
whether a particular test procedure adheres to MLRsearch specification.
For motivations, explanations, and other comments see the previous chapters.

Some definitions are direct copies from other documents.
Other are intended only for internal use in this ducument,
whether the terms are new, or just generalizations of terms defined elsewhere.

## MLRsearch Architecture

MLRsearch architecture consists of three main components:
the manager, the controller and the measurer.
Presence of other components (mainly the SUT) is also implied.

While the manager and the measurer can be seen a abstractions
present in any testing procedure, the behavior of the controller
is what distinguishes MLRsearch algorithms from other search procedures.

(The definitions of the three components refer to terms defined on other sections
of this chapter.)

### Manager

The manager is the component that initializes SUT, traffic generator
(called tester in [RFC2544]), the measurer and the controller
with intended configurations. It then hands over the execution
to the controller and receives its result.

Creation of reports of appropriate format can also be understood
as the responsibility of the manager.

### Measurer

The measurer is the component which performs one trial
as described in [RFC2544] section 23, when requested by the controller.

Specifically, one call to the measurer turns trial load and trial duration,
into trial loss ratio.

It is responsibility of the measurer to uphold any requirements
and assumptions present in MLRsearch specification
(e.g. trial forwarding rate not being larger than one).
Implementers have some freedom, for example in the way they deal with
duplicated frames, or what to return if tester sent zero frames towards SUT.
Implementations are RECOMMENDED to document their behavior
related to such freedoms in as detailed way as possible

Implemenations MUST document any deviations from RFC documents,
for example if the wait time around traffic
is shorter than what [RFC2544] section 23 specifies.

### Controller

The controller is the component of MLRsearch architecture
that is called by the manager (just once), calls the measurer
(usually multiple times in succession),
and returns the Search Result to the manager.

The only required argument in the call to the controller
is a list of search goals.

## Units

The specification deals with physical quantities, so it is assumed
each numeric value is accompanied by an appropriate physical unit.

The specification does not state which unit is appropriate,
but implementations MUST make it explicit which unit is used
for each value provided or received by the user.

For example, load quantities (including the conditional throughput)
returned by the controller are defined to be based on single-interface
(unidirectional) loads. For bidirectional traffic, users are likely
to expect bidirectional throughput quantities, so the manager is responsible
for making its report clear.

## SUT

As defined in [RFC2285]:
The collective set of network devices to which stimulus is offered
as a single entity and response measured.

## Trial

A trial is the part of test described in [RFC2544] section 23.

### Load

Trial load is the intended constant load for a trial.

Load is the quantity implied by Constant Load of [RFC1242],
Data Rate of [RFC2544] and Intended Load of [RFC2285].
All three specify this value applies to one (input or output) interface.

### Duration

Trial duration is the intended duration of the traffic for a trial.

This general quantity does not include any preparation nor waiting
described in section 23 of [RFC2544].

For purposes of computing duration sums in the controller,
the measurer MAY return a duration value different from the intended duration.
The manager MUST report how those durations sums are computed in that case.

### Forwarding Ratio

Trial forwarding ratio is dimensionless floating point value,
assumed to be between 0.0 and 1.0, both including.
It is computed as the number of frames forwarded by SUT, divided by
the number of frames that should have been forwarded during the trial.

Note that, contrary to load, frame counts used to compute
trial forwarding ratio are aggregates over all SUT ports.

Questions around what is the correct number of frames
that should have been forwarded it outside of the scope of this document.
E.g. what should the measurer return when it detects
that the offered load differs significantly from the intended load.

It is RECOMMENDED implementations return an irregular goal result
if they detect questionable (in comparability sense) trial results
affecting their goal result.

### Loss Ratio

Trial loss ratio is equal to one minus the trial forwarding ratio.

### Forwarding Rate

The trial forwarding rate is the trial load multiplied by
the trial forwarding ratio.

Note that this is very similar, but not identical to Forwarding Rate
as defined in [RFC2285] section 3.6.1, as that definition
is specific to one output interface, while trial forwarding ratio
is based on frame counts aggregated over all SUT interfaces.

## Traffic profile

Any other specifics (besides trial load and trial duration)
the measurer needs to perform the trial are understood as a composite
called the traffic profile.
All its attributes are assumed to be constant during the search,
and the composite is configured on the measurer by the manager
before the search starts.

Traffic profile is REQUIRED by [RFC2544] to contain some specific quantities
(for example frame size).
Several more specific quantities may be RECOMMENDED.

Depending on SUT configuration (e.g. when testing specific protocols),
additional values need to be included in the traffic profile
and in the test report. (See other IETF documents.)

## Search goal

Search goal is a composite consisting of several attributes,
some of them are required.
Implementations are free to add their own attributes.

Subsections list all required attributes and one recommended attribute.

### Goal loss ratio

A threshold value for trial loss ratios.
REQUIRED attribute, MUST be non-negative and smaller than one.

### Goal final trial duration

A threshold value for trial durations.
REQUIRED attribute, MUST be positive.

### Goal duration sum

A threshold value for a particular sum of trial durations.
REQUIRED attribute, MUST be positive.

### Goal exceed ratio

A threshold value for particular ratio of duration sums.
REQUIRED attribute, MUST be non-negative and smaller than one.

### Goal width

A value used as a threshold for telling when two trial load values
are close enough.

RECOMMENDED attribute, positive. Implementations without this attribute
MUST give the manager other ways to control the search exit condition.

Absolute load difference and relative load difference are two popular choices,
but implementations may choose a different way to specify width.

## Search result

Search result is a single composite object returned from the controller
to the manager.
It is a mapping from the search goals (the same list as the controller got
as its required arument) into goal results (defined in the next subsection).

Each search goal instance is mapped to a goal result instance.
Multiple search goal instances may map to the same goal result instance.

## Goal result

Goal result is a composite object consisting of several attributes,
all related to one search goal (the one the search result
is mapping to this instance).

Some of the attributes are required, some are recommended,
implementations are free to add their own.

The subsections define attributes for regular goal result.
Implementations are free to define their own irregular goal results,
but the manager MUST report them clearly as not regular according to this section.

A typical irregular result is when all trial at maximum offered load
have zero loss, as the relevant upper bound does not exist in that case.

### Relevant lower bound

Relevant lower bound is the intended load value that got classified
(after all trials) as the relevant lower bound (see Appendix A) for this goal.
This is a REQUIRED attribute.

### Relevant upper bound

Relevant upper bound is the intended load value that got classified
(after all trials) as the relevant upper bound (see Appendix A) for this goal.
This is a REQUIRED attribute.

The distance between the relevant lower bound and the relevant upper bound
MUST NOT be larger than the goal width, for regular goal result,
if the implementation offers width as a goal attribute.

### Conditional throughput

The conditional throughput (see Appendix B) as evaluated
at the relevant lower bound.
This is a RECOMMENDED attribute.

# Problems after MLRsearch

Now when MLRsearch is clearly specified and explained,
it is possible to summarize how does MLRsearch specification help with problems.

Here, "multiple trials" is a shorthand for having the goal final trial duration
significantly smaller than the goal duration sum.
This results in MLRsearch performing multiple trials at the same load,
which may not be the case with other configurations.

## Long Test Duration

As shortening the overall search duration is the main motivation
of MLRsearch library development, the library implements
multiple improvements on this front, both big and small.
Most of implementation details are not part of the MLRsearch specification,
so that future implementations may keep shortening the search duration even more.

From the required goal attributes, the goal duration sum
remains the best way to get even shorter searches.

Usage of multiple trials can also save time,
depending on wait times around trial traffic.

The farther the goal exceed ratio is from 0.5, the less predictable
the overal search duration becomes in practice.

Width parameter does not change search duration much in practice
(compared to other, mainly optional goal attributes).

## DUT in SUT

Practice shows big improvements when multiple trials
and moderate exceed ratios are used. Mainly when it comes to result
repeatability, as sometimes it is not easy to distinguish
SUT noise from DUT instability.

Conditional throughput has intuitive meaning when described
using the performance spectrum, so this is an improvement,
especially when compared to search procedures which use non-zero
goal loss ratio but return only the intended load at a lower bound.

Multiple trials can save time also when the noisy end of
the preformance spectrum needs to be examined, e.g. for [RFC9004].

Under some circumstances, testing the same DUT and SUT setup with different
DUT configurations can give some hints on what part of noise us SUT noise
and what part is DUT performance fluctuations.
In practice, both types of noise tend to be too complicated for that analysis.
MLRsearch does not offer additional tools in this regard,
apart of giving users ability to search for more goals,
hoping to get more insight at the cost of longer overall search time.

## Repeatability and Comparability

Multiple trials improve repeatability, depending on exceed ratio.

In practice, 1s goal final trial duration with exceed ratio 0.5
is good enough for modern SUTs (but that usually requires
smaller wait times around the traffic part of the trial,
otherwise too much search time is wasted waiting).

It is not clear whether exceed ratios higher than 0.5 are better
for repeatability.
The 0.5 value is still preferred due to explainability using median.

It is possible that the conditional throughput values (with non-zero
goal loss ratio) are better for repeatability than the relevant
lower bound values, especially for implementations
which pick load from a small set of discrete values.

Implementations focusing on shortening the overall search time
are automatically forced to avoid comparability issues
due to load selection, as they must prefer even splits wherever possible.
But this conclusion only holds when the same goals are used.
Larger adoption is needed before any further claims on comparability
between MLRsearch implementations can be made.

## Throughput with Non-Zero Loss

Suported by the goal loss ratio attribute.
Improves repeatability as expected.

## Inconsistent Trial Results

MLRsearch is conservative wherever possible,
this is built into the definition of conditional throughput,
and into the treatment of short trial results for load classification.

This is consistent with [RFC2544] zero loss tolerance motivation.

If the very best (noiseless) part of the SUT performance spectrum
is of interest, it should be enough to set small value for
the goal final trial duration, and perhaps also a large value
for the goal exceed ratio.

Implementations may offer other (optional) configuration attributes
(and optional goal result attributes)
to become less conservative, but currently it is not clear
what impact would that have on repeatability.

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

Special wholehearted gratitude and thanks to late Al Morton for his
thorough reviews filled with very specific feedback and constructive
guidelines. Thank you Al for the close collaboration over the years,
for your continuous unwavering encouragements full of empathy and
positive attitude.
Al, you are dearly missed.

# Appendix A

This is a specification of load classification.

The block at the end of this appendix holds pseudocode
which computes two values, stored in variables named optimistic and pessimistic.
The pseudocode happens to be a valid Python code.

If both values are computed to be true, the load in question
is classified as a lower bound according to the goal in question.
If both values are false, the load is classified as an upper bound.
Otherwise, the load is classifies as undecided.

The pseudocole expects the following variables hold values as follows:

- goal_duration_sum: The goal duration sum value.

- goal_exceed_ratio: The goal exceed ratio value.

- good_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with trial loss ratio
  not higher than the goal loss ratio.

- bad_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with trial loss ratio
  higher than the goal loss ratio.

- good_short_sum: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with trial loss ratio
  not higher than the goal loss ratio.

- bad_short_sum: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with trial loss ratio
  higher than the goal loss ratio.

Here the implicit set of available trial results consists of all trials
measured at given intended load at the end of search.

The code works correctly also when there are no trial results at given load.

```
balancing_sum = good_short_sum * goal_exceed_ratio / (1.0 - goal_exceed_ratio)
effective_bad_sum = bad_long_sum + max(0.0, bad_short_sum - balancing_sum)
effective_whole_sum = max(good_long_sum + effective_bad_sum, goal_duration_sum)
quantile_duration_sum = effective_whole_sum * goal_exceed_ratio
optimistic = effective_bad_sum <= quantile_duration_sum
pessimistic = (effective_whole_sum - good_long_sum) <= quantile_duration_sum
```

# Appendix B

This is a specification of conditional throughput.

The block at the end of this appendix holds pseudocode
which computes a value stored as variable conditional_throughput.
The pseudocode happens to be a valid Python code.

The pseudocole expects the following variables hold values as follows:

- goal_duration_sum: The goal duration sum value.

- goal_exceed_ratio: The goal exceed ratio value.

- good_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with trial loss ratio
  not higher than the goal loss ratio.

- bad_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with trial loss ratio
  higher than the goal loss ratio.

- long_trials: An iterable of all trial results from trials with trial duration
  at least equal to the goal final trial duration,
  sorted by increasing trial loss ratio.
  A trial result is a composite with the following two attributes available:

  - trial.loss_ratio: The trial loss ratio as measured for this trial.

  - trial.duration: The trial duration of this trial.

Here the implicit set of available trial results consists of all trials
measured at given intended load at the end of search.

The code works correctly only when there if there is at leas one
trial result measured at given load.

```
all_long_sum = max(goal_duration_sum, good_long_sum + bad_long_sum)
remaining = all_long_sum * (1.0 - goal_exceed_ratio)
quantile_loss_ratio = None
for trial in long_trials:
    if quantile_loss_ratio is None or remaining > 0.0:
        quantile_loss_ratio = trial.loss_ratio
        remaining -= trial.duration
    else:
        break
else:
    if remaining > 0.0:
        quantile_loss_ratio = 1.0

conditional_throughput = intended_load * (1.0 - quantile_loss_ratio)
```

--- back

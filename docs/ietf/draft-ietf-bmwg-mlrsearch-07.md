---

title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-07
date: 2024-07-08

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
    target: https://pypi.org/project/MLRsearch/1.2.1/
    title: "MLRsearch 1.2.1, Python Package Index"
    date: 2023-10

--- abstract

This document proposes extensions to [RFC2544] throughput search by
defining a new methodology called Multiple Loss Ratio search
(MLRsearch). MLRsearch aims to minimize search duration,
support multiple loss ratio searches,
and enhance result repeatability and comparability.

The primary reason for extending [RFC2544] is to address the challenges
and requirements presented by the evaluation and testing
of software-based networking systems' data planes.

To give users more freedom, MLRsearch provides additional configuration options
such as allowing multiple shorter trials per load instead of one large trial,
tolerating a certain percentage of trial results with higher loss,
and supporting the search for multiple goals with varying loss ratios.

--- middle

{::comment}
    As we use Kramdown to convert from Markdown,
    we use this way of marking comments not to be visible in the rendered draft.
    https://stackoverflow.com/a/42323390
    If another engine is used, convert to this way:
    https://stackoverflow.com/a/20885980
{:/comment}

TODO: Each RFC reference should mentions specific subsection.

# Purpose and Scope

The purpose of this document is to describe Multiple Loss Ratio search
(MLRsearch), a data plane throughput search methodology optimized for software
networking DUTs.

Applying vanilla [RFC2544] throughput bisection to software DUTs
results in several problems:

- Binary search takes too long as most trials are done far from the
  eventually found throughput.
- The required final trial duration and pauses between trials
  prolong the overall search duration.
- Software DUTs show noisy trial results,
  leading to a big spread of possible discovered throughput values.
- Throughput requires a loss of exactly zero frames, but the industry
  frequently allows for small but non-zero losses.
- The definition of throughput is not clear when trial results are inconsistent.


To address the problems mentioned above,
the MLRsearch library employs the following enhancements:

- Allow multiple shorter trials instead of one big trial per load.
  - Optionally, tolerate a percentage of trial results with higher loss.
- Allow searching for multiple search goals, with differing loss ratios.
  - Any trial result can affect each search goal in principle.
- Insert multiple coarse targets for each search goal, earlier ones need
  to spend less time on trials.
  - Earlier targets also aim for lesser precision.
  - Use Forwarding Rate (FR) at maximum offered load
    [RFC2285] (section 3.6.2) to initialize the initial targets.
- Take care when dealing with inconsistent trial results.
  - Reported throughput is smaller than the smallest load with high loss.
  - Smaller load candidates are measured first.
- Apply several load selection heuristics to save even more time
  by trying hard to avoid unnecessarily narrow bounds.

Some of these enhancements are formalized as MLRsearch specification,
the remaining enhancements are treated as implementation details,
thus achieving high comparability without limiting future improvements.

MLRsearch configuration options are flexible enough to
support both conservative settings and aggressive settings.
Where the conservative settings lead to results
unconditionally compliant with [RFC2544],
but longer search duration and worse repeatability.
Conversely, aggressive settings lead to shorter search duration
and better repeatability, but the results are not compliant with [RFC2544].

No part of [RFC2544] is intended to be obsoleted by this document.

# Identified Problems

This chapter describes the problems affecting usability
of various performance testing methodologies,
mainly a binary search for [RFC2544] unconditionally compliant throughput.

## Long Search Duration

The emergence of software DUTs, with frequent software updates and a
number of different frame processing modes and configurations,
has increased both the number of performance tests
required to verify the DUT update and the frequency of running those tests.
This makes the overall test execution time even more important than before.

The current [RFC2544] throughput definition restricts the potential
for time-efficiency improvements.
A more generalized throughput concept could enable further enhancements
while maintaining the precision of simpler methods.

The bisection method, when unconditionally compliant with [RFC2544],
is excessively slow.
This is because a significant amount of time is spent on trials
with loads that, in retrospect, are far from the final determined throughput.

[RFC2544] does not specify any stopping condition for throughput search,
so users already have an access to a limited trade-off
between search duration and achieved precision.
However, each full 60-second trials doubles the precision,
so not many trials can be removed without a substantial loss of precision.

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

In the case of software networking, the SUT consists of not only the DUT
as a software program processing frames, but also of
a server hardware and operating system functions,
with server hardware resources shared across all programs
and the operating system running on the same server.

Given that the SUT is a shared multi-tenant environment
encompassing the DUT and other components, the DUT might inadvertently
experience interference from the operating system
or other software operating on the same server.

Some of this interference can be mitigated.
For instance,
pinning DUT program threads to specific CPU cores
and isolating those cores can prevent context switching.

Despite taking all feasible precautions, some adverse effects may still impact
the DUT's network performance.
In this document, these effects are collectively
referred to as SUT noise, even if the effects are not as unpredictable
as what other engineering disciplines call noise.

DUT can also exhibit fluctuating performance itself, for reasons
not related to the rest of SUT; for example due to pauses in execution
as needed for internal stateful processing.
In many cases this
may be an expected per-design behavior, as it would be observable even
in a hypothetical scenario where all sources of SUT noise are eliminated.
Such behavior affects trial results in a way similar to SUT noise.
As the two phenomenons are hard to distinguish,
in this document the term 'noise' is used to encompass
both the internal performance fluctuations of the DUT
and the genuine noise of the SUT.

A simple model of SUT performance consists of an idealized noiseless performance,
and additional noise effects.
For a specific SUT, the noiseless performance is assumed to be constant,
with all observed performance variations being attributed to noise.
The impact of the noise can vary in time, sometimes wildly,
even within a single trial.
The noise can sometimes be negligible, but frequently
it lowers the observed SUT performance as observed in trial results.

In this model, SUT does not have a single performance value, it has a spectrum.
One end of the spectrum is the idealized noiseless performance value,
the other end can be called a noiseful performance.
In practice, trial result
close to the noiseful end of the spectrum happens only rarely.
The worse the performance value is, the more rarely it is seen in a trial.
Therefore, the extreme noiseful end of the SUT spectrum is not observable
among trial results.
Also, the extreme noiseless end of the SUT spectrum
is unlikely to be observable, this time because some small noise effects
are likely to occur multiple times during a trial.

Unless specified otherwise, this document's focus is
on the potentially observable ends of the SUT performance spectrum,
as opposed to the extreme ones.

When focusing on the DUT, the benchmarking effort should ideally aim
to eliminate only the SUT noise from SUT measurements.
However,
this is currently not feasible in practice, as there are no realistic enough
models available to distinguish SUT noise from DUT fluctuations,
based on the author's experience and available literature.

Assuming a well-constructed SUT, the DUT is likely its
primary performance bottleneck.
In this case, we can define the DUT's
ideal noiseless performance as the noiseless end of the SUT performance spectrum,
especially for throughput.
However, other performance metrics, such as latency,
may require additional considerations.

Note that by this definition, DUT noiseless performance
also minimizes the impact of DUT fluctuations, as much as realistically possible
for a given trial duration.

This document aims to solve the DUT in SUT problem
by estimating the noiseless end of the SUT performance spectrum
using a limited number of trial results.

Any improvements to the throughput search algorithm, aimed at better
dealing with software networking SUT and DUT setup, should employ
strategies recognizing the presence of SUT noise, allowing the discovery of
(proxies for) DUT noiseless performance
at different levels of sensitivity to SUT noise.

## Repeatability and Comparability

[RFC2544] does not suggest to repeat throughput search.
And from just one
discovered throughput value, it cannot be determined how repeatable that value is.
Poor repeatability then leads to poor comparability,
as different benchmarking teams may obtain varying throughput values
for the same SUT, exceeding the expected differences from search precision.

[RFC2544] throughput requirements (60 seconds trial and
no tolerance of a single frame loss) affect the throughput results
in the following way.
The SUT behavior close to the noiseful end of its performance spectrum
consists of rare occasions of significantly low performance,
but the long trial duration makes those occasions not so rare on the trial level.
Therefore, the binary search results tend to wander away from the noiseless end
of SUT performance spectrum, more frequently and more widely than shorter
trials would, thus causing poor throughput repeatability.

The repeatability problem can be addressed by defining a search procedure
that identifies a consistent level of performance,
even if it does not meet the strict definition of throughput in [RFC2544].

According to the SUT performance spectrum model, better repeatability
will be at the noiseless end of the spectrum.
Therefore, solutions to the DUT in SUT problem
will help also with the repeatability problem.

Conversely, any alteration to [RFC2544] throughput search
that improves repeatability should be considered
as less dependent on the SUT noise.

An alternative option is to simply run a search multiple times, and report some
statistics (e.g. average and standard deviation).
This can be used
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

However, many benchmarking teams accept a small,
non-zero loss ratio as the goal for their load search.

Motivations are many:

- Modern protocols tolerate frame loss better,
  compared to the time when [RFC1242] and [RFC2544] were specified.

- Trials nowadays send way more frames within the same duration,
  increasing the chance of a small SUT performance fluctuation
  being enough to cause frame loss.

- Small bursts of frame loss caused by noise have otherwise smaller impact
  on the average frame loss ratio observed in the trial,
  as during other parts of the same trial the SUT may work more closely
  to its noiseless performance, thus perhaps lowering the trial loss ratio
  below the goal loss ratio value.

- If an approximation of the SUT noise impact on the trial loss ratio is known,
  it can be set as the goal loss ratio.

Regardless of the validity of all similar motivations,
support for non-zero loss goals makes any search algorithm more user-friendly.
[RFC2544] throughput is not user-friendly in this regard.

Furthermore, allowing users to specify multiple loss ratio values,
and enabling a single search to find all relevant bounds,
significantly enhances the usefulness of the search algorithm.

Searching for multiple search goals also helps to describe the SUT performance
spectrum better than the result of a single search goal.
For example, the repeated wide gap between zero and non-zero loss loads
indicates the noise has a large impact on the observed performance,
which is not evident from a single goal load search procedure result.

It is easy to modify the vanilla bisection to find a lower bound
for the intended load that satisfies a non-zero goal loss ratio.
But it is not that obvious how to search for multiple goals at once,
hence the support for multiple search goals remains a problem.

## Inconsistent Trial Results

While performing throughput search by executing a sequence of
measurement trials, there is a risk of encountering inconsistencies
between trial results.

The plain bisection never encounters inconsistent trials.
But [RFC2544] hints about the possibility of inconsistent trial results,
in two places in its text.
The first place is section 24, where full trial durations are required,
presumably because they can be inconsistent with the results
from shorter trial durations.
The second place is section 26.3, where two successive zero-loss trials
are recommended, presumably because after one zero-loss trial
there can be a subsequent inconsistent non-zero-loss trial.

Examples include:

- A trial at the same load (same or different trial duration) results
  in a different trial loss ratio.
- A trial at a higher load (same or different trial duration) results
  in a smaller trial loss ratio.

Any robust throughput search algorithm needs to decide how to continue
the search in the presence of such inconsistencies.
Definitions of throughput in [RFC1242] and [RFC2544] are not specific enough
to imply a unique way of handling such inconsistencies.

Ideally, there will be a definition of a new quantity which both generalizes
throughput for non-zero-loss (and other possible repeatability enhancements),
while being precise enough to force a specific way to resolve trial result
inconsistencies.
But until such a definition is agreed upon, the correct way to handle
inconsistent trial results remains an open problem.

# MLRsearch Specification

This chapter focuses on technical definitions needed for evaluating
whether a particular test procedure complies with MLRsearch specification.

For additional motivations, explanations, and other comments see other chapters.

TODO: Sort bottom-up by definition dependencies.

## Overview

TODO: Improve style.

While definitions are ordered by their direct dependencies,
in discussion paragraphs it is useful to refer to terms defined later.
This section gives a quick introduction to some of such terms.

MLRsearch specification describes co-called MLRsearch architecture.
There are components, acting as functions with specified inputs and outputs.

A test procedure is said to comply with MLRsearch specification
if it can be conceptually divided into analogous components,
each satisfying requirements for the corresponding MLRsearch component.

The measurer component is tasked to perform trials,
the controller component is tasked to select trial loads and durations,
the manager component is tasked to pre-configure everything
and to produce the test report.
The test report explicitly states search goals (as the controller inputs)
and corresponding goal results (controller outputs).

The manager calls the controller once,
the controller keeps calling the measurer
until all exit conditions are met.

The part where controller calls the measurer is called the search.
Any activity done by the manager before it calls the controller
(or after the controller returns) is not considered to be part of the search.

TODO: Currently some Discussion paragraphs contain SHOULDs and MUSTs.

## General Considerations

The specification defines various quantities.
In general, the specification does require specific units to be used
but it is required for the test report to state all the units.
For example, ratio quantities can be dimensionless numbers between zero and one,
but may be expressed as percentages instead.

For convenience, groups of quantities can be treated as a composite quantity,
One constituent of a composite quantity is called an attribute,
and a group of attribute values is called an instance of that composite quantity.

Some attributes are not independent from others,
and they can even be calculated from other attributes.
Such quantites are called derived quantities.

## Existing Terms

These terms are already defined in earlier documents,
and apply in this document without any changes.

Only two existing terms are mentioned in definitions.
Discussion paragraphs may mention other existing terms.
TODO: List those other existing terms.

TODO: Mention DUT and tester here, not in subsections?

### SUT

As defined in [RFC2285] section 3.1.2.

Definition:

The collective set of network devices to which stimulus is offered
as a single entity and response measured.

Discussion:

SUT consisting of a single network device is also allowed.

DUT, as a sub-component of SUT, is not a direct part
of the MLRsearch specification, but is of relevance for its motivation.

### Trial

Definition:

A trial is the part of the test described in [RFC2544] section 23.

It is ALLOWED for the test procedure to deviate from [RFC2544],
but any such deviation MUST be made explicit in the test report.

Discussion:

We say a trial is performed or measured.

Trials are the only stimuli the SUT is expected to experience
during the search.

Measuring trials is the responsibility of the measurer component.
One call, one trial.

An example of deviation from [RFC2544] is using shorter wait times.

TODO: Define traffic generator / traffic analyzer / tester.

See Also:

- Measurer

## Trial Terms

Subsections of this section define new terms for quantities
relevant as inputs or outputs of trial as measured by the measurer component.

### Trial Duration

Definition:

Trial duration is the intended duration of the traffic for a trial.

Discussion:

In general, this quantity does not include any preparation nor waiting
described in section 23 of [RFC2544].

See Also:

- Measurer

### Trial Load

Definition:

The trial load is the intended and constant load for a trial.

Discussion:

Load is the quantity implied by Constant Load of [RFC1242],
Data Rate of [RFC2544] and Intended Load of [RFC2285].
All three specify this value applies to one (input or output) interface.

For report purposes, multi-interface aggregate load MAY be reported,
this is understood as the same quantity expressed using different units.
From the report it must be clear whether a particular trial load quantity
is per one interface, or an aggregate over all interfaces.

It is ALLOWED to combine trial load and trial duration in a way
that would not be possible to achieve using any integer number of data frames.
TODO: Refer to this from trial forwarding/loss rate subsection.

### Trial Input

Definition:

Trial input is a composite quantity, consisting of two attributes:
trial duration and trial load.

Discussion:

When talking about multiple trials, it is common to say "trial inputs"
to denote all corresponding trial input instances.

A trial input instance acts as the input for one call of the measurer component.

### Traffic profile

Definition:

Traffic profile is a composite quantity
containing any specifics other than trial load and trial duration,
needed by the measurer in order to perform the trial.

Discussion:

All its attributes are assumed to be constant during the search,
and the composite is configured on the measurer by the manager
before the search starts.
This is why traffic profile is not part of the trial input.

The traffic profile is REQUIRED by [RFC2544]
to contain some specific quantities, for example data link frame size
as defined in [RFC1224] section 3.5.

Several more specific quantities may be RECOMMENDED, depending on media type.
For example, [RFC2544] (Appendix C) lists frame formats and protocol addresses,
as recommended from section 8 and 12.

Depending on SUT configuration, e.g. when testing specific protocols,
additional values need to be included in the traffic profile
and in the test report.
See other IETF documents.

Example: [RFC8219] (section 5.3. Traffic Setup) introduces traffic setups
consisting of a mix of IPv4 and IPv6 traffic, the implied traffic profile
therefore MUST include an attribute for their percentage.

### Trial Forwarding Ratio

Definition:

The trial forwarding ratio is a dimensionless floating point value
that ranges from 0.0 to 1.0, both inclusive.
It is calculated by dividing the number of frames
successfully forwarded by the SUT
by the total number of frames expected to be forwarded during the trial.

Discussion:

Trial forwarding ratio MAY be expressed in other units
(e.g. as a percentage) in the test report.

Note that, contrary to loads, frame counts used to compute
trial forwarding ratio are aggregates over all SUT output interfaces.

Questions around what is the correct number of frames
that should have been forwarded is outside of the scope of this document.
E.g. what should the measurer return when it detects
that the offered load differs significantly from the intended load.

TODO: Coordinate with the measurer definition.

### Trial Loss Ratio

Definition:

The trial loss ratio is equal to one minus the trial forwarding ratio.

Discussion:

100% minus the trial forwarding ratio, when expressed as a percentage.

This is almost identical to Frame Loss Rate from [RFC1242] (section 3.6),
except that that is required to be a percentage.

### Trial Forwarding Rate

Definition:

The trial forwarding rate is a derived quantity, calculated by
multiplying the trial load by the trial forwarding ratio.

Discussion:

It is important to note that while similar, this quantity is not identical
to the Forwarding Rate as defined in [RFC2285] (section 3.6.1),
The latter is specific to one output interface only,
whereas the trial forwarding ratio is based
on frame counts aggregated over all SUT output interfaces.

### Trial Effective Duration

TODO: Better explain this is an optional feature.

TODO: Do not refer measurer nor controller from the definition.

Definition:

Any time quantity chosen by the measurer
to be used for time-based decisions in the controller.

Discussion:

By default, it is assumed the trial effective duration
is equal to the trial duration.

However, the measurer MAY optionally return a trial effective duration value
that differs from the intended duration.

This feature can be beneficial for users
who wish to manage the overall search duration,
rather than solely the traffic portion of it.
The manager MUST report how the measurer computes the returned
trial effective duration values if this feature is enabled.

### Trial Output

Definition:

Trial output is a composite quantity. The REQUIRED attributes are
trial loss ratio, trial effective duration and trial forwarding rate.

Discussion:

When talking about multiple trials, it is common to say "trial outputs"
to denote all corresponding trial output instances.

Implementations may provide additional (optional) attributes.

For example: the total number of frames expected to be forwarded during the trial,
especially if it is not just a rounded-up value
implied by trial load and trial duration.

While [RFC2285] (Section 3.5.2 Offered load (Oload))
requires the offered load value to be reported for forwarding rate measurements,
it is not required in the MLRsearch specification.

### Trial Result

Definition:

Trial result is a composite quantity,
consisting of the trial input and the trial output.

Discussion:

When talking about multiple trials, it is common to say "trial results"
to denote all corresponding trial result instances.
Sometimes just "trials".
TODO: Polish the wording.

## Goal Terms

Subsections of this section define new terms, for quantities
indirectly relevant for inputs or outputs of the controller component.

Subsections define several attributes before introducing
the main component quantity: the search goal.

Each subsection contains a short informal description,
but see other chapters for more in-depth explanations.

TODO: Clarify that when an attribute is REQUIRED, it is property of the composite.

### Goal Final Trial Duration

Definition:

A threshold value for trial durations.

Discussion:

This attribute is REQUIRED, and the value MUST be positive.

Trials with trial duration at least as long as the goal final trial duration
are called "full-length" trials with respect to the given search goal.

Informally, while MLRsearch is allowed to perform trials shorter than full-length,
the results from such short trials have only limited impact on search results.

One trial may be full-length for some search goals, but not for others.

The full relation needs definitions in later subsections.
But for example, the conditional throughput
for this goal will be computed only from full-length trial results.

### Goal Duration Sum

Definition:

A threshold value for a particular sum of trial effective durations.

Discussion:

This attribute is REQUIRED, and the value MUST be positive.

Informally, even when looking only at full-length trials,
MLRsearch may spend up to this time measuring the same load value.

If the goal duration sum is larger than the goal final trial duration,
multiple full-length trials may need to be performed at the same load.

### Goal Loss Ratio

Definition:

A threshold value for trial loss ratios.

Discussion:

REQUIRED attribute, MUST be non-negative and smaller than one.

Informally, if a load causes too many trials with trial loss ratios
larger than this, the relevant lower bound for this goal
will be smaller than that load.

A trial with trial loss ratio larger than a goal loss ratio value
is called a "lossy" trial with respect to given search goal.
TODO: Reword.

### Goal Exceed Ratio

Definition:

A threshold value for a particular ratio of sums of trial effective durations.

Discussion:

REQUIRED attribute, MUST be non-negative and smaller than one.

See section on controller outputs (TODO: number) for detail on which sums.

Informally, the impact of lossy trials is controlled by this value.
The full relation needs definitions is later subsections.

But for example, the definition of the conditional throughput
refers to a q-value (TODO: recheck Discussion there.)
for a quantile when selecting
which trial result gives the conditional throughput.
The goal exceed ratio acts as the q-value to use there.

Specifically, when the goal exceed ratio is 50% and MLRsearch happened
to use the whole goal duration sum (using full-length trials),
it means the conditional throughput is the median
of a particular set of trial forwarding rates.

### Goal Width

Definition:

A value used as a threshold for deciding
whether two trial load values are close enough
for search exit condition purposes.
(TODO: wording?)

Discussion:

RECOMMENDED attribute, positive.

Implementations without this attribute
MUST give the controller other ways to control the search exit condition.

Absolute load difference and relative load difference are two popular choices,
but implementations may choose a different way to specify width.

Informally, this acts as an exit condition,
controlling the precision of the search.
The search stops if every goal has reached its precision.

### Search Goal

Definition:

The search goal is a composite quantity consisting of several attributes,
some of them are required.

Required attributes: (TODO: capitalization)
- Goal Final Trial Duration
- Goal Duration Sum
- Goal Loss Ratio
- Goal Exceed Ratio

Optional attribute:
- Goal Width

Discussion:

Implementations are free to add their own additional attributes.

The meaning of the attributes is formally given only by their effect
on the controller output attributes
(defined in later in section Search Result).

Informally, later chapters give additional intuitions and examples
to the search goal attribute values.
Later chapters also give motivation to formulas of computation of the outputs.

An example of additional attributes required by some implementations
is a goal initial trial duration, together with another attribute
which controls possible intermediate trial duration values.

### Controller Input

Definition:

Controller input is a composite quantity
required as an input for the controller.
The only required attribute is a list of search goal instances.

Discussion:

MLRsearch implementations MAY use additional attributes,
e.g. when tweaking time-related decisions.

Formally, the manager does not apply any controller configuration
outside the one controller input instance.
Any other assumed pieces of configuration (e.g. traffic profile)
is passed (as if) outside the visibility of the controller.

The order of search goal instances SHOULD NOT
have a big impact on controller outputs,
but MLRsearch implementations MAY base their behavior on the order
of search goal instances.

The search goal instances SHOULD NOT be identical.
MLRsearch implementation MAY allow identical instances.

An example of an optional attribute (outside the list of search goals)
required by some implementations is max load.
While this is a frequently used configuration parameter,
already governed by [RFC2544] (section 20. Maximum frame rate)
and [RFC2285] (3.5.3 Maximum offered load (MOL)),
some implementations may detect or discover it instead.
In MLRsearch specification, the upper relevant bound was added
as a required attribute precisely because it makes the search result
independent of max load value.
TODO: Move some of this into upper relevant bound Discussion?

## Result Terms

Before defining the output of the controller,
it is useful to define what the goal result is.

And as the goal result is a composite quantity, it is better to
define all its attribute quantites first.

There is a correspondence between search goals and goal results.
All following subsection refer to a given search goal
when defining attributes of the goal results.
Conversely, at the end of the search, each sarch goal
has its corresponding goal result.

Conceptually, the search can be seen as the process of load classification,
where the controller attempts to classify some loads as an upper bound
or a lower bound with respect to some search goal.

TODO: Move REQUIRED from attributes into composite.

### Relevant Upper Bound

Definition:

The relevant upper bound is the smallest trial load value that is classified
at the end of the search as an upper bound (see Appendix A)
for the given search goal.

Discussion:

This is a REQUIRED attribute.

Informally, this is the smallest intended load that failed to uphold
all the requirements of the given search goal, mainly the goal loss ratio
in combination with the goal exceed ratio.

If max load does not cause enough lossy trials,
the relevant upper bound does not exist.

### Relevant Lower Bound

Definition:

The relevant lower bound is the largest trial load value
among those smaller than the relevant upper bound,
that got classified at the end of the search
as a lower bound (see Appendix A) for the given search goal.

Discussion:

This is a REQUIRED attribute.

For a regular goal result, the distance between the relevant lower bound
and the relevant upper bound MUST NOT be larger than the goal width,
if the implementation offers width as a goal attribute.

Informally, this is the largest intended load that managed to uphold
all the requirements of the given search goal, mainly the goal loss ratio
in combination with the goal exceed ratio, while not being larger
than the relevant upper bound.

### Conditional Throughput

Definition:

The conditional throughput (see Appendix B)
as evaluated at the relevant lower bound of the given search goal
at the end of the search.
This is a RECOMMENDED attribute.

Discussion:

Informally, this is a typical trial forwarding rate expected to be seen
at the relevant lower bound of the given search goal.

But frequently it is only a conservative estimate thereof,
as MLRsearch implementations tend to stop gathering more data
as soon as they confirm the value cannot get worse than this estimate
within the goal duration sum.

This value is RECOMMENDED to be used when evaluating repeatability
and comparability if different MLRsearch implementations.

### TODO: Trial results at relevant bounds?

### Goal Result

Definition:

The goal result is a composite quantity consisting of several attributes.
Relevant upper bound and relevant lower bound are required attributes,
conditional throughput is a recommended attribute.
(TODO: trial results optional)

Discussion:

Any goal result instance can be either regular or irregular.
TODO: Separate definition for regular instances?

MLRsearch specification puts requirements on regular goal result instances.
Any instance that does not meet the requirements is deemed irregular.

Some of the attributes of a regular goal result instance are required,
some are recommended, implementations are free to add their own.
(TODO: trial results here if not before)

Implementations are free to define their own specific subtypes
of irregular goal results, but the test report MUST mark them clearly
as not regular according to this section.

A typical irregular result is when all trials at the max load
have zero loss, as the relevant upper bound does not exist in that case.

### Search Result

Definition:

The search result is a single composite object
that maps each search goal instance to a corresponding goal result instance.

Discussion:

Alternatively, the search result can be implemented as an ordered list
of the goal result instances, matching the order of search gaol instances.

The search result (as a mapping)
MUST map from all the search goal instances present in the controller input.
The search goal instances MAY be irregular.
TODO: Irregular search result if at least one irregular goal result?

TODO: Discuss API / interoperability
between manager and several controller implementations.

### Controller Output

Definition:

The controller output is a composite quantity returned from the controller
to the manager at the end of the search.
The search result instance is its only REQUIRED attribute.

Discussion:

MLRsearch implementation MAY return additional data in the controller output.

TODO: Mention telemetry (and other non-opaque-box stuff).

## Architecture Terms

TODO: Harmonize with the overview in general.

MLRsearch architecture consists of three main components:
the manager, the controller, and the measurer.

The architecture also implies the presence of other components,
such as the SUT and the tester.
(TODO: See the other TODO on tester / TG / TA.)

These components can be seen as abstractions present in any testing procedure.
For example, there can be a single component acting both
as the manager and the controller, but as long as required attributes
of search goals and goal results are visible in the test report,
controller input and output is implied.

Protocols of communication between components are generally left unspecified.
For example when this specification mentions "controller calls measurer",
it is possible that the controller notifies the manager
to call the measurer indirectly instead. This way the measurer implementations
can be fully independent from the controller implementations,
e.g. programmed in different programming languages.

### Measurer

Definition:

The measurer is an abstract component
that when called with a trial input instance,
performs one trial as described in [RFC2544] section 23,
and returns a trial output instance.

Discussion:

This definition assumes the measurer is already initialized.
In practice, there may be additional steps before the search,
e.g. when the manager configures the traffic profile
(either on the measurer or on its tester sub-component directly)
and performs a warmup (if the tester requires one).

It is the responsibility of the measurer to uphold any requirements
and assumptions present in MLRsearch specification,
e.g. trial forwarding ratio not being larger than one.

Implementers have some freedom.
For example [RFC2544] (section 10. Verifying received frames)
gives some suggestions (but not requirements) related to
duplicated or reordered frames.
Implementations are RECOMMENDED to document their behavior
related to such freedoms in as detailed a way as possible.

It is RECOMMENDED to benchmark the test equipment first,
e.g. connect sender and receiver directly (without ant DUT in path),
find a load value that guarantees the offered load is not too far
from the intended load, and use that value as max load parameter.
When testing the real SUT, it is RECOMMENDED to turn any big difference
between the intended load and the offered load into non-zero loss ratio.
Neither of the two recommendations are made into requirements,
because it is not easy to tell when the difference is big enough,
in a way thay would be dis-entangled from other measurer freedoms.

### Controller

Definition:

The controller is an abstract component
that when called with a controller input instance
repeatedly computes trial input instance for the measurer,
obtains corresponding trial output instances,
and eventually returns a controller output instance.

Discussion:

Goal width or other attributes act directly as requirements
for search result precision, and indirectly as the search exit conditions.

Informally, the controller has big freedom is selection of trial inputs,
and the implementations want to achieve the search goals
in the shortest expected time.

The controller's role in optimizing the overall search time
distinguishes MLRsearch algorithms from simpler search procedures.

### Manager

Definition:

The manager is an abstract component
that is reponsible for configuring other components,
calling the controller component once,
and for creating the test report (TODO: RFC2544 term here) in appropriate format.

Discussion:

The controller initializes SUT, the traffic generator
(TODO: tester in [RFC2544] terminology) and the measurer
with their intended configurations before calling the controller.

The manager does not need to be able to tweak any search goal attribute.

In principle, there sould be a "user" (human or CI)
that "starts" or "calls" the manager and receives the report.
The manager MAY be able to be called more than once whis way.
TODO: Reword.

Also, the manager may use the measurer or other components
to perform other tests, e.g. back-to-back frames,
as the controller is only replacing [RFC2544] (section 26.1) Throughput.

### MLRsearch architecture

Definition:

Any setup where there can be logically delineated components
and there are components satisfying requirements for the measurer,
the controller and the manager.

Discussion:

For example, any setup for conditionally compliant [RFC2544] throughput testing
can be understood as a MLRsearch architecture (maybe with hardcoded goals),
assuming there is enough data to reconstruct the relevant upper bound.

Any test procedure that can be understood as (one call to the manager of)
MLRsearch architecture is said to be compliant with MLRsearch specification.

TODO: Why do we need both architecture and specification?

TODO: Does the test procedure need to be able to produce a regular search result?

TODO: Modularity, e.g. freedom to swap measurer hardware and controller software
as long as the manager understands communication protocols of both?

# Further Explanations

This chapter focuses on intuitions and motivations
and skips over some important details.

Familiarity with the MLRsearch specification is not required here,
so this chapter can act as an introduction.
For example, this chapter starts talking about the tightest lower bounds
before it is ready to talk about the relevant lower bound from the specification.

## MLRsearch Versions

The MLRsearch algorithm has been developed in a code-first approach,
a Python library has been created, debugged, and used in production
before the first descriptions (even informal) were published.
In fact, multiple versions of the library were used in the production
over the past few years, and later code was usually not compatible
with earlier descriptions.

The code in (any version of) MLRsearch library fully determines
the search process (for given configuration parameters),
leaving no space for deviations.
MLRsearch, as a name for a broad class of possible algorithms,
leaves plenty of space for future improvements, at the cost
of poor comparability of results of different MLRsearch implementations.

There are two competing needs.
There is the need for standardization in areas critical to comparability.
There is also the need to allow flexibility for implementations
to innovate and improve in other areas.
This document defines the MLRsearch specification
in a manner that aims to fairly balances both needs.

## Exit Condition

[RFC2544] prescribes that after performing one trial at a specific offered load,
the next offered load should be larger or smaller, based on frame loss.

The usual implementation uses binary search.
Here a lossy trial becomes
a new upper bound, a lossless trial becomes a new lower bound.
The span of values between (including both) the tightest lower bound
and the tightest upper bound forms an interval of possible results,
and after each trial the width of that interval halves.

Usually the binary search implementation tracks only the two tightest bounds,
simply calling them bounds.
But the old values still B remain valid bounds,
just not as tight as the new ones.

After some number of trials, the tightest lower bound becomes the throughput.
[RFC2544] does not specify when (if ever) should the search stop.

MLRsearch library introduces a concept of goal width.
The search stops
when the distance between the tightest upper bound and the tightest lower bound
is smaller than a user-configured value, called goal width from now on.
In other words, the interval width at the end of the search
has to be no larger than the goal width.

This goal width value therefore determines the precision of the result.
As MLRsearch specification requires a particular structure of the result,
the result itself does contain enough information to determine its precision,
thus it is not required to report the goal width value.

This allows MLRsearch implementations to use exit conditions
different from goal width.

## Load Classification

MLRsearch keeps the basic logic of binary search (tracking tightest bounds,
measuring at the middle), perhaps with minor technical clarifications.
The algorithm chooses an intended load (as opposed to the offered load),
the interval between bounds does not need to be split
exactly into two equal halves,
and the final reported structure specifies both bounds.

The biggest difference is that to classify a load
as an upper or lower bound, MLRsearch may need more than one trial
(depending on configuration options) to be performed at the same intended load.

As a consequence, even if a load already does have few trial results,
it still may be classified as undecided, neither a lower bound nor an upper bound.

An explanation of the classification logic is given in the next chapter,
as it relies heavily on other sections of this chapter.

For repeatability and comparability reasons, it is important that
given a set of trial results, all implementations of MLRsearch
classify the load equivalently.

## Loss Ratios

The next difference is in the goals of the search.
[RFC2544] has a single goal,
based on classifying full-length trials as either lossless or lossy.

As the name suggests, MLRsearch can search for multiple goals,
differing in their loss ratios.
The precise definition of the goal loss ratio will be given later.
The [RFC2544] throughput goal then simply becomes a zero goal loss ratio.
Different goals also may have different goal widths.

A set of trial results for one specific intended load value
can classify the load as an upper bound for some goals, but a lower bound
for some other goals, and undecided for the rest of the goals.

Therefore, the load classification depends not only on trial results,
but also on the goal.
The overall search procedure becomes more complicated
(compared to binary search with a single goal),
but most of the complications do not affect the final result,
except for one phenomenon, loss inversion.

## Loss Inversion

In [RFC2544] throughput search using bisection, any load with a lossy trial
becomes a hard upper bound, meaning every subsequent trial has a smaller
intended load.

But in MLRsearch, a load that is classified as an upper bound for one goal
may still be a lower bound for another goal, and due to the other goal
MLRsearch will probably perform trials at even higher loads.
What to do when all such higher load trials happen to have zero loss?
Does it mean the earlier upper bound was not real?
Does it mean the later lossless trials are not considered a lower bound?
Surely we do not want to have an upper bound at a load smaller than a lower bound.

MLRsearch is conservative in these situations.
The upper bound is considered real, and the lossless trials at higher loads
are considered to be a coincidence, at least when computing the final result.

This is formalized using new notions, the relevant upper bound and
the relevant lower bound.
Load classification is still based just on the set of trial results
at a given intended load (trials at other loads are ignored),
making it possible to have a lower load classified as an upper bound,
and a higher load classified as a lower bound (for the same goal).
The relevant upper bound (for a goal) is the smallest load classified
as an upper bound.
But the relevant lower bound is not simply
the largest among lower bounds.
It is the largest load among loads
that are lower bounds while also being smaller than the relevant upper bound.

With these definitions, the relevant lower bound is always smaller
than the relevant upper bound (if both exist), and the two relevant bounds
are used analogously as the two tightest bounds in the binary search.
When they are less than the goal width apart,
the relevant bounds are used in the output.

One consequence is that every trial result can have an impact on the search result.
That means if your SUT (or your traffic generator) needs a warmup,
be sure to warm it up before starting the search.

## Exceed Ratio

The idea of performing multiple trials at the same load comes from
a model where some trial results (those with high loss) are affected
by infrequent effects, causing poor repeatability of [RFC2544] throughput results.
See the discussion about noiseful and noiseless ends
of the SUT performance spectrum.
Stable results are closer to the noiseless end of the SUT performance spectrum,
so MLRsearch may need to allow some frequency of high-loss trials
to ignore the rare but big effects near the noiseful end.

MLRsearch can do such trial result filtering, but it needs
a configuration option to tell it how frequent can the infrequent big loss be.
This option is called the exceed ratio.
It tells MLRsearch what ratio of trials
(more exactly what ratio of trial seconds) can have a trial loss ratio
larger than the goal loss ratio and still be classified as a lower bound.
Zero exceed ratio means all trials have to have a trial loss ratio
equal to or smaller than the goal loss ratio.

For explainability reasons, the RECOMMENDED value for exceed ratio is 0.5,
as it simplifies some later concepts by relating them to the concept of median.

## Duration Sum

When more than one trial is needed to classify a load,
MLRsearch also needs something that controls the number of trials needed.
Therefore, each goal also has an attribute called duration sum.

The meaning of a goal duration sum is that when a load has trials
(at full trial duration, details later)
whose trial durations when summed up give a value at least this long,
the load is guaranteed to be classified as an upper bound or a lower bound
for the goal.

As the duration sum has a big impact on the overall search duration,
and [RFC2544] prescribes wait intervals around trial traffic,
the MLRsearch algorithm is allowed to sum durations that are different
from the actual trial traffic durations.

## Short Trials

MLRsearch requires each goal to specify its final trial duration.
Full-length trial is a shorter name for a trial whose intended trial duration
is equal to (or longer than) the goal final trial duration.

Section 24 of [RFC2544] already anticipates possible time savings
when short trials (shorter than full-length trials) are used.
Full-length trials are the opposite of short trials,
so they may also be called long trials.

Any MLRsearch implementation may include its own configuration options
which control when and how MLRsearch chooses to use shorter trial durations.

For explainability reasons, when exceed ratio of 0.5 is used,
it is recommended for the goal duration sum to be an odd multiple
of the full trial durations, so conditional throughput becomes identical to
a median of a particular set of trial forwarding rates.

The presence of shorter trial results complicates the load classification logic.
Full details are given later.
In short, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the relevant lower bound
(below what would classification say when considering full-length trials only).

For explainability reasons, it is RECOMMENDED users use such configurations
that guarantee all trials have the same length.
Alas, such configurations are usually not compliant with [RFC2544] requirements,
or not time-saving enough.

## Conditional Throughput

As testing equipment takes the intended load as an input parameter
for a trial measurement, any load search algorithm needs to deal
with intended load values internally.

But in the presence of goals with a non-zero loss ratio, the intended load
usually does not match the user's intuition of what a throughput is.
The forwarding rate (as defined in [RFC2285] section 3.6.1) is better,
but it is not obvious how to generalize it
for loads with multiple trial results and a non-zero goal loss ratio.

MLRsearch defines one such generalization, called the conditional throughput.
It is the trial forwarding rate from one of the trials
performed at the load in question.
Specification of which trial exactly is quite technical,
see the specification and Appendix B.

Conditional throughput is partially related to load classification.
If a load is classified as a lower bound for a goal,
the conditional throughput can be calculated,
and guaranteed to show an effective loss ratio
no larger than the goal loss ratio.

While the conditional throughput gives more intuitive-looking values
than the relevant lower bound, especially for non-zero goal loss ratio values,
the actual definition is more complicated than the definition of the relevant
lower bound.
In the future, other intuitive values may become popular,
but they are unlikely to supersede the definition of the relevant lower bound
as the most fitting value for comparability purposes,
therefore the relevant lower bound remains a required attribute
of the goal result structure, while the conditional throughput is only optional.

Note that comparing the best and worst case, the same relevant lower bound value
may result in the conditional throughput differing up to the goal loss ratio.
Therefore it is rarely needed to set the goal width (if expressed
as the relative difference of loads) below the goal loss ratio.
In other words, setting the goal width below the goal loss ratio
may cause the conditional throughput for a larger loss ratio to become smaller
than a conditional throughput for a goal with a smaller goal loss ratio,
which is counter-intuitive, considering they come from the same search.
Therefore it is RECOMMENDED to set the goal width to a value no smaller
than the goal loss ratio.

## Search Time

MLRsearch was primarily developed to reduce the time
required to determine a throughput, either the [RFC2544] compliant one,
or some generalization thereof.
The art of achieving short search times
is mainly in the smart selection of intended loads (and intended durations)
for the next trial to perform.

While there is an indirect impact of the load selection on the reported values,
in practice such impact tends to be small,
even for SUTs with quite a broad performance spectrum.

A typical example of two approaches to load selection leading to different
relevant lower bounds is when the interval is split in a very uneven way.
Any implementation choosing loads very close to the current relevant lower bound
is quite likely to eventually stumble upon a trial result
with poor performance (due to SUT noise).
For an implementation choosing loads very close
to the current relevant upper bound, this is unlikely,
as it examines more loads that can see a performance
close to the noiseless end of the SUT performance spectrum.

However, as even splits optimize search duration at give precision,
MLRsearch implementations that prioritize minimizing search time
are unlikely to suffer from any such bias.

Therefore, this document remains quite vague on load selection
and other optimization details, and configuration attributes related to them.
Assuming users prefer libraries that achieve short overall search time,
the definition of the relevant lower bound
should be strict enough to ensure result repeatability
and comparability between different implementations,
while not restricting future implementations much.

Sadly, different implementations may exhibit their sweet spot of
the best repeatability for a given search duration
at different goals attribute values, especially concerning
any optional goal attributes such as the initial trial duration.
Thus, this document does not comment much on which configurations
are good for comparability between different implementations.
For comparability between different SUTs using the same implementation,
refer to configurations recommended by that particular implementation.

## [RFC2544] Compliance

The following search goal ensures unconditional compliance with
[RFC2544] throughput search procedure:

- Goal loss ratio: zero.

- Goal final trial duration: 60 seconds.

- Goal duration sum: 60 seconds.

- Goal exceed ratio: zero.

The presence of other search goals does not affect the compliance
of this goal result.
The relevant lower bound and the conditional throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

If the 60 second quantity is replaced by a smaller quantity in both attributes,
the conditional throughput is still conditionally compliant with
[RFC2544] throughput.

# Logic of Load Classification

This chapter continues with explanations,
but this time more precise definitions are needed
for readers to follow the explanations.
The definitions here are wordy, implementers should read the specification
chapter and appendices for more concise definitions.

The two related areas of focus in this chapter are load classification
and the conditional throughput, starting with the latter.

The section Performance Spectrum contains definitions
needed to gain insight into what conditional throughput means.
The rest of the subsections discuss load classification,
they do not refer to Performance Spectrum, only to a few duration sums.

For load classification, it is useful to define good and bad trials.
A trial is called bad (according to a goal) if its trial loss ratio
is larger than the goal loss ratio.
The trial that is not bad is called good.

## Performance Spectrum

There are several equivalent ways to explain
the conditional throughput computation.
One of the ways relies on an object called the performance spectrum.
First, two heavy definitions are needed.

Take an intended load value, a trial duration value, and a finite set
of trial results, all trials measured at that load value and duration value.
The performance spectrum is the function that maps
any non-negative real number into a sum of trial durations among all trials
in the set that has that number as their trial forwarding rate,
e.g. map to zero if no trial has that particular forwarding rate.

A related function, defined if there is at least one trial in the set,
is the performance spectrum divided by the sum of the durations
of all trials in the set.
That function is called the performance probability function, as it satisfies
all the requirements for probability mass function function
of a discrete probability distribution,
the one-dimensional random variable being the trial forwarding rate.

These functions are related to the SUT performance spectrum,
as sampled by the trials in the set.

As for any other probability function, we can talk about percentiles
of the performance probability function, including the median.
The conditional throughput will be one such quantile value
for a specifically chosen set of trials.

Take a set of all full-length trials performed at the relevant lower bound,
sorted by decreasing trial forwarding rate.
The sum of the durations of those trials
may be less than the goal duration sum, or not.
If it is less, add an imaginary trial result with zero trial forwarding rate,
such that the new sum of durations is equal to the goal duration sum.
This is the set of trials to use.
The q-value for the quantile
is the goal exceed ratio.
If the quantile touches two trials,
the larger trial forwarding rate (from the trial result sorted earlier) is used.
The resulting quantity is the conditional throughput of the goal in question.

First example.
For zero exceed ratio, when goal duration sum has been reached.
The conditional throughput is the smallest trial forwarding rate among the trials.

Second example.
For zero exceed ratio, when goal duration sum has not been reached yet.
Due to the missing duration sum, the worst case may still happen,
so the conditional throughput is zero.
This is not reported to the user,
as this load cannot become the relevant lower bound yet.

Third example.
Exceed ratio 50%, goal duration sum two seconds,
one trial present with the duration of one second and zero loss.
The imaginary trial is added with the duration
of one second and zero trial forwarding rate.
The median would touch both trials, so the conditional throughput
is the trial forwarding rate of the one non-imaginary trial.
As that had zero loss, the value is equal to the offered load.

Note that Appendix B does not take into account short trial results.

### Summary

While the conditional throughput is a generalization of the trial forwarding rate,
its definition is not an obvious one.

Other than the trial forwarding rate, the other source of intuition
is the quantile in general, and the median the the recommended case.

In future, different quantities may prove more useful,
especially when applying to specific problems,
but currently the conditional throughput is the recommended compromise,
especially for repeatability and comparability reasons.

## Single Trial Duration

When goal attributes are chosen in such a way that every trial has the same
intended duration, the load classification is simpler.

The following description looks technical, but it follows the motivation
of goal loss ratio, goal exceed ratio, and goal duration sum.
If the sum of the durations of all trials (at the given load)
is less than the goal duration sum, imagine best case scenario
(all subsequent trials having zero loss) and worst case scenario
(all subsequent trials having 100% loss).
Here we assume there are as many subsequent trials as needed
to make the sum of all trials equal to the goal duration sum.
As the exceed ratio is defined just using sums of durations
(number of trials does not matter), it does not matter whether
the "subsequent trials" can consist of an integer number of full-length trials.

In any of the two scenarios, we can compute the load exceed ratio,
As the duration sum of good trials divided by the duration sum of all trials,
in both cases including the assumed trials.

If even in the best case scenario the load exceed ratio would be larger
than the goal exceed ratio, the load is an upper bound.
If even in the worst case scenario the load exceed ratio would not be larger
than the goal exceed ratio, the load is a lower bound.

Even more specifically.
Take all trials measured at a given load.
The sum of the durations of all bad full-length trials is called the bad sum.
The sum of the durations of all good full-length trials is called the good sum.
The result of adding the bad sum plus the good sum is called the measured sum.
The larger of the measured sum and the goal duration sum is called the whole sum.
The whole sum minus the measured sum is called the missing sum.
The optimistic exceed ratio is the bad sum divided by the whole sum.
The pessimistic exceed ratio is the bad sum plus the missing sum,
that divided by the whole sum.
If the optimistic exceed ratio is larger than the goal exceed ratio,
the load is classified as an upper bound.
If the pessimistic exceed ratio is not larger than the goal exceed ratio,
the load is classified as a lower bound.
Else, the load is classified as undecided.

The definition of pessimistic exceed ratio is compatible with the logic in
the conditional throughput computation, so in this single trial duration case,
a load is a lower bound if and only if the conditional throughput
effective loss ratio is not larger than the goal loss ratio.
If it is larger, the load is either an upper bound or undecided.

## Short Trial Scenarios

Trials with intended duration smaller than the goal final trial duration
are called short trials.
The motivation for load classification logic in the presence of short trials
is based around a counter-factual case: What would the trial result be
if a short trial has been measured as a full-length trial instead?

There are three main scenarios where human intuition guides
the intended behavior of load classification.

False good scenario.
The user had their reason for not configuring a shorter goal
final trial duration.
Perhaps SUT has buffers that may get full at longer
trial durations.
Perhaps SUT shows periodic decreases in performance
the user does not want to be treated as noise.
In any case, many good short trials may become bad full-length trials
in the counter-factual case.
In extreme cases, there are plenty of good short trials and no bad short trials.
In this scenario, we want the load classification NOT to classify the load
as a lower bound, despite the abundance of good short trials.
Effectively, we want the good short trials to be ignored, so they
do not contribute to comparisons with the goal duration sum.

True bad scenario.
When there is a frame loss in a short trial,
the counter-factual full-length trial is expected to lose at least as many
frames.
And in practice, bad short trials are rarely turning into
good full-length trials.
In extreme cases, there are no good short trials.
In this scenario, we want the load classification
to classify the load as an upper bound just based on the abundance
of short bad trials.
Effectively, we want the bad short trials
to contribute to comparisons with the goal duration sum,
so the load can be classified sooner.

Balanced scenario.
Some SUTs are quite indifferent to trial duration.
Performance probability function constructed from short trial results
is likely to be similar to the performance probability function constructed
from full-length trial results (perhaps with larger dispersion,
but without a big impact on the median quantiles overall).
For a moderate goal exceed ratio value, this may mean there are both
good short trials and bad short trials.
This scenario is there just to invalidate a simple heuristic
of always ignoring good short trials and never ignoring bad short trials.
That simple heuristic would be too biased.
Yes, the short bad trials
are likely to turn into full-length bad trials in the counter-factual case,
but there is no information on what would the good short trials turn into.
The only way to decide safely is to do more trials at full length,
the same as in scenario one.

## Short Trial Logic

MLRsearch picks a particular logic for load classification
in the presence of short trials, but it is still RECOMMENDED
to use configurations that imply no short trials,
so the possible inefficiencies in that logic
do not affect the result, and the result has better explainability.

With that said, the logic differs from the single trial duration case
only in different definition of the bad sum.
The good sum is still the sum across all good full-length trials.

Few more notions are needed for defining the new bad sum.
The sum of durations of all bad full-length trials is called the bad long sum.
The sum of durations of all bad short trials is called the bad short sum.
The sum of durations of all good short trials is called the good short sum.
One minus the goal exceed ratio is called the inceed ratio.
The goal exceed ratio divided by the inceed ratio is called the exceed coefficient.
The good short sum multiplied by the exceed coefficient is called the balancing sum.
The bad short sum minus the balancing sum is called the excess sum.
If the excess sum is negative, the bad sum is equal to the bad long sum.
Otherwise, the bad sum is equal to the bad long sum plus the excess sum.

Here is how the new definition of the bad sum fares in the three scenarios,
where the load is close to what would the relevant bounds be
if only full-length trials were used for the search.

False good scenario.
If the duration is too short, we expect to see a higher frequency
of good short trials.
This could lead to a negative excess sum,
which has no impact, hence the load classification is given just by
full-length trials.
Thus, MLRsearch using too short trials has no detrimental effect
on result comparability in this scenario.
But also using short trials does not help with overall search duration,
probably making it worse.

True bad cenario.
Settings with a small exceed ratio
have a small exceed coefficient, so the impact of the good short sum is small,
and the bad short sum is almost wholly converted into excess sum,
thus bad short trials have almost as big an impact as full-length bad trials.
The same conclusion applies to moderate exceed ratio values
when the good short sum is small.
Thus, short trials can cause a load to get classified as an upper bound earlier,
bringing time savings (while not affecting comparability).

Balanced scenario.
Here excess sum is small in absolute value, as the balancing sum
is expected to be similar to the bad short sum.
Once again, full-length trials are needed for final load classification;
but usage of short trials probably means MLRsearch needed
a shorter overall search time before selecting this load for measurement,
thus bringing time savings (while not affecting comparability).

Note that in presence of short trial results,
the comparibility between the load classification
and the conditional throughput is only partial.
The conditional throughput still comes from a good long trial,
but a load higher than the relevant lower bound may also compute to a good value.

## Longer Trial Durations

If there are trial results with an intended duration larger
than the goal trial duration, the precise definitions
in Appendix A and Appendix B treat them in exactly the same way
as trials with duration equal to the goal trial duration.

But in configurations with moderate (including 0.5) or small
goal exceed ratio and small goal loss ratio (especially zero),
bad trials with longer than goal durations may bias the search
towards the lower load values, as the noiseful end of the spectrum
gets a larger probability of causing the loss within the longer trials.

For some users, this is an acceptable price
for increased configuration flexibility
(perhaps saving time for the related goals),
so implementations SHOULD allow such configurations.
Still, users are encouraged to avoid such configurations
by making all goals use the same final trial duration,
so their results remain comparable across implementations.

# Addressed Problems

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

Most of implementation details are not constrained by the MLRsearch specification,
so that future implementations may keep shortening the search duration even more.

One exception is the impact of short trial results on the relevant lower bound.
While motivated by human intuition, the logic is not straightforward.
In practice, configurations with only one common trial duration value
are capable of achieving good overal search time and result repeatability
without the need to consider short trials.

### Impact of goal attribute values

From the required goal attributes, the goal duration sum
remains the best way to get even shorter searches.

Usage of multiple trials can also save time,
depending on wait times around trial traffic.

The farther the goal exceed ratio is from 0.5 (towards zero or one),
the less predictable the overal search duration becomes in practice.

Width parameter does not change search duration much in practice
(compared to other, mainly optional goal attributes).

## DUT in SUT

In practice, using multiple trials and moderate exceed ratios
often improves result repeatability without increasing the overall search time,
depending on the specific SUT and DUT characteristics.
Benefits for separating SUT noise are less clear though,
as it is not easy to distinguish SUT noise from DUT instability in general.

Conditional throughput has an intuitive meaning when described
using the performance spectrum, so this is an improvement
over existing simple (less configurable) search procedures.

Multiple trials can save time also when the noisy end of
the preformance spectrum needs to be examined, e.g. for [RFC9004].

Under some circumstances, testing the same DUT and SUT setup with different
DUT configurations can give some hints on what part of noise is SUT noise
and what part is DUT performance fluctuations.
In practice, both types of noise tend to be too complicated for that analysis.

MLRsearch enables users to search for multiple goals,
potentially providing more insight at the cost of a longer overall search time.
However, for a thorough and reliable examination of DUT-SUT interactions,
it is necessary to employ additional methods beyond black-box benchmarking,
such as collecting and analyzing DUT and SUT telemetry.

## Repeatability and Comparability

Multiple trials improve repeatability, depending on exceed ratio.

In practice, one-second goal final trial duration with exceed ratio 0.5
is good enough for modern SUTs.
However, unless smaller wait times around the traffic part of the trial
are allowed, too much of overal search time would be wasted on waiting.

It is not clear whether exceed ratios higher than 0.5 are better
for repeatability.
The 0.5 value is still preferred due to explainability using median.

It is possible that the conditional throughput values (with non-zero goal
loss ratio) are better for repeatability than the relevant lower bound values.
This is especially for implementations
which pick load from a small set of discrete values,
as that hides small variances in relevant lower bound values
other implementations may find.

Implementations focusing on shortening the overall search time
are automatically forced to avoid comparability issues due to load selection,
as they must prefer even splits wherever possible.
But this conclusion only holds when the same goals are used.
Larger adoption is needed before any further claims on comparability
between MLRsearch implementations can be made.

## Throughput with Non-Zero Loss

Trivially suported by the goal loss ratio attribute.

In practice, usage of non-zero loss ratio values
improves the result repeatability
(exactly as expected based on results from simpler search methods).

## Inconsistent Trial Results

MLRsearch is conservative wherever possible.
This is built into the definition of conditional throughput,
and into the treatment of short trial results for load classification.

This is consistent with [RFC2544] zero loss tolerance motivation.

If the noiseless part of the SUT performance spectrum is of interest,
it should be enough to set small value for the goal final trial duration,
and perhaps also a large value for the goal exceed ratio.

Implementations may offer other (optional) configuration attributes
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

Some phrases and statements in this document were created
with help of Mistral AI (mistral.ai).

Many thanks to Alec Hothan of the OPNFV NFVbench project for thorough
review and numerous useful comments and suggestions.

Special wholehearted gratitude and thanks to the late Al Morton for his
thorough reviews filled with very specific feedback and constructive
guidelines. Thank you Al for the close collaboration over the years,
for your continuous unwavering encouragement full of empathy and
positive attitude.
Al, you are dearly missed.

# Appendix A: Load Classification

This is the specification of how to perform the load classification.

Any intended load value can be classified, according to the given search goal.

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the measurer.

The block at the end of this appendix holds pseudocode
which computes two values, stored in variables named optimistic and pessimistic.
The pseudocode happens to be a valid Python code.

If both values are computed to be true, the load in question
is classified as a lower bound according to the given search goal.
If both values are false, the load is classified as an upper bound.
Otherwise, the load is classified as undecided.

The pseudocode expects the following variables to hold values as follows:

- goal_duration_sum: The duration sum value of the given search goal.

- goal_exceed_ratio: The exceed ratio value of the given search goal.

- good_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a trial loss ratio
  not higher than the goal loss ratio.

- bad_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a trial loss ratio
  higher than the goal loss ratio.

- good_short_sum: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with a trial loss ratio
  not higher than the goal loss ratio.

- bad_short_sum: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with a trial loss ratio
  higher than the goal loss ratio.

The code works correctly also when there are no trial results at the given load.

~~~ python
balancing_sum = good_short_sum * goal_exceed_ratio / (1.0 - goal_exceed_ratio)
effective_bad_sum = bad_long_sum + max(0.0, bad_short_sum - balancing_sum)
effective_whole_sum = max(good_long_sum + effective_bad_sum, goal_duration_sum)
quantile_duration_sum = effective_whole_sum * goal_exceed_ratio
optimistic = effective_bad_sum <= quantile_duration_sum
pessimistic = (effective_whole_sum - good_long_sum) <= quantile_duration_sum
~~~

# Appendix B: Conditional Throughput

This is the specification of how to compute conditional throughput.

Any intended load value can be used as the basis for the following computation,
but only the relevant lower bound (at the end of the search)
leads to the value called the conditional throughput for a given search goal.

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the measurer.

The block at the end of this appendix holds pseudocode
which computes a value stored as variable conditional_throughput.
The pseudocode happens to be a valid Python code.

The pseudocode expects the following variables to hold values as follows:

- goal_duration_sum: The duration sum value of the given search goal.

- goal_exceed_ratio: The exceed ratio value of the given search goal.

- good_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a trial loss ratio
  not higher than the goal loss ratio.

- bad_long_sum: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a trial loss ratio
  higher than the goal loss ratio.

- long_trials: An iterable of all trial results from trials with trial duration
  at least equal to the goal final trial duration,
  sorted by increasing the trial loss ratio.
  A trial result is a composite with the following two attributes available:

  - trial.loss_ratio: The trial loss ratio as measured for this trial.

  - trial.duration: The trial duration of this trial.

The code works correctly only when there if there is at least one
trial result measured at a given load.

~~~ python
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
~~~

--- back

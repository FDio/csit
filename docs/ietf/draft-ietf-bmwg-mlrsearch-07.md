---

<mark>mk edit note: I applied markdown `<mark>` `</mark>` markup throughout the document for all TODOs, edit notes and crossed-out or to-be-moved text. All markup must be removed before publishing.</mark>

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

[toc]

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
the MLRsearch test methodology specification employs the following enhancements:

- Allow multiple shorter trials instead of one big trial per load.
  - Optionally, tolerate a percentage of trial results with higher loss.
- Allow searching for multiple Search Goals, with differing loss ratios.
  - Any trial result can affect each Search Goal in principle.
- Insert multiple coarse targets for each Search Goal, earlier ones need
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
The conservative settings lead to results
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
server hardware and operating system functions,
with that server hardware resources shared across all programs including
the operating system.

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
not related to the rest of SUT. For example due to pauses in execution
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
based on authors' experience and available literature.

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

MLRsearch methodology aims to solve the DUT in SUT problem
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

Searching for multiple Search Goals also helps to describe the SUT performance
spectrum better than the result of a single Search Goal.
For example, the repeated wide gap between zero and non-zero loss loads
indicates the noise has a large impact on the observed performance,
which is not evident from a single goal load search procedure result.

It is easy to modify the vanilla bisection to find a lower bound
for the intended load that satisfies a non-zero goal loss ratio.
But it is not that obvious how to search for multiple goals at once,
hence the support for multiple Search Goals remains a problem.

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

This section describes MLRsearch specification including all technical definitions needed for evaluating
whether a particular test procedure complies with MLRsearch specification.

<mark>TODO mk: Unify "the" before "MLRsearch specification" when text is stable.</mark>

<mark>TODO mk: Recheck the definition dependencies go bottom-up.</mark>

<mark>~~For additional motivations, explanations, and other comments see other chapters.~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

<mark>Currently, the discussion paragraphs may contain requirements.
For example, if some quantity must be present in the test report,
it is useful to mention this after defining the quantity,
not after defining also the test report.</mark>

<mark>mk edit note: Above paragraph does not seem to bring any value. Suggest to remove it.</mark>

<mark>TODO mk: Separate Requirements and Recommendations/Suggestions paragraphs? (currently requirements are in discussion subsections - discussion should only clarify things without adding new requirements)</mark>
<mark>TODO mk: Which dependency order? (applies specifically to discussion)</mark>

## Overview

<mark>While definitions are ordered by their direct dependencies,
in discussion paragraphs it is useful to refer to terms properly defined later.
This section gives a quick introduction to some of such terms.</mark>

<mark>mk edit note: Above paragraph does not seem to bring any value. Suggest to remove it.</mark>

MLRsearch specification describes a set of abstract system components, acting as functions with specified inputs and outputs.

A test procedure is said to comply with MLRsearch specification
if it can be conceptually divided into analogous components,
each satisfying requirements for the corresponding MLRsearch component.

The Measurer component is tasked to perform trials,
the Controller component is tasked to select trial loads and durations,
the Manager component is tasked to pre-configure everything
and to produce the test report.
The test report explicitly states Search Goals (as the Controller Inputs)
and corresponding Goal Results (Controller Outputs).
<mark>TODO: Find a good reference for the test report, seems only implicit in RFC2544.</mark>

The Manager calls the Controller once,
the Controller keeps calling the Measurer
until all exit conditions are met.

The part where Controller calls the Measurer is called the search.
Any activity done by the Manager before it calls the Controller
(or after Controller returns) is not considered to be part of the search.

<mark>mk edit note: I think it is useful to use upper case letter for names of components, as it distinguishes them in the text and makes it clear to the reader that it Manager means a system components vs say a management function. Applied it above, but leaving as is in the rest of the document.</mark>

## Measurement Quantities

MLRsearch specification uses a number of measurement quantities.

In general, MLRsearch specification does not require particular units to be used,
but it is REQUIRED for the test report to state all the units.
For example, ratio quantities can be dimensionless numbers between zero and one,
but may be expressed as percentages instead.

For convenience, a group of quantities can be treated as a composite quantity,
One constituent of a composite quantity is called an attribute,
and a group of attribute values is called an instance of that composite quantity.

Some attributes are not independent from others,
and they can be calculated from other attributes.
Such quantites are called derived quantities.

## Relevant Existing Terms

These terms are already defined in earlier documents,
and apply in this document without any changes.

Only four existing terms are mentioned in this section and used in the following MLRsearch definitions.
Other existing terms are mentioned in discussion paragraphs. 
<mark>mk edit note: - is this redundant now? TODO VP: List those other existing terms. </mark>

<mark>mk edit note: - is this redundant now? TODO: Mention DUT and tester here, not in subsections?</mark>

### SUT

Defined in [RFC2285] (section 3.1.2 System Under Test (SUT)) as follows.

Definition:

The collective set of network devices to which stimulus is offered
as a single entity and response measured.

Discussion:

An SUT consisting of a single network device is also allowed.

### DUT

Defined in [RFC2285] (section 3.1.1 Device Under Test (DUT)) as follows.

Definition:

The network forwarding device to which stimulus is offered and
response measured.

Discussion:

DUT, as a sub-component of SUT, is only indirectly mentioned
in the MLRsearch specification, but is of key relevance for its motivation.

### Tester

<mark> TODO: Add Definition and Discusion paragraphs</mark>

<mark>mk edit note: Bizarre ... i can't find tester definition in rfc1242, rfc2288 or rfc2544, but will keep looking. If there isn't one, we need to define one :).</mark>


### Trial

A trial is the part of the test described in [RFC2544] (section 23. Trial description).

Definition:

It is ALLOWED for the test procedure to deviate from [RFC2544],
but any such deviation MUST be made explicit in the test report.
<mark>TODO: Strictly a change from rfc2544.</mark>

Discussion:

<mark>~~We say a trial is performed or measured. (TODO: reword without "we say")~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

Trials are the only stimuli the SUT is expected to experience
during the search.

Measuring trials is the responsibility of the Measurer component.
One call, one trial.

In some discussion paragraphs, it is useful to consider the traffic
as sent and received by a tester, as implicitly defined
in [RFC2544] (section 6. Test set up).

An example of deviation from [RFC2544] is using shorter wait times.

~~TODO: Do not re-send the learning frames?~~

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

~~TODO: Allow any deviation that never increases the Conditional Throughput?~~

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

## Trial Terms

This section defines new and redefine existing terms for quantities
relevant as inputs or outputs of trial, as used by the Measurer component.

### Trial Duration

Definition:

Trial duration is the intended duration of the traffic for a trial.

Discussion:

In general, this quantity does not include any preparation nor waiting
described in section 23 of [RFC2544] (section 23. Trial description).

While any positive real value may be provided, some Measurer implementations
MAY limit possible values, e.g. by rounding down to neared integer in seconds.
In that case, it is RECOMMENDED to give such inputs to the Controller
so the Controller only proposes the accepted values.
Alternatively, the test report MUST present the rounded values
as Search Goal attributes.

### Trial Load

Definition:

The trial load is the intended and constant load for a trial.

<mark>mk edit note: What about burst profile, where the packet load is not evenly distributed in time but instead is a series of packet bursts (packets sent at linerate in sequence) separated by inter-burst gap. E.g. see IXIA user guide [Bursts and the Inter-Burst GAP (IBG)](https://downloads.ixiacom.com/library/user_guides/IxOS/6.30/EA_6.30_Rev_A/IxiaReferenceGuide/GeneralTheory.html#wp1256803). We don't need to address it now, but if this question comes we should have an answer e.g. constant load has a burst profile that can be described by burst size (number of frames sent back-to-back at linerate) and inter-burst gap.</mark>

Discussion:

Trial load is the quantity defined as Constant Load of [RFC1242]
(section 3.4 Constant Load), Data Rate of [RFC2544]
(section 14. Bidirectional traffic)
and Intended Load of [RFC2285] (section 3.5.1 Intended load (Iload)).
All three definitions specify
that this value applies to one (input or output) interface.

For test report purposes, multi-interface aggregate load MAY be reported,
this is understood as the same quantity expressed using different units.
From the report it MUST be clear whether a particular trial load value
is per one interface, or an aggregate over all interfaces.

Similarly to trial duration, some Measurers may limit the possible values
of trial load. Contrary to trial duration, the test report is NOT REQUIRED
to document such behavior.

See further discussion in [Trial Forwarding Ratio](#Trial-Forwarding-Ratio)
and in [Measurer](#Measurer) sections for other related issues.

### Trial Input

Definition:

Trial Input is a composite quantity, consisting of two attributes:
trial duration and trial load.

Discussion:

When talking about multiple trials, it is common to say "Trial Inputs"
to denote all corresponding Trial Input instances.

A Trial Input instance acts as the input for one call of the Measurer component.

Contrary to other composite quantities, MLRsearch implementations
are NOT ALLOWED to add optional attributes here.
This improves interoperability between various implementations of
the Controller and the Measurer.

It is ALLOWED to combine trial load and trial duration in a way
that would not be possible to achieve using any integer number of data frames.

### Traffic profile

Definition:

Traffic profile is a composite quantity
containing attributes other than trial load and trial duration,
needed by the Measurer in order to perform one trial.

Discussion:

All its attributes are assumed to be constant during the search,
and the composite is configured on the Measurer by the Manager
before the search starts. 
This is why the traffic profile is not part of the Trial Input.

The traffic profile SHOULD contain some specific quantities,
for example [RFC2544] (section 9. Frame sizes) governs
data link frame size as defined in [RFC1224] (section 3.5 Data link frame size).

Several more specific quantities may be RECOMMENDED, depending on media type.
For example, [RFC2544] (Appendix C) lists frame formats and protocol addresses,
as recommended from [RFC2544] (section 8. Frame formats)
and [RFC2544] (section 12. Protocol addresses).

Depending on SUT configuration, e.g. when testing specific protocols,
additional attributes MUST be included in the traffic profile
and in the test report.
See relevant IETF documents.

Example: [RFC8219] (section 5.3. Traffic Setup) introduces traffic setups
consisting of a mix of IPv4 and IPv6 traffic - the implied traffic profile
therefore must include an attribute for their percentage.

As a consequence, implementations of the Manager and the Measurer
must be aware of their common set of capabilities, so that the traffic profile
uniquely defines the traffic during the search.
The important fact is that none of those capabilities
have to be known by the Controller implementations.

### Trial Forwarding Ratio

Definition:

The trial forwarding ratio is a dimensionless floating point value.
It MUST range between 0.0 and 1.0, both inclusive.
It is calculated by dividing the number of frames
successfully forwarded by the SUT
by the total number of frames expected to be forwarded during the trial (i.e. transmitted by Tester and reaching SUT).

Discussion:

Trial forwarding ratio MAY be expressed in other units
(e.g. as a percentage) in the test report.

Note that, contrary to loads, frame counts used to compute
trial forwarding ratio are aggregates over all SUT output interfaces.

Questions around what is the correct number of frames
that should have been forwarded
is generally outside of the scope of this document.
See discussion in [Measurer](#Measurer) section for more details about calibrating test equipment.

<mark>mk edit note: we need to more explicitly address the relevance or irrelevance of [RFC2285] (Section 3.5.2 Offered load (Oload)). Current text in [Trial Output](#Trial-Output) is ambiguous.</mark>

<mark>mk edit note: I think it is useful to add local hyperlinks to this document sections and subsections to make it easier and faster for reader to cross-reference and cross-verify across different parts of this specification.</mark>

### Trial Loss Ratio

Definition:

The trial loss ratio is equal to one minus the trial forwarding ratio.

Discussion:

100% minus the trial forwarding ratio, when expressed as a percentage.

This is almost identical to Frame Loss Rate of [RFC1242]
(section 3.6 Frame Loss Rate),
the only minor difference is that Trial Loss Ratio
does not need to be expressed as a percentage
<mark>~~(assuming lack of resources is still the only cause of frame loss).~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

<mark>mk edit note: I think it is useful to use upper case letter for names of quantities too.</mark>

### Trial Forwarding Rate

Definition:

The trial forwarding rate is a derived quantity, calculated by
multiplying the trial load by the trial forwarding ratio.

Discussion:

It is important to note that while similar, this quantity is not identical
to the Forwarding Rate as defined in [RFC2285]
(section 3.6.1 Forwarding rate (FR)).
The latter is specific to one output interface only,
whereas the trial forwarding ratio is based
on frame counts aggregated over all SUT output interfaces.

### Trial Effective Duration

Definition:

Trial effective duration is a time quantity related to the trial,
by default equal to the trial duration.

Discussion:

This is an optional feature.
If the Measurer does not return any trial effective duration value,
the Controller MUST use the trial duration value instead.

Trial effective duration may be any time quantity chosen by the Measurer
to be used for time-based decisions in the Controller.

The test report MUST explain how the Measurer computes the returned
trial effective duration values, if they are not always
equal to the trial duration.

This feature can be beneficial for users
who wish to manage the overall search duration,
rather than solely the traffic portion of it.

Also, this is a way for the Measurer to inform the Controller about
its surprising behavior, for example when rounding the trial duration value.

<mark>TODO: Recommend for Measurer to return all trials at relevant bounds,
as that may better inform users when surprisingly small amount of trials
was performed, just because the the trial effective duration values were big.</mark>

### Trial Output

Definition:

Trial Output is a composite quantity. The REQUIRED attributes are
trial loss ratio, trial effective duration and trial forwarding rate.

Discussion:

When talking about multiple trials, it is common to say "Trial Outputs"
to denote all corresponding Trial Output instances.

Implementations may provide additional (optional) attributes.
The Controller implementations MUST ignore values of any optional attribute
they are not familiar with,
except when passing Trial Output instance to the Manager.

For example: the total number of frames expected to be forwarded during the trial,
especially if it is not just a rounded-up value
implied by trial load and trial duration.

While [RFC2285] (Section 3.5.2 Offered load (Oload))
requires the offered load value to be reported for forwarding rate measurements,
it is NOT REQUIRED in the MLRsearch specification.

<mark>~~TODO: Why? Just because bound trial results are optional in Controller Output?~~</mark>

<mark>mk edit note: we need to more explicitly address the relevance or irrelevance of [RFC2285] (Section 3.5.2 Offered load (Oload)). Current text in [Trial Load](#Trial-Load) is ambiguous - quoted below.</mark>

<mark>"Questions around what is the correct number of frames
that should have been forwarded
is generally outside of the scope of this document.
See discussion in [Measurer](#Measurer) section for more details about calibrating test equipment."</mark>

### Trial Result

Definition:

Trial result is a composite quantity,
consisting of the Trial Input and the Trial Output.

Discussion:

When talking about multiple trials, it is common to say "trial results"
to denote all corresponding trial result instances.
<mark>~~TODO: Polish the wording.~~</mark>

<mark>mk edit note: Wording is simple, short and good. Above line is not needed and needs to be removed.</mark>

## Goal Terms

<mark>mk edit note: Shouldn't this section be named "Goal Quantities" instead?</mark>

This section defines new and redefine existing terms for quantities
indirectly relevant for inputs or outputs of the Controller component.

Several goal attributes are defined before introducing
the main component quantity: the Search Goal.

<mark>~~Each subsection contains a short informal description,
but see other chapters for more in-depth explanations.~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

<mark>~~TODO: "subsection" or "sub-section"?~~</mark>

<mark>mk edit note: "subsection" is more common and correct according to OED and AED. Above line is not needed and needs to be removed.</mark>

### Goal Final Trial Duration

Definition:

A threshold value for trial durations.

Discussion:

This attribute value MUST be positive.

Trials with trial duration at least as long as the goal final trial duration
are called full-length trials with respect to the given Search Goal.

Informally, while MLRsearch is allowed to perform trials shorter than full-length,
the results from such short trials have only limited impact on search results.

One trial may be full-length for some Search Goals, but not for others.

The full relation of this goal to Controller Output is defined later in this document in section [Controller Output](#Controller-Output).
For example, the Conditional Throughput
for this goal is computed only from full-length trial results.

### Goal Duration Sum

Definition:

A threshold value for a particular sum of trial effective durations.

Discussion:

This attribute value MUST be positive.

Informally, even when looking only at full-length trials,
MLRsearch may spend up to this time measuring the same load value.

<mark>If the goal duration sum is larger than the goal final trial duration,
multiple full-length trials may need to be performed at the same load.</mark>

<mark> mk edit note: Above sentence does not make sense to me. Can you provide some examples of cases when the goal duration sum is > goal final trial duration, and multiple full-length trials need to be performed as per sentence?</mark>

### Goal Loss Ratio

Definition:

A threshold value for trial loss ratios.

Discussion:

Attribute value MUST be non-negative and smaller than one.

A trial with trial loss ratio larger than a goal loss ratio value
is called a "lossy" trial, with respect to given Search Goal.

Informally, if a load causes too many lossy trials,
the Relevant Lower Bound for this goal will be smaller than that load.

### Goal Exceed Ratio

Definition:

A threshold value for a particular ratio of sums of trial effective durations.

Discussion:

Attribute value MUST be non-negative and smaller than one.

<mark>See later sections for details on which sums.</mark>

<mark>mk edit note: Which sections?</mark>

Informally, the impact of lossy trials is controlled by this value.
<mark>The full relation needs definitions is later subsections.</mark>

<mark>mk edit note: This is ambigouous and contentless. "needs" or "is provided"? Need hyperlink to related section(s).</mark>

For example, the definition of the Conditional Throughput (see section [Conditional Throughput](#Conditional-Throughput))
refers to a q-value  

<mark>mk edit note: By "q-value" I think you mean ["q-quantile" value](https://en.wikipedia.org/wiki/Quantile) and not ["q-value" statistics value](https://en.wikipedia.org/wiki/Q-value_(statistics)), or do you really mean the [Storey procedure](https://en.wikipedia.org/wiki/Q-value_(statistics)), or some other meaning of [Q value](https://en.wikipedia.org/wiki/Q_value) :)? Also, there is no "q-value" referred to in sections [Conditional Throughput](#Conditional-Throughput) and [Appendix B: Conditional Throughput](#Appendix-B\:-Conditional-Throughput).</mark>

<mark>(TODO: recheck Discussion there.)</mark>

<mark>mk edit note: This looks like mental shortcut of your Vratko.</mark>

for a quantile when selecting
which trial result gives the Conditional Throughput.
<mark>The Goal Exceed Ratio acts as the q-value to use there.</mark>

<mark>mk edit note: See my earlier note re "q-value".</mark>

Specifically, when the Goal Exceed Ratio is 50%, and MLRsearch happened
to use the whole [Goal Duration Sum](#Goal-Duration-Sum) (using full-length trials)
at the [Relevant Lower Bound](#Relevant-Lower-Bound),
it means the Conditional Throughput is the median of the Trial Forwarding Rates.

### Goal Width

Definition:

<mark>A value used as a threshold for deciding
whether two trial load values are close enough
for search exit condition purposes.</mark>

<mark> mk edit note: Is "search exit condition" described anywhere? There is some text in [Controller](#Controller) section, but it's not a complete description or definition.</mark>

<mark>~~(TODO: wording?)~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

Discussion:

If present, the value MUST be positive.

Informally, this acts as an exit condition,
controlling the precision of the search.
The search stops if every goal has reached its precision.

Implementations without this attribute
MUST give the Controller other ways to control the search exit conditions.

Absolute load difference and relative load difference are two popular choices,
but implementations may choose a different way to specify width.

The test report MUST make it clear what specific quantity is used as Goal Width.

<mark>~~TODO: Assume absolute or relative width just based on the unit?~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

### Search Goal

Definition:

The Search Goal is a composite quantity consisting of several attributes,
some of them are required.

Required attributes: <mark>~~(TODO: capitalization)~~</mark>
- Goal Final Trial Duration
- Goal Duration Sum
- Goal Loss Ratio
- Goal Exceed Ratio

Optional attribute:
- Goal Width

Discussion:

Implementations are free to add their own additional optional attributes.

<mark>The meaning of listed attributes is formally given only by their effect
on the Controller Output attributes
(defined in later in section [Search Result](#Search-Result)).</mark>

<mark>mk edit note: I can't see any of these attributes mentioned in [Search Result](#Search-Result). Either they have to be added there, or this sentence to be changed or removed.</mark>

Informally, later sections provide additional intuitions and examples
of the Search Goal attribute values.
Later sections also give motivation for formulas used to produce the outputs.

An example of additional attributes required by some implementations
is a goal initial trial duration, together with another attribute
that controls possible intermediate Trial Duration values.

### Controller Input

<mark>mk edit note: Shouldn't this section be indented one level up, as it is not really a subsection of "Goal Terms"?</mark>

Definition:

Controller Input is a composite quantity
required as an input for the Controller.
The only REQUIRED attribute is a list of Search Goal instances.

Discussion:

MLRsearch implementations MAY use additional attributes,
e.g. when tweaking some time-related behavior.

Formally, the Manager does not apply any Controller configuration
apart from one Controller Input instance.

<mark>Any other assumed pieces of configuration (e.g. traffic profile)
are passed (as if) outside the visibility of the Controller.</mark>

<mark>mk edit note: Unclear sentence. "are passed" where and by whom and what for?</mark>

The order of Search Goal instances in a list SHOULD NOT
have a big impact on Controller Output (see section [Controller Output](#Controller-Output) ,
but MLRsearch implementations MAY base their behavior on the order
of Search Goal instances in a list.

<mark>The Search Goal instances SHOULD NOT be identical.
MLRsearch implementation MAY allow identical instances.</mark>

<mark>mk edit note: Unclear what this sentence means. Does it mean "The Search Goal instances (with their values) in the list SHOULD NOT be identical", and if yes, why would MLRsearch implementation allow this?</mark>

An example of an optional attribute (outside the list of Search Goals)
required by some implementations is max load.
While this is a frequently used configuration parameter,
already governed by [RFC2544] (section 20. Maximum frame rate)
and [RFC2285] (3.5.3 Maximum offered load (MOL)),
some implementations may detect or discover it instead.

In MLRsearch specification, the Relevant Upper Bound (see section [Relevant Upper Bound](#Relevant-Upper-Bound)) was added
as a required attribute precisely because it makes the search result
independent of max load value.
<mark>~~TODO: Move some of this into upper relevant bound Discussion?~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

## Result Terms

Before defining the output of the Controller,
it is useful to define what the Goal Result is.

The Goal Result is a composite quantity. 

Following subsections define its attribute first, before describing the Goal Result quantity.

There is a correspondence between Search Goals and Goal Results.
Most of the following subsections refer to a given Search Goal,
when defining attributes of the Goal Result.
Conversely, at the end of the search, each Search Goal
has its corresponding Goal Result.

Conceptually, the search can be seen as a process of load classification,
where the Controller attempts to classify some loads as an Upper Bound
or a Lower Bound with respect to some Search Goal.

<mark>~~TODO: Irregular Goal Result instances may need to be mentioned here already.~~<mark>

<mark>mk edit note: This shouldn't be covered here, but elsewhere, if at all. Above line is not needed and needs to be removed.</mark>

### Relevant Upper Bound

Definition:

The Relevant Upper Bound is the smallest trial load value that is classified
at the end of the search as an upper bound (see Appendix A)
for the given Search Goal.

Discussion:

Informally, this is the smallest intended load that failed to uphold
all the requirements of the given Search Goal, mainly the goal loss ratio
in combination with the goal exceed ratio.

If max load does not cause enough lossy trials,
the Relevant Upper Bound does not exist.

### Relevant Lower Bound

Definition:

The Relevant Lower Bound is the largest trial load value
among those smaller than the Relevant Upper Bound,
that got classified at the end of the search
as a lower bound (see Appendix A) for the given Search Goal.

Discussion:

For a regular Goal Result, the distance between the Relevant Lower Bound
and the Relevant Upper Bound MUST NOT be larger than the goal width,
if the implementation offers width as a goal attribute.

Informally, this is the largest intended load that managed to uphold
all the requirements of the given Search Goal, mainly the goal loss ratio
in combination with the goal exceed ratio, while not being larger
than the Relevant Upper Bound.

Strictly speaking, if the Relevant Upper Bound does not exist,
the Relevant Lower Bound also does not exist.
Max load usually is classified as a lower bound,
but it is not clear whether a higher lower bound
would be found if the search used a higher max load value.

### Conditional Throughput

Definition:

The Conditional Throughput (see section [Appendix B: Conditional Throughput](#Appendix-B\:-Conditional-Throughput))
as evaluated at the Relevant Lower Bound of the given Search Goal
at the end of the search.

Discussion:

Informally, this is a typical trial forwarding rate, expected to be seen
at the Relevant Lower Bound of the given Search Goal.

But frequently it is only a conservative estimate thereof,
as MLRsearch implementations tend to stop gathering more data
as soon as they confirm the value cannot get worse than this estimate
within the goal duration sum.

This value is RECOMMENDED to be used when evaluating repeatability
and comparability if different MLRsearch implementations.

### <mark>~~TODO: Trial results at relevant bounds?~~</mark>

<mark>mk edit note: Why is this needed here and not elsewhere e.g. in [Trial Result](#Trial-Result) section, if at ll. Above line is not needed and needs to be removed.</mark>

### <mark>Goal Result</mark>

<mark>mk edit note:  Discussion paragraphs are ambiguous and incomplete. Requires work.</mark>

Definition:

The Goal Result is a composite quantity consisting of several attributes.
Relevant Upper Bound and Relevant Lower Bound are required attributes,
Conditional Throughput is a recommended attribute.

Discussion:

<mark>Any Goal Result instance can be either regular or irregular.
TODO: Separate definition for regular instances?</mark>

<mark>mk edit note:  Definitions of regular and irregular Goal Result instance is missing. Above sentence needs to be edited or removed.</mark>

<mark>MLRsearch specification puts requirements on regular Goal Result instances.
Any instance that does not meet the requirements is deemed irregular.</mark>

<mark>mk edit note: Definitions of regular and irregular Goal Result instance is missing. Above sentence needs to be edited or removed.</mark>

<mark>Some of the attributes of a regular Goal Result instance are required,
some are recommended, implementations are free to add their own.</mark>

<mark>mk edit note: Definitions of regular and irregular Goal Result instance is missing. Above sentence needs to be edited or removed.</mark>

<mark>(TODO: trial results here if not before)</mark>

<mark>mk edit note: This does not make sense here. Above line is not needed and needs to be removed.</mark>

<mark>Implementations are free to define their own specific subtypes
of irregular Goal Results, but the test report MUST mark them clearly
as irregular according to this section.</mark>

<mark>mk edit note:  Definitions of regular and irregular Goal Result instance is missing. Above sentence needs to be edited or removed.</mark>

<mark>A typical irregular result is when all trials at the max load
have zero loss, as the Relevant Upper Bound does not exist in that case.</mark>

<mark>mk edit note: this is an example not a definition. Definitions of regular and irregular Goal Result instance is missing. Above sentence needs to be edited or removed.</mark>

### Search Result

Definition:

The Search Result is a single composite object
that maps each Search Goal instance to a corresponding Goal Result instance.

Discussion:

Alternatively, the Search Result can be implemented as an ordered list
of the Goal Result instances, matching the order of Search Goal instances.

The Search Result (as a mapping)
MUST map from all the Search Goal instances present in the Controller Input.
<mark>~~The Search Goal instances MAY be irregular.~~</mark>
<mark>~~TODO: Irregular search result if at least one irregular Goal Result?~~</mark>

<mark>mk edit note:  See my earlier note about irregular result.</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

<mark>~~TODO: Discuss API / interoperability~~</mark>
<mark>~~between Manager and several Controller implementations,~~</mark>
<mark>~~especially re telemetry and irregular Goal Results.~~</mark>

<mark>mk edit note: Why is it needed here and now? If needed, can we move it to future work that is out of scope or other considerations that are out of scope of this document?</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

### Controller Output

Definition:

The Controller Output is a composite quantity returned from the Controller
to the Manager at the end of the search.
The Search Result instance is its only REQUIRED attribute.

Discussion:

MLRsearch implementation MAY return additional data in the Controller Output.

<mark>~~TODO: Pass-through logging from Measurer, debug logging from Controller.~~</mark>

<mark>mk edit note: Why is it needed here and now? If needed, can we move it to future work that is out of scope or other considerations that are out of scope of this document?</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

## Architecture Terms

MLRsearch architecture consists of three main system components:
the Manager, the Controller, and the Measurer.

The architecture also implies the presence of other components,
such as the SUT and the Tester (as a sub-component of the Measurer).

Protocols of communication between components are generally left unspecified.
For example, when MLRsearch specification mentions "Controller calls Measurer",
it is possible that the Controller notifies the Manager
to call the Measurer indirectly instead. This way the Measurer implementations
can be fully independent from the Controller implementations,
e.g. programmed in different programming languages.

### Measurer

Definition:

The Measurer is an abstract system component
that when called with a [Trial Input](#Trial-Input) instance,
performs one trial as described in [RFC2544] (section 23. Trial description),
and returns a [Trial Output](#Trial-Output) instance.

Discussion:

This definition assumes the Measurer is already initialized.
In practice, there may be additional steps before the search,
e.g. when the Manager configures the traffic profile
(either on the Measurer or on its tester sub-component directly)
and performs a warmup (if the tester requires one).

It is the responsibility of the Measurer implementation to uphold
any requirements and assumptions present in MLRsearch specification,
e.g. trial forwarding ratio not being larger than one.

Implementers have some freedom.
For example [RFC2544] (section 10. Verifying received frames)
gives some suggestions (but not requirements) related to
duplicated or reordered frames.
Implementations are RECOMMENDED to document their behavior
related to such freedoms in as detailed a way as possible.

It is RECOMMENDED to benchmark the test equipment first,
e.g. connect sender and receiver directly (without any SUT in the path),
find a load value that guarantees the offered load is not too far
from the intended load, and use that value as the max load value.
When testing the real SUT, it is RECOMMENDED to turn any big difference
between the intended load and the offered load into increased trial loss ratio.

Neither of the two recommendations are made into requirements,
because it is not easy to tell when the difference is big enough,
in a way thay would be dis-entangled from other Measurer freedoms.

### Controller

Definition:

The Controller is an abstract system component
that when called with a Controller Input instance
repeatedly computes Trial Input instance for the Measurer,
obtains corresponding Trial Output instances,
and eventually returns a Controller Output instance.

Discussion:

<mark>Goal width or other attributes act directly as requirements
for search result precision, and indirectly as the search exit conditions.</mark>

<mark>mk edit note:  Does this sentence belong here?</mark>

Informally, the Controller has big freedom in selection of Trial Inputs,
and the implementations want to achieve the Search Goals
in the shortest expected time.

The Controller's role in optimizing the overall search time
distinguishes MLRsearch algorithms from simpler search procedures.

<mark>~~TODO: Mention implementations (versions) being replaceable?~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

<mark>~~Different implementations may require additional attributes from the Manager.~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

### Manager

Definition:

The Manager is an abstract system component
that is reponsible for configuring other components,
calling the Controller component once,
and for creating the test report following the reporting format as defined in [RFC2544] (section 26. Benchmarking tests).

Discussion:

The Manager initializes the SUT, the Measurer (and the Tester if independent)
with their intended configurations before calling the Controller.

The Manager does not need to be able to tweak any Search Goal attributes,
but it MUST report all applied attribute values even if not tweaked.

In principle, there sould be a "user" (human or CI)
that "starts" or "calls" the Manager and receives the report.
The Manager MAY be able to be called more than once whis way.
<mark>~~TODO: Reword.~~</mark>

<mark>mk edit note: Wording is good. Above line is not needed and needs to be removed.</mark>

<mark>The Manager may use the Measurer or other system components
to perform other tests, e.g. back-to-back frames,
as the Controller is only replacing the search from
[RFC2544] (section 26.1 Throughput).</mark>

<mark>mk edit note: Is above sentence needed? What value does it bring?</mark>

<mark>mk edit note: And if we need it, shouldn't it say: The Manager may use the Controller or other system components to perform other tests, e.g. back-to-back frames, as the Controller is only replacing the search from [RFC2544] (section 26.1 Throughput).</mark>

### <mark>MLRsearch Architecture</mark>

<mark>mk edit note: Is "MLRsearch Architecture" a term to be defined? Shouldn't this be renamed to "MLRsearch Specification Compliance" or similar?</mark>

Definition:

Any setup where there can be logically delineated system components
and there are components satisfying requirements for the Measurer,
the Controller and the Manager.

Discussion:

These components can be seen as abstractions present in any testing procedure.
For example, there can be a single component acting both
as the Manager and the Controller, but as long as values of required attributes
of Search Goals and Goal Results are visible in the test report,
the Controller Input instance and output instance are implied.

<mark>For example, any setup for conditionally compliant [RFC2544]
(section 26.1 Throughput) throughput testing</mark>

<mark>mk edit note: I don't see any conditions or conditional compliance being specified in RFC2544 section 26.1. IOW this sentence doesn't make sense.</mark>

can be understood as a MLRsearch architecture,
assuming there is enough data to reconstruct the Relevant Upper Bound.
<mark>TODO: Move the Search Goal instance for 2544 compliant search here.</mark>

<mark>mk edit note: This is unclear and looks like mental shortcut. There is mention of compliance with RFC2544 in [Purpose and Scope](#Purpose-and-Scope) and in [[RFC2544] Compliance](#\[RFC2544\]-Compliance) . Do you mean moving content from these sections into here, or something else?</mark>

Any test procedure that can be understood as (one call to the Manager of)
MLRsearch architecture is said to be compliant with MLRsearch specification.

<mark>TODO: Why do we need both architecture and specification?</mark>

<mark>mk edit note: We don't. See my edit note below the section title.</mark>

<mark>~~TODO: Does the test procedure need to be able to produce a regular search result?~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

<mark>~~TODO: Modularity, e.g. freedom to swap Measurer hardware and Controller software
as long as the Manager understands communication protocols of both?~~</mark>

<mark>mk edit note: Why is it needed here and now? If needed, can we move it to future work that is out of scope or other considerations that are out of scope of this document?</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

# Additional Considerations

<mark>mk edit note: Renamed this section from "Further Explanations", as it better reflects the content.</mark>

This section focuses on additional consideration, intuitions and motivations pertaining to MLRsearch methodology.

Familiarity with the MLRsearch specification is not required here,
so this section can act as an introduction.
<mark>~~For example, this chapter starts talking about the tightest lower bounds
before it is ready to talk about the Relevant Lower Bound
from the MLRsearch specification.~~</mark>

<mark>mk edit note: Above line is not needed and needs to be removed.</mark>

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

This is formalized using new notions, the Relevant Upper Bound and
the Relevant Lower Bound.
Load classification is still based just on the set of trial results
at a given intended load (trials at other loads are ignored),
making it possible to have a lower load classified as an upper bound,
and a higher load classified as a lower bound (for the same goal).
The Relevant Upper Bound (for a goal) is the smallest load classified
as an upper bound.
But the Relevant Lower Bound is not simply
the largest among lower bounds.
It is the largest load among loads
that are lower bounds while also being smaller than the Relevant Upper Bound.

With these definitions, the Relevant Lower Bound is always smaller
than the Relevant Upper Bound (if both exist), and the two relevant bounds
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
of the full trial durations, so Conditional Throughput becomes identical to
a median of a particular set of trial forwarding rates.

The presence of shorter trial results complicates the load classification logic.
Full details are given later.
In short, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the Relevant Lower Bound
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

MLRsearch defines one such generalization, called the Conditional Throughput.
It is the trial forwarding rate from one of the trials
performed at the load in question.
Specification of which trial exactly is quite technical,
see the specification and Appendix B.

Conditional Throughput is partially related to load classification.
If a load is classified as a lower bound for a goal,
the Conditional Throughput can be calculated,
and guaranteed to show an effective loss ratio
no larger than the goal loss ratio.

While the Conditional Throughput gives more intuitive-looking values
than the Relevant Lower Bound, especially for non-zero goal loss ratio values,
the actual definition is more complicated than the definition of the relevant
lower bound.
In the future, other intuitive values may become popular,
but they are unlikely to supersede the definition of the Relevant Lower Bound
as the most fitting value for comparability purposes,
therefore the Relevant Lower Bound remains a required attribute
of the Goal Result structure, while the Conditional Throughput is only optional.

Note that comparing the best and worst case, the same Relevant Lower Bound value
may result in the Conditional Throughput differing up to the goal loss ratio.
Therefore it is rarely needed to set the goal width (if expressed
as the relative difference of loads) below the goal loss ratio.
In other words, setting the goal width below the goal loss ratio
may cause the Conditional Throughput for a larger loss ratio to become smaller
than a Conditional Throughput for a goal with a smaller goal loss ratio,
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
Relevant Lower Bounds is when the interval is split in a very uneven way.
Any implementation choosing loads very close to the current Relevant Lower Bound
is quite likely to eventually stumble upon a trial result
with poor performance (due to SUT noise).
For an implementation choosing loads very close
to the current Relevant Upper Bound, this is unlikely,
as it examines more loads that can see a performance
close to the noiseless end of the SUT performance spectrum.

However, as even splits optimize search duration at give precision,
MLRsearch implementations that prioritize minimizing search time
are unlikely to suffer from any such bias.

Therefore, this document remains quite vague on load selection
and other optimization details, and configuration attributes related to them.
Assuming users prefer libraries that achieve short overall search time,
the definition of the Relevant Lower Bound
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

The following Search Goal ensures unconditional compliance with
[RFC2544] throughput search procedure:

- Goal loss ratio: zero.

- Goal final trial duration: 60 seconds.

- Goal duration sum: 60 seconds.

- Goal exceed ratio: zero.

The presence of other Search Goals does not affect the compliance
of this Goal Result.
The Relevant Lower Bound and the Conditional Throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

If the 60 second quantity is replaced by a smaller quantity in both attributes,
the Conditional Throughput is still conditionally compliant with
[RFC2544] throughput.

# Logic of Load Classification

This chapter continues with explanations,
but this time more precise definitions are needed
for readers to follow the explanations.
The definitions here are wordy, implementers should read MLRsearch specification
chapter and appendices for more concise definitions.

The two related areas of focus in this chapter are load classification
and the Conditional Throughput, starting with the latter.

The section Performance Spectrum contains definitions
needed to gain insight into what Conditional Throughput means.
The rest of the subsections discuss load classification,
they do not refer to Performance Spectrum, only to a few duration sums.

For load classification, it is useful to define good and bad trials.
A trial is called bad (according to a goal) if its trial loss ratio
is larger than the goal loss ratio.
The trial that is not bad is called good.

## Performance Spectrum

There are several equivalent ways to explain
the Conditional Throughput computation.
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
The Conditional Throughput will be one such quantile value
for a specifically chosen set of trials.

Take a set of all full-length trials performed at the Relevant Lower Bound,
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
The resulting quantity is the Conditional Throughput of the goal in question.

First example.
For zero exceed ratio, when goal duration sum has been reached.
The Conditional Throughput is the smallest trial forwarding rate among the trials.

Second example.
For zero exceed ratio, when goal duration sum has not been reached yet.
Due to the missing duration sum, the worst case may still happen,
so the Conditional Throughput is zero.
This is not reported to the user,
as this load cannot become the Relevant Lower Bound yet.

Third example.
Exceed ratio 50%, goal duration sum two seconds,
one trial present with the duration of one second and zero loss.
The imaginary trial is added with the duration
of one second and zero trial forwarding rate.
The median would touch both trials, so the Conditional Throughput
is the trial forwarding rate of the one non-imaginary trial.
As that had zero loss, the value is equal to the offered load.

Note that Appendix B does not take into account short trial results.

### Summary

While the Conditional Throughput is a generalization of the trial forwarding rate,
its definition is not an obvious one.

Other than the trial forwarding rate, the other source of intuition
is the quantile in general, and the median the the recommended case.

In future, different quantities may prove more useful,
especially when applying to specific problems,
but currently the Conditional Throughput is the recommended compromise,
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
the Conditional Throughput computation, so in this single trial duration case,
a load is a lower bound if and only if the Conditional Throughput
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
and the Conditional Throughput is only partial.
The Conditional Throughput still comes from a good long trial,
but a load higher than the Relevant Lower Bound may also compute to a good value.

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

One exception is the impact of short trial results on the Relevant Lower Bound.
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

Conditional Throughput has an intuitive meaning when described
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

It is possible that the Conditional Throughput values (with non-zero goal
loss ratio) are better for repeatability than the Relevant Lower Bound values.
This is especially for implementations
which pick load from a small set of discrete values,
as that hides small variances in Relevant Lower Bound values
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
This is built into the definition of Conditional Throughput,
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

Any intended load value can be classified, according to the given Search Goal.

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the Measurer.

The block at the end of this appendix holds pseudocode
which computes two values, stored in variables named optimistic and pessimistic.
The pseudocode happens to be a valid Python code.

If both values are computed to be true, the load in question
is classified as a lower bound according to the given Search Goal.
If both values are false, the load is classified as an upper bound.
Otherwise, the load is classified as undecided.

The pseudocode expects the following variables to hold values as follows:

- goal_duration_sum: The duration sum value of the given Search Goal.

- goal_exceed_ratio: The exceed ratio value of the given Search Goal.

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

This is the specification of how to compute Conditional Throughput, as referred to in section [Conditional Throughput](#Conditional-Throughput).

Any intended load value can be used as the basis for the following computation,
but only the Relevant Lower Bound (at the end of the search)
leads to the value called the Conditional Throughput for a given Search Goal.

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the Measurer.

The block at the end of this appendix holds pseudocode
which computes a value stored as variable conditional_throughput.
The pseudocode happens to be a valid Python code.

The pseudocode expects the following variables to hold values as follows:

- goal_duration_sum: The duration sum value of the given Search Goal.

- goal_exceed_ratio: The exceed ratio value of the given Search Goal.

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

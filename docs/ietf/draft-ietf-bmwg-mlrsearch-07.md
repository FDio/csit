---

title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-07
date: 2024-07-18

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
  RFC8219:
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
such as allowing multiple short trials per load instead of one large trial,
tolerating a certain percentage of trial results with higher loss,
and supporting the search for multiple goals with varying loss ratios.

--- middle

{::comment}

    As we use Kramdown to convert from Markdown,
    we use this way of marking comments not to be visible in the rendered draft.
    https://stackoverflow.com/a/42323390
    If another engine is used, convert to this way:
    https://stackoverflow.com/a/20885980

    [toc]

{:/comment}


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

- Allow multiple short trials instead of one big trial per load.
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

{::comment}
    [Low priority]

    <mark>MKP2 [VP] TODO: Look for mentions of search duration in existing RFCs.</mark>

    <mark>MKP2 [VP] TODO: If not found, define right after defining "the search".</mark>

{:/comment}

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
of SUT performance spectrum, more frequently and more widely than short
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

[RFC1242] (section 3.17 Throughput) defines throughput as:
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
  to its noiseless performance, thus perhaps lowering the Trial Loss Ratio
  below the Goal Loss Ratio value.

- If an approximation of the SUT noise impact on the Trial Loss Ratio is known,
  it can be set as the Goal Loss Ratio.

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
for the intended load that satisfies a non-zero Goal Loss Ratio.
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
from short trial durations.
The second place is section 26.3, where two successive zero-loss trials
are recommended, presumably because after one zero-loss trial
there can be a subsequent inconsistent non-zero-loss trial.

Examples include:

- A trial at the same load (same or different trial duration) results
  in a different Trial Loss Ratio.
- A trial at a higher load (same or different trial duration) results
  in a smaller Trial Loss Ratio.

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

This section describes MLRsearch specification including all technical
definitions needed for evaluating whether a particular test procedure
complies with MLRsearch specification.

{::comment}
    [Good idea for 08, maybe ask BMWG first?]

    <mark>TODO VP: Separate Requirements and Recommendations/Suggestions
    paragraphs? (currently requirements are in discussion subsections -
    discussion should only clarify things without adding new
    requirements)</mark>

{:/comment}

## Overview

MLRsearch specification describes a set of abstract system components,
acting as functions with specified inputs and outputs.

A test procedure is said to comply with MLRsearch specification
if it can be conceptually divided into analogous components,
each satisfying requirements for the corresponding MLRsearch component.

The Measurer component is tasked to perform trials,
the Controller component is tasked to select trial loads and durations,
the Manager component is tasked to pre-configure everything
and to produce the test report.
The test report explicitly states Search Goals (as the Controller Inputs)
and corresponding Goal Results (Controller Outputs).

{::comment}
    [Low priority]

    <mark>MKP2 TODO: Find a good reference for the test report, seems only implicit in RFC2544.</mark>

{:/comment}

The Manager calls the Controller once,
the Controller keeps calling the Measurer
until all stopping conditions are met.

The part where Controller calls the Measurer is called the search.
Any activity done by the Manager before it calls the Controller
(or after Controller returns) is not considered to be part of the search.

MLRsearch specification prescribes regular search results and recommends
their stopping conditions. Irregular search results are also allowed,
they may have different requirements and stopping conditions.

Search results are based on load classification.
When measured enough, any chosen load either achieves of fails each search goal,
thus becoming a lower or an upper bound for that goal.
When the relevant bounds are at loads that are close enough
(according to goal precision), the regular result is found.
Search stops when all regular results are found
(or if some goals are proven to have only irregular results).

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

## Existing Terms

RFC 1242 "Benchmarking Terminology for Network Interconnect Devices"
contains basic definitions, and
RFC 2544 "Benchmarking Methodology for Network Interconnect Devices"
contains discussions of a number of terms and additional methodology requirements.
RFC 2285 adds more terms and discussions, describing some known situations
in more precise way.

All three documents should be consulted
before attempting to make use of this document.

Definitions of some central terms are copied and discussed in subsections.

{::comment}
    [Good idea for 08, but needs more work. Ask BMWG?]

    Alternatively, quick list of all (existing and new here) terms,
    with links (external or internal respectively) to definitions.

    <mark>MKP3 [VP] TODO: Even if the following list will not be in final draft,
    it is useful to keep it around (maybe commented-out) while editing.</mark>

    <mark>MKP3 VP note: rough list of all RFC references:
    - [RFC1242] (section 3.17 Throughput) ... definition
    - [RFC2544] (section 26.1 Throughput) ... methodology
    - [RFC2544] (section 24. Trial duration):
     - full trial durations (implies short trials)
     - Also 60s for unconditional compliance is here.
     - Also "the search" (without quotes) appears there.
     - Also "binary search" (with quotes) appears there.
    - [RFC2544] (section 26.3 Frame loss rate):
     - two successive zero-loss trials are recommended (hints about loss inversion)
    - un/conditionally compliant with [RFC2544]
    - [RFC2544] (section 26. Benchmarking tests:)
     - all its "dot sections" have "Reporting format:" paragraphs
      - (implies test report)
     - [RFC2544] (section 26.1 Throughput) wants graph, frame size on X axis.
    - [RFC2544] (section 23. Trial description) trial
     - general description of trial
     - wait times specifically, maybe also learning frames?
    - Constant Load of [RFC1242] (section 3.4 Constant Load)
    - Data Rate of [RFC2544] (section 14. Bidirectional traffic)
     - seems equal to input frame rate [RFC2544] (23. Trial description).
    - [RFC2544] (section 21. Bursty traffic) suggests non-constant loads?
    - Intended Load of [RFC2285] (section 3.5.1 Intended load (Iload))
    - [RFC2285] (Section 3.5.2 Offered load (Oload))
    - Frame Loss Rate of [RFC1242] (section 3.6 Frame Loss Rate)
    - Forwarding Rate as defined in [RFC2285] (section 3.6.1 Forwarding rate (FR))
    - [RFC2544] (section 20. Maximum frame rate)
    - [RFC2285] (3.5.3 Maximum offered load (MOL))
    - reordered frames [RFC2544] (section 10. Verifying received frames)
    - For example, [RFC2544] (Appendix C) lists frame formats and protocol addresses,
      as recommended from [RFC2544] (section 8. Frame formats)
      and [RFC2544] (section 12. Protocol addresses).
    - [RFC8219] (section 5.3. Traffic Setup) introduces traffic setups consisting of a mix of IPv4 and IPv6 traffic
    - [RFC2544] (section 9. Frame sizes)
    - [RFC1242] (section 3.5 Data link frame size)
    - [RFC2285] (section 3.6.2) FRMOL
    - [RFC2285] (section 3.1.1) DUT
    - [RFC2285] (section 3.1.2) SUT
    - [RFC2544] (section 6. Test set up) test setup with (an external) tester
    - [RFC9004] B2B
    - [RFC8219] (section 5.3. Traffic Setup) for an example of ip4+ip6 mixed traffic
    </mark>

    <mark>MKP3 [VP] TODO: Do not mention those that do not need discussion here.</mark>

{:/comment}


{::comment}
    [Low priority]

    <mark>MKP3 [VP] TODO: Do we even need RFC9004?</mark>

{:/comment}

{::comment}
    [I do not understand what I meant. Typos? Probably not important overall.]

    <mark>MKP2 [VP] TODO: Even terms that are discussed in this memo,
    they perhaps do not need a separate list (just free paragraphs),
    in a chapter after MLRsearch specification.</mark>

{:/comment}

{::comment}
    [Important, just not enough time in 07.]

    <mark>MKP3 [VP] TODO: Verify that MLRsearch specification does not discuss
    meaning of existing terms without quoting their original definition.</mark>

{:/comment}

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
in MLRsearch specification, but is of key relevance for its motivation.

{::comment}
    [Could be useful, but not high priority.]

    ### Tester

    <mark>MKP3 TODO: Add Definition and Discusion paragraphs</mark>

    <mark>MKP3 MK note: Bizarre ... i can't find tester definition in
    rfc1242, rfc2288 or rfc2544, but will keep looking. If there isn't one,
    we need to define one :).</mark>

    <mark>[VP] TODO: There were some documents distinguishing TG and TA.</mark>

{:/comment}

### Trial

A trial is the part of the test described in [RFC2544] (section 23. Trial description).

Definition:

   A particular test consists of multiple trials.  Each trial returns
   one piece of information, for example the loss rate at a particular
   input frame rate.  Each trial consists of a number of phases:

   a) If the DUT is a router, send the routing update to the "input"
   port and pause two seconds to be sure that the routing has settled.

   b)  Send the "learning frames" to the "output" port and wait 2
   seconds to be sure that the learning has settled.  Bridge learning
   frames are frames with source addresses that are the same as the
   destination addresses used by the test frames.  Learning frames for
   other protocols are used to prime the address resolution tables in
   the DUT.  The formats of the learning frame that should be used are
   shown in the Test Frame Formats document.

   c) Run the test trial.

   d) Wait for two seconds for any residual frames to be received.

   e) Wait for at least five seconds for the DUT to restabilize.

Discussion:

The definition describes some traits, it is not clear whether all of them
are REQUIRED, or some of them are only RECOMMENDED.

{::comment}
    [Useful if possible.]

    <mark>MKP2 [VP] TODO: Search RFCs for better description of "Run the test trial".</mark>

{:/comment}

For the purposes of the MLRsearch specification,
it is ALLOWED for the test procedure to deviate from the [RFC2544] description,
but any such deviation MUST be made explicit in the test report.

Trials are the only stimuli the SUT is expected to experience
during the search.

In some discussion paragraphs, it is useful to consider the traffic
as sent and received by a tester, as implicitly defined
in [RFC2544] (section 6. Test set up).

An example of deviation from [RFC2544] is using shorter wait times.

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

The trial load is the intended load for a trial

Discussion:

For test report purposes, it is assumed that this is a constant load by default.
This MAY be only an average load, e.g. when the traffic is intended to be busty,
e.g. as suggested in [RFC2544] (section 21. Bursty traffic),
but the test report MUST explicitly mention how non-constant the traffic is.

Trial load is the quantity defined as Constant Load of [RFC1242]
(section 3.4 Constant Load), Data Rate of [RFC2544]
(section 14. Bidirectional traffic)
and Intended Load of [RFC2285] (section 3.5.1 Intended load (Iload)).
All three definitions specify
that this value applies to one (input or output) interface.

{::comment}
    [Not important.]

    <mark>MKP2 [VP] TODO: Also mention input frame rate [RFC2544] (23. Trial description).</mark>

{:/comment}

For test report purposes, multi-interface aggregate load MAY be reported,
this is understood as the same quantity expressed using different units.
From the report it MUST be clear whether a particular trial load value
is per one interface, or an aggregate over all interfaces.

Similarly to trial duration, some Measurers may limit the possible values
of trial load. Contrary to trial duration, the test report is NOT REQUIRED
to document such behavior.

{::comment}
    [Can of worms. Be aware, but probably do not let spill into draft.]

    <mark>MKP2 [VP] TODO: Why? In practice the difference is small, but what if it is big?
    Do we need Trial Effective Load for bounds an conditional throughput purposes?
    Should the Controller be recommended to chose load values that are exactly accepted?
    </mark>

{:/comment}

It is ALLOWED to combine trial load and trial duration in a way
that would not be possible to achieve using any integer number of data frames.

{::comment}
    [I feel this is important, to be discussed separately (not in-scope).]

    <mark>MKP2 [VP] TODO: Explain why are we not using Oload.
    1. MLRsearch implementations cannot react correctly to big differences
    between Iload and Oload.
    2. The media between the tested and the DUT are thus considered to be part of SUT.
    If DUT causes congestion control, it is not expected to handle Iload.
    </mark>

    See further discussion in [Trial Forwarding Ratio] (#Trial-Forwarding-Ratio)
    and in [Measurer] (#Measurer) sections for other related issues.

    <mark>MKP2 [VP] TODO: Create a separate subsection for Oload discussion,
    or clearly separate which aspects are discussed under which term.</mark>

    <mark>MKP2 [VP] TODO: New idea. Compare the tester to an ordinary router
    in some datacenter. The Intended Load is not jst some abstract input.
    It is the real traffic coming from routers next hop farther.
    It does not matter that DUT has forwarded each frame it received,
    if the tester was unable to sent all the traffic in time.
    Endpoint see packet loss, they do not care about [RFC2285]
    half-duplex, spanning trees, nor congestion control mechanisms.
    Formally speaking, I consider even the sending interface of the sender
    to be the part of SUT.
    Reading [RFC2285] (section 3.5.3 Maximum offered load (MOL))
    "This will be the case  when an external source lacks the resources
    to transmit frames at the minimum legal inter-frame gap"
    that means TRex workers are also part of SUT. If they do not have
    enough CPU power to generate frames are required, those frames are lost.
    </mark>

    <mark>MKP2 [VP] TODO: That new idea warants some discussion in "DUT within SUT",
    as it is just another case of ther rest of SUT ruining
    otherwise good DUT performance.</mark>

{:/comment}

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

### Traffic Profile

Definition:

Traffic profile is a composite quantity
containing attributes other than trial load and trial duration,
needed for unique determination of the trial to be performed.

Discussion:

All its attributes are assumed to be constant during the search,
and the composite is configured on the Measurer by the Manager
before the search starts.
This is why the traffic profile is not part of the Trial Input.

As a consequence, implementations of the Manager and the Measurer
must be aware of their common set of capabilities, so that the traffic profile
uniquely defines the traffic during the search.
The important fact is that none of those capabilities
have to be known by the Controller implementations.

The traffic profile SHOULD contain some specific quantities,
for example [RFC2544] (section 9. Frame sizes) governs
data link frame size as defined in [RFC1242] (section 3.5 Data link frame size).

Several more specific quantities may be RECOMMENDED, depending on media type.
For example, [RFC2544] (Appendix C) lists frame formats and protocol addresses,
as recommended from [RFC2544] (section 8. Frame formats)
and [RFC2544] (section 12. Protocol addresses).

Depending on SUT configuration, e.g. when testing specific protocols,
additional attributes MUST be included in the traffic profile
and in the test report.

Example: [RFC8219] (section 5.3. Traffic Setup) introduces traffic setups
consisting of a mix of IPv4 and IPv6 traffic - the implied traffic profile
therefore must include an attribute for their percentage.

Other traffic properties that need to be somehow specified
in Traffic Profile include:
[RFC2544] (section 14. Bidirectional traffic),
[RFC2285] (section 3.3.3 Fully meshed traffic),
and [RFC2544] (section 11. Modifiers).

### Trial Forwarding Ratio

Definition:

The trial forwarding ratio is a dimensionless floating point value.
It MUST range between 0.0 and 1.0, both inclusive.
It is calculated by dividing the number of frames
successfully forwarded by the SUT
by the total number of frames expected to be forwarded during the trial

Discussion:

For most traffic profiles, "expected to be forwarded" means
"intended to get transmitted from Tester towards SUT".

Trial forwarding ratio MAY be expressed in other units
(e.g. as a percentage) in the test report.

Note that, contrary to loads, frame counts used to compute
trial forwarding ratio are aggregates over all SUT output interfaces.

Questions around what is the correct number of frames
that should have been forwarded
is generally outside of the scope of this document.

{::comment}
    [Part two of iload/oload discussion.]

    See discussion in [Measurer] (#Measurer) section
    for more details about calibrating test equipment.

    <mark>MKP2 [VP] TODO: Define unsent frames?</mark>

    <mark>MKP2 [VP] TODO: If Oload is fairly below Iload, the unsent frames
    should be counted as lost, otherwise search outputs are misleading.
    But what is "fairly"? CSIT tolerates 10 microseconds worth of unsent frames.</mark>

{:/comment}

{::comment}
    [Low priority, but maybe useful for somebody?]

    <mark>MKP2 [VP] TODO: Mention traffic profiles with uneven frame counts?
    E.g. when SUT is expected to perform IP packet fragmentation or reassembly.
    </mark>

{:/comment}

### Trial Loss Ratio

Definition:

The Trial Loss Ratio is equal to one minus the trial forwarding ratio.

Discussion:

100% minus the trial forwarding ratio, when expressed as a percentage.

This is almost identical to Frame Loss Rate of [RFC1242]
(section 3.6 Frame Loss Rate),
the only minor difference is that Trial Loss Ratio
does not need to be expressed as a percentage.

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

{::comment}
    [Part 3 of iload/oload discussion.]

    <mark>MKP2 [VP] TODO: If some unsent frames were tolerated (not counted as lost),
    this value is actually higher than the real fps output of the SUT.
    Should we use the real FR as the basis for Conditional Throughput
    (instead of this TFR)? That would require additional Trial Output attribute.
    </mark>

    <mark>MKP2 [VP] TODO: What about duration stretching?
    This also causes difference between Iload and Oload,
    but in an invisible way.</mark>

    <mark>MKP2 [VP] TODO: Recommend start+sleep+stop?
    How long wait for late frames? RFC2544 2s is too much even at 30s trial.</mark>

{:/comment}

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
Simply measure the duration of the whole trial (waits including)
and use that as the trial effective duration.

Also, this is a way for the Measurer to inform the Controller about
its surprising behavior, for example when rounding the trial duration value.

{::comment}
    [Not very important, but easy and nice recommendation.]

    <mark>MKP2 [VP] TODO: Recommend for Measurer to return all trials at relevant bounds,
    as that may better inform users when surprisingly small amount of trials
    was performed, just because the the trial effective duration values were big.</mark>

    <mark>MKP2 [VP] TODO: Repeat that this is not here to deal with duration stretching.</mark>

{:/comment}

### Trial Output

Definition:

Trial Output is a composite quantity. The REQUIRED attributes are
Trial Loss Ratio, trial effective duration and trial forwarding rate.

Discussion:

When talking about multiple trials, it is common to say "Trial Outputs"
to denote all corresponding Trial Output instances.

Implementations may provide additional (optional) attributes.
The Controller implementations MUST ignore values of any optional attribute
they are not familiar with,
except when passing Trial Output instance to the Manager.

Example of an optional attribute:
The aggregate number of frames expected to be forwarded during the trial,
especially if it is not just (a rounded-up value)
implied by trial load and trial duration.

While [RFC2285] (Section 3.5.2 Offered load (Oload))
requires the offered load value to be reported for forwarding rate measurements,
it is NOT REQUIRED in MLRsearch specification.

{::comment}
    [Side tangent from iload/oload discussion. Stilll recommendation is not obvious.]

    <mark>MKP2 TODO: Why? Just because bound trial results are optional in Controller Output?</mark>

    <mark>MKP2 mk edit note: we need to more explicitly address
    the relevance or irrelevance of [RFC2285] (Section 3.5.2 Offered load (Oload)).
    Current text in [Trial Load] (#Trial-Load) is ambiguous - quoted below.</mark>

    <mark>MKP2 "Questions around what is the correct number of frames that should
    have been forwarded is generally outside of the scope of this document.
    See discussion in [Measurer] (#Measurer) section for more details about
    calibrating test equipment."</mark>

{:/comment}

### Trial Result

Definition:

Trial result is a composite quantity,
consisting of the Trial Input and the Trial Output.

Discussion:

When talking about multiple trials, it is common to say "trial results"
to denote all corresponding trial result instances.

While implementations SHOULD NOT include additional attributes
with independent values, they MAY include derived quantities.

## Goal Terms

This section defines new and redefine existing terms for quantities
indirectly relevant for inputs or outputs of the Controller component.

Several goal attributes are defined before introducing
the main component quantity: the Search Goal.

### Goal Final Trial Duration

Definition:

A threshold value for trial durations.

Discussion:

This attribute value MUST be positive.

A trial with Trial Duration at least as long as the Goal Final Trial Duration
is called a full-length trial (with respect to the given Search Goal).

A trial that is not full-length is called a short trial.

Informally, while MLRsearch is allowed to perform short trials,
the results from such short trials have only limited impact on search results.

One trial may be full-length for some Search Goals, but not for others.

The full relation of this goal to Controller Output is defined later in
this document in subsections of [Goal Result] (#Goal-Result).
For example, the Conditional Throughput for this goal is computed only from
full-length trial results.

### Goal Duration Sum

Definition:

A threshold value for a particular sum of trial effective durations.

Discussion:

This attribute value MUST be positive.

Informally, even when looking only at full-length trials,
MLRsearch may spend up to this time measuring the same load value.

If the Goal Duration Sum is larger than the Goal Final Trial Duration,
multiple full-length trials may need to be performed at the same load.

See [TST009 Example] (#TST009-Example) for an example where possibility
of multiple full-length trials at the same load is intended.

A Goal Duration Sum value lower than the Goal Final Trial Duration
(of the same goal) could save some search time, but is NOT RECOMMENDED.
See [Relevant Upper Bound] (#Relevant-Upper-Bound) for partial explanation.

### Goal Loss Ratio

Definition:

A threshold value for Trial Loss Ratios.

Discussion:

Attribute value MUST be non-negative and smaller than one.

A trial with Trial Loss Ratio larger than a Goal Loss Ratio value
is called a lossy trial, with respect to given Search Goal.

Informally, if a load causes too many lossy trials,
the Relevant Lower Bound for this goal will be smaller than that load.

If a trial is not lossy, it is called a low-loss trial,
or (specifically for zero Goal Loss Ratio value) zero-loss trial.

### Goal Exceed Ratio

Definition:

A threshold value for a particular ratio of sums of Trial Effective Durations.

Discussion:

Attribute value MUST be non-negative and smaller than one.

See later sections for details on which sums.
Specifically, the direct usage is only in
[Appendix A: Load Classification] (#Appendix-A\:-Load-Classification)
and [Appendix B: Conditional Throughput] (#Appendix-B\:-Conditional-Throughput).
The impact of that usage is discussed in subsections leading to
[Goal Result] (#Goal-Result).

Informally, the impact of lossy trials is controlled by this value.
Effectively, Goal Exceed Ratio is a percentage of full-length trials
that may be lossy without the load being classified
as the [Relevant Upper Bound] (#Relevant-Upper-Bound).

### Goal Width

Definition:

A value used as a threshold for deciding
whether two trial load values are close enough.

Discussion:

If present, the value MUST be positive.

Informally, this acts as a stopping condition,
controlling the precision of the search.
The search stops if every goal has reached its precision.

Implementations without this attribute
MUST give the Controller other ways to control the search stopping conditions.

Absolute load difference and relative load difference are two popular choices,
but implementations may choose a different way to specify width.

The test report MUST make it clear what specific quantity is used as Goal Width.

It is RECOMMENDED to set the Goal Width (as relative difference) value
to a value no smaller than the Goal Loss Ratio.
(The reason is not obvious, see [Throughput] (#Throughput) if interested.)

### Search Goal

Definition:

The Search Goal is a composite quantity consisting of several attributes,
some of them are required.

Required attributes:
- Goal Final Trial Duration
- Goal Duration Sum
- Goal Loss Ratio
- Goal Exceed Ratio

Optional attribute:
- Goal Width

Discussion:

Implementations MAY add their own attributes.
Those additional attributes may be required by the implementation
even if they are not required by MLRsearch specification.
But it is RECOMMENDED for those implementations
to support missing values by computing reasonable defaults.

The meaning of listed attributes is formally given only by their indirect effect
on the search results.

Informally, later sections provide additional intuitions and examples
of the Search Goal attribute values.

An example of additional attributes required by some implementations
is Goal Initial Trial Duration, together with another attribute
that controls possible intermediate Trial Duration values.
The reasonable default in this case is using the Goal Final Trial Duration
and no intermediate values.

### Controller Input

Definition:

Controller Input is a composite quantity
required as an input for the Controller.
The only REQUIRED attribute is a list of Search Goal instances.

Discussion:

MLRsearch implementations MAY use additional attributes.
Those additional attributes may be required by the implementation
even if they are not required by MLRsearch specification.

Formally, the Manager does not apply any Controller configuration
apart from one Controller Input instance.

For example, Traffic Profile is configured on the Measurer by the Manager
(without explicit assistance of the Controller).

The order of Search Goal instances in a list SHOULD NOT
have a big impact on Controller Output (see section [Controller Output] (#Controller-Output) ,
but MLRsearch implementations MAY base their behavior on the order
of Search Goal instances in a list.

An example of an optional attribute (outside the list of Search Goals)
required by some implementations is Max Load.
While this is a frequently used configuration parameter,
already governed by [RFC2544] (section 20. Maximum frame rate)
and [RFC2285] (3.5.3 Maximum offered load (MOL)),
some implementations may detect or discover it instead.

{::comment}
    [Not important directly, may matter for iload/oload.]

    <mark>MKP2 [VP] TODO: 2544 and 2285 care about half-duplex media. Should we?</mark>

{:/comment}

{::comment}
    [Maybe obvious but I think useful. RFC2544 talks about header compression in WANs.]

    <mark>MKP2 [VP] TODO: Mention that Max Load should care about all media within SUT,
    including DUT-DUT links. Important when that link carries encapsulated traffic,
    as bandwidth limit there implies lower max rate
    (than implied by tester-SUT links).</mark>

{:/comment}

In MLRsearch specification, the [Relevant Upper Bound] (#Relevant-Upper-Bound)
is added as a required attribute precisely because it makes the search result
independent of Max Load value.

{::comment}
    [User recommendation, we should have separate section summarizing those.]

    <mark>[VP] TODO for MK: The rest of this subsection is new, review?</mark>

    It is RECOMMENDED to use the same Goal Final Trial Duration value across all goals.
    Otherwise, some goals may be measured at Trial Durations longer than needed,
    with possibly unexpected impacts on repeatability and comparability.

    For example when Goal Loss Ratio is zero, any increase in Trial Duration
    also increases the likelihood of the trial to become lossy,
    similar to usage of lower Goal Exceed Ratio or larger Goal Duration Sum,
    both of which tend to lower the search results, towards noisy end
    of performance spectrum.

    Also, it is recommended to avoid "incomparable" goals, e.g. one with
    lower loss ratio but higher exceed ratio, and other with higher loss ratio
    but lower loss ratio. In worst case, this can make the search to last too long.
    Implementations are RECOMMENDED to sort the goals and start with
    stricter ones first, as bounds for those will not get invalidated
    byt measureing for less trict goal later in the search.

{:/comment}

## Search Goal Examples

### RFC2544 Goal

The following set of values makes the search result unconditionally compliant
with [RFC2544] (section 24 Trial duration)

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 60 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 0%

The latter two attributes are enough to make the search goal
conditionally compliant, adding the first attribute
makes it unconditionally compliant.

The second attribute (Goal Duration Sum) only prevents MLRsearch
from repeating zero-loss full-length trials.

Non-zero exceed ratio could prolong the search and allow loss inversion
between lower-load lossy short trial and higher-load full-length zero-loss trial.
From [RFC2544] alone, it is not clear whether that higher load
could be considered as compliant throughput.

### TST009 Goal

One of the alternatives to RFC2544 is described in
[TST009] (section 12.3.3 Binary search with loss verification).
The idea there is to repeat lossy trials, hoping for zero loss on second try,
so the results are closer to the noiseless end of performance sprectum,
and more repeatable and comparable.

Only the variant with "z = infinity" is achievable with MLRsearch.

{::comment}
    [Low priority, unless a short sentence is found.]

    <mark>MKP2 MK note: Shouldn't we add a note about how MLRsearch goes about
    addressing the TST009 point related to z, that is "z is threshold of
    Lord(r) to override Loss Verification when the count of lost frames is
    very high and unnecessary verification trials."? i.e. by have Goal Loss
    Ratio. Thoughts?</mark>

{:/comment}

For example, for "r = 2" variant, the following search goal should be used:

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 120 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 50%

If the first 60s trial has zero loss, it is enough for MLRsearch to stop
measuring at that load, as even a second lossy trial
would still fit within the exceed ratio.

But if the first trial is lossy, MLRsearch needs to perform also
the second trial to classify that load.
As Goal Duration Sum is twice as long as Goal Final Trial Duration,
third full-length trial is never needed.

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

Before defining real attributes of the goal result,
it is useful to define bounds in general.

### Relevant Upper Bound

Definition:

The Relevant Upper Bound is the smallest trial load value that is classified
at the end of the search as an upper bound
(see [Appendix A: Load Classification] (#Appendix-A\:-Load-Classification))
for the given Search Goal.

Discussion:

One search goal can have many different load classified as an upper bound.
At the end of the search, one of those loads will be the smallest,
becoming the relevant upper bound for that goal.

In more detail, the set of all trial outputs (both short and full-length,
enough of them according to Goal Duration Sum)
performed at that smallest load failed to uphold all the requirements
of the given Search Goal, mainly the Goal Loss Ratio
in combination with the Goal Exceed Ratio.

{::comment}
    [Recheck. Move to end?]

    <mark>[VP] TODO: Is the above a good summary of Appendix A inputs?</mark>

{:/comment}

If Max Load does not cause enough lossy trials,
the Relevant Upper Bound does not exist.
Conversely, if Relevant Upper Bound exists,
it is not affected by Max Load value.

{::comment}
    [Medium priority, depends on how many user recommendations we have.]

    With non-zero exceed ratio values, a lossy short trial may not be enough
    to classify a load as the relevant upper bound.
    Users MAY apply Goal Duration Sum value lower than Goal Final Trial Duration
    to force such classification in hope to save time,
    but it is RECOMMENDED not to do so, as in practice
    it hurts comparability and repeatability.

{:/comment}

{::comment}
    [Probably too technical, unless relation to repeatability is found.]

    In general, a load starts as as undecided, then maybe flips to become
    an upper bound. MLRsearch stops measuring at that load for this goal,
    but it may be forced to measure more for some other search goals,
    in which case the load may flip to a lower bound (and back and forth).

    <mark>[VP] TODO: Confirm the load can never flip back to being undecided.</mark>

    Even though the load classification may change during the search,
    the goal results are established at the end of the search.

    If the exceed ratio is zero, an upper bound can never flip;
    one lossy trial (even short) is enough to pin the classification.

{:/comment}

### Relevant Lower Bound

Definition:

The Relevant Lower Bound is the largest trial load value
among those smaller than the Relevant Upper Bound,
that got classified at the end of the search as a lower bound (see
[Appendix A: Load Classification] (#Appendix-A\:-Load-Classification))
for the given Search Goal.

Discussion:

Only among loads smaller that the relevant upper bound,
the largest load becomes the relevant lower bound.
With loss inversion, stricter upper bound matters.

In more detail, the set of all trial outputs (both short and full-length,
enough of them according to Goal Duration Sum)
performed at that largest load managed to uphold all the requirements
of the given Search Goal, mainly the Goal Loss Ratio
in combination with the Goal Exceed Ratio.

Is no load had enough low-loss trials, the relevant lower bound
MAY not exist.

{::comment}
    [Min Load us useful for detecting broken SUTs (and latency).]

    <mark>[VP] TODO: Mention min load here?</mark>

    <mark>[VP] TODO: Allow zero as implicit lower bound that needs no trials?
    If yes, then probably way earlier than here.</mark>

{:/comment}

Strictly speaking, if the Relevant Upper Bound does not exist,
the Relevant Lower Bound also does not exist.
In that case, Max Load is classified as a lower bound,
but it is not clear whether a higher lower bound
would be found if the search used a higher Max Load value.

For a regular Goal Result, the distance between the Relevant Lower Bound
and the Relevant Upper Bound MUST NOT be larger than the Goal Width,
if the implementation offers width as a goal attribute.

{::comment}
    [True but no time to fix properly.]

    <mark>mk note: Seemingly broken grammar,
    "managed to uphold all requirements", should be followed
    by stating what it means.</mark>

{:/comment}

Searching for anther search goal may cause a loss inversion phenomenon,
where a lower load is classified as an upper bound,
but also a higher load is classified as a lower bound for the same search goal.
The definition of the Relevant Lower Bound ignores such high lower bounds.

{::comment}
    [Compare to similar block in upper bound.]

    In general, a load starts as as undecided, then maybe flips to become
    a lower bound. MLRsearch stops measuring at that load for this goal,
    but it may be forced to measure more for some other search goals,
    in which case the load may flip to an upper bound (and back and forth).

    <mark>[VP] TODO: Confirm the load can never flip back to being undecided.</mark>

    Even though the load classification may change during the search,
    the goal results are established at the end of the search.

    No valid exceed ratio value pins the classification as a lower bound.

{:/comment}

### Conditional Throughput

Definition:

The Conditional Throughput (see section [Appendix B: Conditional Throughput] (#Appendix-B\:-Conditional-Throughput))
as evaluated at the Relevant Lower Bound of the given Search Goal
at the end of the search.

Discussion:

Informally, this is a typical trial forwarding rate, expected to be seen
at the Relevant Lower Bound of the given Search Goal.

But frequently it is only a conservative estimate thereof,
as MLRsearch implementations tend to stop gathering more data
as soon as they confirm the value cannot get worse than this estimate
within the Goal Duration Sum.

This value is RECOMMENDED to be used when evaluating repeatability
and comparability if different MLRsearch implementations.

{::comment}
    [Low priority but useful for comparabuility.]

    <mark>[VP] TODO: Add subsection for Trial Results At Relevant Bounds
    as an optional attribute of Goal Result.</mark>

{:/comment}

### Goal Result

Definition:

The Goal Result is a composite quantity consisting of several attributes.
Relevant Upper Bound and Relevant Lower Bound are REQUIRED attributes,
Conditional Throughput is a RECOMMENDED attribute.

Discussion:

Depending on SUT behavior, it is possible that one or both relevant bounds
do not exist. The goal result instance where the required attribute values exist
is informally called a Regular Goal Result instance,
so we can say some goals reached Irregular Goal Results.

{::comment}
    [Probably delete after last edits re irregular results.]

    <mark>MKP2 [VP] TODO: Additional attributes should not be required by the Manager?
    Explicitly mention that irregular goal result may support different attributes.
    </mark>

    <mark>MKP2 Implementations are free to define their own specific subtypes
    of irregular Goal Results, but the test report MUST mark them clearly
    as irregular according to this section.</mark>

{:/comment}

A typical Irregular Goal Result is when all trials at the Max Load
have zero loss, as the Relevant Upper Bound does not exist in that case.

It is RECOMMENDED that the test report will display such results appropriately,
although MLRsearch specification does not prescibe how.

{::comment}
    [Useful.]

    <mark>MKP2 [VP] TODO: Also allways-fail. Link to bounds to avoid duplication.</mark>

{:/comment}

Anything else regarging Irregular Goal Results,
including their role in stopping conditions of the search
is outside the scope of this document.

### Search Result

Definition:

The Search Result is a single composite object
that maps each Search Goal instance to a corresponding Goal Result instance.

Discussion:

Alternatively, the Search Result can be implemented as an ordered list
of the Goal Result instances, matching the order of Search Goal instances.

{::comment}
    [Low priority, as there is no obvious harm.]

    <mark>MKP1 [VP] TODO: Disallow any additional attributes?</mark>

{:/comment}

The Search Result (as a mapping)
MUST map from all the Search Goal instances present in the Controller Input.

{::comment}
    [Not important.]

    <mark>[VP] Postponed: API independence, modularity.</mark>

{:/comment}

{::comment}
    [Not needed?]

    <mark>MKP1 [VP] TODO: Short sentence on what to do on irregular goal result.</mark>

{:/comment}

### Controller Output

Definition:

The Controller Output is a composite quantity returned from the Controller
to the Manager at the end of the search.
The Search Result instance is its only REQUIRED attribute.

Discussion:

MLRsearch implementation MAY return additional data in the Controller Output.

{::comment}
    [Not needed?]

    <mark>MKP1 [VP] TODO: Short sentence on what to do on irregular goal result.</mark>

    <mark>MKP1 [VP] TODO: Irregular output, e.g. with "max search time exceeded" flag?</mark>

{:/comment}

## MLRsearch Architecture

{::comment}
    [Meta and irrelevant. Delete after verifying other text is good.]

    <mark>MKP2 [VP] TODO: Review the folowing:
    This section is about division into components,
    so it fits this definition:
    "The software architecture of a system represents the design decisions
    related to overall system structure and behavior."
    Saying "MLRsearch Design" does not make it clear if it is
    Vratko designing the MLRsearch specification,
    or some other person designing a new MLRsearch implementation using that spec.
    </mark>

{:/comment}

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
that when called with a [Trial Input] (#Trial-Input) instance,
performs one [Trial] (#Trial),
and returns a [Trial Output] (#Trial-Output) instance.

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
from the intended load, and use that value as the Max Load value.
When testing the real SUT, it is RECOMMENDED to turn any big difference
between the intended load and the offered load into increased Trial Loss Ratio.

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

Informally, the Controller has big freedom in selection of Trial Inputs,
and the implementations want to achieve the Search Goals
in the shortest expected time.

The Controller's role in optimizing the overall search time
distinguishes MLRsearch algorithms from simpler search procedures.

Informally, each implementation can have different stopping conditions.
Goal Width is only one example.
In practice, implementation details do not matter,
as long as Goal Results are regular.

### Manager

Definition:

The Manager is an abstract system component that is reponsible for
configuring other components, calling the Controller component once,
and for creating the test report following the reporting format as
defined in [RFC2544] (section 26. Benchmarking tests).

Discussion:

The Manager initializes the SUT, the Measurer (and the Tester if independent)
with their intended configurations before calling the Controller.

The Manager does not need to be able to tweak any Search Goal attributes,
but it MUST report all applied attribute values even if not tweaked.

{::comment}
    [Not very important but also should be easy to add.]

    <mark>MKP2 [VP] TODO: Is saying "RFC2544" indirectly reporting RFC2544 Goal values?</mark>

{:/comment}

In principle, there should be a "user" (human or CI)
that "starts" or "calls" the Manager and receives the report.
The Manager MAY be able to be called more than once whis way.

{::comment}
    [Not important, unless anybody else asks.]

    <mark>MKP2 The Manager may use the Measurer or other system components
    to perform other tests, e.g. back-to-back frames,
    as the Controller is only replacing the search from
    [RFC2544] (section 26.1 Throughput).</mark>

{:/comment}

## Implementation Compliance

Any networking measurement setup where there can be logically delineated system components
and there are components satisfying requirements for the Measurer,
the Controller and the Manager, is considered to be compliant with MLRsearch design.

These components can be seen as abstractions present in any testing procedure.
For example, there can be a single component acting both
as the Manager and the Controller, but as long as values of required attributes
of Search Goals and Goal Results are visible in the test report,
the Controller Input instance and output instance are implied.

For example, any setup for conditionally (or unconditionally)
compliant [RFC2544] throughput testing
can be understood as a MLRsearch architecture,
assuming there is enough data to reconstruct the Relevant Upper Bound.

See [RFC2544 Goal] (#RFC2544-Goal) subsection for equivalent Search Goal.

Any test procedure that can be understood as (one call to the Manager of)
MLRsearch architecture is said to be compliant with MLRsearch specification.

# Additional Considerations

This section focuses on additional considerations, intuitions and motivations
pertaining to MLRsearch methodology.

{::comment}
    [Meta, redundant.]

    <mark>MKP2 [VP] TODO: Review the following:
    If MLRsearch specification is a product design specification
    for MLRsearch implementation, then this chapter talks about
    my goals and early attempts at designing the MLRsearch specification.
    </mark>

{:/comment}

## MLRsearch Versions

The MLRsearch algorithm has been developed in a code-first approach,
a Python library has been created, debugged, used in production
and published in PyPI before the first descriptions
(even informal) were published.

But the code (and hence the description) was evolving over time.
Multiple versions of the library were used over past several years,
and later code was usually not compatible with earlier descriptions.

The code in (some version of) MLRsearch library fully determines
the search process (for a given set of configuration parameters),
leaving no space for deviations.

{::comment}
    [Different type of external link, should be in 08.]

    <mark>MKP2 mk3 note: any references to library
    should have specific reference link.
    We have FDio-CSIT-MLRsearch in informative: at the start. Link it.
    </mark>

{:/comment}

{::comment}
    [Lesson learned is important, but maybe does not need version history?]

    <mark>MKP2 mk edit note: Suggest to remove crossed-out text, as it is
    distracting, doesn't bring any value, and recalls multiple versions of
    MLRsearch library, without any references. A much more appropriate
    approach would be to provide a pointer to MLRsearch code versions in
    FD.io that evolved over the years, as an example implementation. But I
    would question the value of referring to old previous versions in this
    document. It's okay for the blog, but not for IETF specification,
    unless there are specific lessons learned that need to be highlighted
    to support the specification.</mark>

{:/comment}

This historic meaning of MLRsearch, as a family
of search algorithm implementations,
leaves plenty of space for future improvements, at the cost
of poor comparability of results of search algoritm implementations.

{::comment}
    [Reckeck after clarifying library/algorithm/implementation/specification mess.]

    <mark>mk edit note: If the aim of this sentence is to state that there
    could be possibly other approaches to address this problem space, then
    I think we are already addressing it in the opening sections discussing
    problems, and referring to ETSi TST.009 and opnfv work. If the aim is
    to define "MLRsearch" as a completely new class of algorithms for
    software network benchmarking, of which this spec is just one example,
    then i have a problem with it. This specification is very prescriptive
    in the main functional areas to address the problem identified, but
    still leaving space for further exploration and innovation as noted
    elsewhere in this document. It is not a new class of algorithms. It is
    a newly defined methodology to amend RFC2544, to specifically address
    identified problems.</mark>

{:/comment}

There are two competing needs.
There is the need for standardization in areas critical to comparability.
There is also the need to allow flexibility for implementations
to innovate and improve in other areas.
This document defines MLRsearch as a new specification
in a manner that aims to fairly balance both needs.

## Stopping Conditions

[RFC2544] prescribes that after performing one trial at a specific offered load,
the next offered load should be larger or smaller, based on frame loss.

The usual implementation uses binary search.
Here a lossy trial becomes
a new upper bound, a lossless trial becomes a new lower bound.
The span of values between the tightest lower bound
and the tightest upper bound (including both values) forms an interval of possible results,
and after each trial the width of that interval halves.

Usually the binary search implementation tracks only the two tightest bounds,
simply calling them bounds.
But the old values still remain valid bounds,
just not as tight as the new ones.

After some number of trials, the tightest lower bound becomes the throughput.
[RFC2544] does not specify when, if ever, should the search stop.

MLRsearch introduces a concept of [Goal Width] (#Goal-Width).

The search stops
when the distance between the tightest upper bound and the tightest lower bound
is smaller than a user-configured value, called Goal Width from now on.
In other words, the interval width at the end of the search
has to be no larger than the Goal Width.

This Goal Width value therefore determines the precision of the result.
Due to the fact that MLRsearch specification requires a particular
structure of the result (see [Trial Result] (#Trial-Result) section),
the result itself does contain enough information to determine its
precision, thus it is not required to report the Goal Width value.

This allows MLRsearch implementations to use stopping conditions
different from Goal Width.

## Load Classification

MLRsearch keeps the basic logic of binary search (tracking tightest bounds,
measuring at the middle), perhaps with minor technical differences.

MLRsearch algorithm chooses an intended load (as opposed to the offered load),
the interval between bounds does not need to be split
exactly into two equal halves,
and the final reported structure specifies both bounds.

The biggest difference is that to classify a load
as an upper or lower bound, MLRsearch may need more than one trial
(depending on configuration options) to be performed at the same intended load.

In consequence, even if a load already does have few trial results,
it still may be classified as undecided, neither a lower bound nor an upper bound.

An explanation of the classification logic is given in the next section [Logic of Load Classification] (#Logic-of-Load-Classification),
as it heavily relies on other subsections of this section.

For repeatability and comparability reasons, it is important that
given a set of trial results, all implementations of MLRsearch
classify the load equivalently.

## Loss Ratios

Another difference between MLRsearch and [RFC2544] binary search is in the goals of the search.
[RFC2544] has a single goal,
based on classifying full-length trials as either lossless or lossy.

MLRsearch, as the name suggests, can search for multiple goals,
differing in their loss ratios.
The precise definition of the Goal Loss Ratio will be given later.
The [RFC2544] throughput goal then simply becomes a zero Goal Loss Ratio.
Different goals also may have different Goal Widths.

A set of trial results for one specific intended load value
can classify the load as an upper bound for some goals, but a lower bound
for some other goals, and undecided for the rest of the goals.

Therefore, the load classification depends not only on trial results,
but also on the goal.
The overall search procedure becomes more complicated, when
compared to binary search with a single goal,
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

This is formalized using new notions, the [Relevant Upper Bound] (#Relevant-Upper-Bound) and
the [Relevant Lower Bound] (#Relevant-Lower-Bound).
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
When they are less than the Goal Width apart,
the relevant bounds are used in the output.

One consequence is that every trial result can have an impact on the search result.
That means if your SUT (or your traffic generator) needs a warmup,
be sure to warm it up before starting the search.

## Exceed Ratio

The idea of performing multiple trials at the same load comes from
a model where some trial results (those with high loss) are affected
by infrequent effects, causing poor repeatability of [RFC2544] throughput results.
See the discussion about noiseful and noiseless ends
of the SUT performance spectrum in section [DUT in SUT] (#DUT-in-SUT).
Stable results are closer to the noiseless end of the SUT performance spectrum,
so MLRsearch may need to allow some frequency of high-loss trials
to ignore the rare but big effects near the noiseful end.

MLRsearch can do such trial result filtering, but it needs
a configuration option to tell it how frequent can the infrequent big loss be.
This option is called the exceed ratio.
It tells MLRsearch what ratio of trials
(more exactly what ratio of trial seconds) can have a [Trial Loss Ratio] (#Trial-Loss-Ratio)
larger than the Goal Loss Ratio and still be classified as a lower bound.
Zero exceed ratio means all trials have to have a Trial Loss Ratio
equal to or smaller than the Goal Loss Ratio.

For explainability reasons, the RECOMMENDED value for exceed ratio is 0.5,
as it simplifies some later concepts by relating them to the concept of median.

## Duration Sum

When more than one trial is intended to classify a load,
MLRsearch also needs something that controls the number of trials needed.
Therefore, each goal also has an attribute called duration sum.

The meaning of a [Goal Duration Sum] (#Goal-Duration-Sum) is that
when a load has (full-length) trials
whose trial durations when summed up give a value at least as big
as the Goal Duration Sum value,
the load is guaranteed to be classified either as an upper bound
or a lower bound for that goal.

Due to the fact that the duration sum has a big impact
on the overall search duration, and [RFC2544] prescribes
wait intervals around trial traffic,
the MLRsearch algorithm is allowed to sum durations that are different
from the actual trial traffic durations.

In the MLRsearch specification, the different duration values are called
[Trial Effective Duration] (#Trial-Effective-Duration).

## Short Trials

MLRsearch requires each goal to specify its final trial duration.
Full-length trial is a shorter name for a trial whose intended trial duration
is equal to (or longer than) the goal final trial duration.

Section 24 of [RFC2544] already anticipates possible time savings
when short trials (shorter than full-length trials) are used.
Full-length trials are the opposite of short trials,
so they may also be called long trials.

Any MLRsearch implementation may include its own configuration options
which control when and how MLRsearch chooses to use short trial durations.

For explainability reasons, when exceed ratio of 0.5 is used,
it is recommended for the Goal Duration Sum to be an odd multiple
of the full trial durations, so Conditional Throughput becomes identical to
a median of a particular set of trial forwarding rates.

The presence of short trial results complicates the load classification logic.

Full details are given later in section [Logic of Load Classification] (#Logic-of-Load-Classification).
In a nutshell, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the Relevant Lower Bound,
below what would classification say when considering full-length trials only.

{::comment}
    [I still think this is important, revisit after explanations re quantiles.]

    <mark>For explainability reasons, it is RECOMMENDED users use such configurations
    that guarantee all trials have the same length.</mark>

    <mark>mk edit note: Using RFC2119 keyword here does not seem to be
    appropriate. Moreover, I do not get the meaning nor the logic behind
    this statement. It seems to say that in order for users to understand
    the workings of MLRsearch, they should use simplified configuration,
    otherwise they won't get it. Illogical it seems to me. Suggest to
    remove it.</mark>

{:/comment}

{::comment}
    [Important. Keeping compatibility slows search considerably.]

    <mark>Alas, such configurations are usually not compliant with [RFC2544] requirements,
    or not time-saving enough.</mark>

    <mark>mk edit note: This statement does not make sense to me. Suggest to remove it.</mark>

{:/comment}

## Throughput

{::comment}
    [Important, we need better title.]

    <mark>[VP] TODO: Was named Conditional Troughput, but spec chapter already has one.</mark>

{:/comment}

Due to the fact that testing equipment takes the intended load as an input parameter
for a trial measurement, any load search algorithm needs to deal
with intended load values internally.

But in the presence of goals with a non-zero loss ratio, the intended load
usually does not match the user's intuition of what a throughput is.
The forwarding rate (as defined in [RFC2285] section 3.6.1) is better,
but it is not obvious how to generalize it
for loads with multiple trial results and a non-zero
[Goal Loss Ratio] (#Goal-Loss-Ratio).

The best example is also the main motivation: hard limit performance.
Even if the medium allows higher performance,
the SUT interfaces may have their additional own limitations,
e.g. a specific fps limit on the NIC (a very common occurance).

Ideally, those should be known and used when computing Max Load.
But if Max Load is higher that what interface can receive or transmit,
there will be a "hard limit" observed in trial results.
Imagine the hard limit is at 100 Mfps, Max Load is higher,
and the goal loss ratio is 0.5%. If DUT has no additional losses,
0.5% loss ratio will be achieved at 100.5025 Mfps (the relevant lower bound).
But it is not intuitive to report SUT performance as a value that is
larger than known hard limit.
We need a generalization of RFC2544 throughput,
different from just the relevant lower bound.

MLRsearch defines one such generalization, called the Conditional Throughput.
It is the trial forwarding rate from one of the trials
performed at the load in question.
Determining which trial exactly is defined in
[MLRsearch Specification] (#MLRsearch-Specification),
and in [Appendix B: Conditional Throughput] (#Appendix-B\:-Conditional-Throughput).

In the hard limit example, 100.5 Mfps load will still have
only 100.0 Mfps forwarding rate, nicely confirming the known limitation.

Conditional Throughput is partially related to load classification.
If a load is classified as a lower bound for a goal,
the Conditional Throughput can be calculated from trial results,
and guaranteed to show an loss ratio
no larger than the Goal Loss Ratio.

{::comment}
    [Revisit after other edits, may be addressed elsewhere.]

    <mark>While the Conditional Throughput gives more intuitive-looking
    values than the Relevant Lower Bound (for non-zero Goal Loss Ratio
    values), the actual definition is more complicated than the definition
    of the Relevant Lower Bound.</mark>

    <mark>mk edit note: Looking at this again, and per improved text, I
    don't think it is that complicated. (BTW saying it is more complicated
    and not addressing it, and leaving it open ended is not
    good.) "Conditional throughput" intuitively is really throughput under
    certain conditions, these being offered load determined by Relevant
    Lower Bound and actual loss. For comparability, and taking into account
    multiple trial samples, per MLRsearch definition, this is
    mathematically expressed as `conditional_throughput = intended_load *
    (1.0 - quantile_loss_ratio)`.</mark>

    <mark>DONE VP to MK: Hmm. Frequently, Conditional Throughput comes
    from the worst among low-loss full-length trials.
    But if two disparate goals are interested at the same load,
    things get complicated (does not happen in CSIT production,
    but I found few bugs when testing in simulator).
    Computation in load classification is also not trivial,
    but at least it only needs two "duration sum" values,
    no need to sort all trial results.</mark>

    <mark>MKP2 [VP] TODO: Still not sure what to do with this subsection.
    Possibly a bigger rewrite once VP and MK agree on what is (or is not)
    complicated. :)</mark>

{:/comment}

{::comment}
    [Important only for "design principles" chapter we may never have.]

    <mark>In the future, other intuitive values may become popular,
    but they are unlikely to supersede the definition of the Relevant Lower Bound
    as the most fitting value for comparability purposes,
    therefore the Relevant Lower Bound remains a required attribute
    of the Goal Result structure, while the Conditional Throughput is only optional.</mark>

    <mark>mk edit note: This paragraph adds to the confusion. I would remove
    this paragraph, as with the new text above it doesn't seem to add any
    value.</mark>

    <mark>[VP] TODO: This is an example of MLRsearch design principles.</mark>

{:/comment}

{::comment}
    [Useful.]

    <mark>[VP] TODO: Mention somewhere that trending is a specific case
    of repeatability/comparability.</mark>

{:/comment}

Note that when comparing the best (all zero loss) and worst case (all loss
just below Goal Loss Ratio), the same Relevant Lower Bound value
may result in the Conditional Throughput differing up to the Goal Loss Ratio.

Therefore it is rarely needed to set the Goal Width (if expressed
as the relative difference of loads) below the Goal Loss Ratio.
In other words, setting the Goal Width below the Goal Loss Ratio
may cause the Conditional Throughput for a larger loss ratio to become smaller
than a Conditional Throughput for a goal with a smaller Goal Loss Ratio,
which is counter-intuitive, considering they come from the same search.
Therefore it is RECOMMENDED to set the Goal Width to a value no smaller
than the Goal Loss Ratio.

Overall, this Conditional Throughput does behave well for comparability purposes.

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

{::comment}
    [Important for BMWG. Configurability is bad for comparability.]

    <mark>MKP2 Sadly, different implementations may exhibit their sweet spot of</mark>
    <mark>the best repeatability for a given search duration</mark>
    <mark>at different goals attribute values, especially concerning</mark>
    <mark>any optional goal attributes such as the initial trial duration.</mark>
    <mark>Thus, this document does not comment much on which configurations</mark>
    <mark>are good for comparability between different implementations.</mark>
    <mark>For comparability between different SUTs using the same implementation,</mark>
    <mark>refer to configurations recommended by that particular implementation.</mark>

    <mark>MKP2 mk edit note: Isn't this going off on a tangent, hypothesising and
    second guessing about different possible implementations. What is the
    value of this content to this document? Suggest to remove it.</mark>

{:/comment}

## [RFC2544] Compliance

Some Search Goal instances lead to results compliant with RFC2544.
See [RFC2544 Goal] (#RFC2544-Goal) for more details
regarding both conditional and unconditional compliance.

The presence of other Search Goals does not affect the compliance
of this Goal Result.
The Relevant Lower Bound and the Conditional Throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

# Logic of Load Classification

## Introductory Remarks

This chapter continues with explanations,
but this time more precise definitions are needed
for readers to follow the explanations.

Descriptions in this section are wordy and implementers should read
[MLRsearch Specification] (#MLRsearch-Specification) section
and Appendices for more concise definitions.

The two areas of focus here are load classification
and the Conditional Throughput.

To start with [Performance Spectrum] (#Performance-Spectrum)
subsection contains definitions needed to gain insight
into what Conditional Throughput means.
Remaining subsections discuss load classification.

For load classification, it is useful to define **good trials** and **bad trials**:

- **Bad trial**: Trial is called bad (according to a goal)
  if its [Trial Loss Ratio] (#Trial-Loss-Ratio)
  is larger than the [Goal Loss Ratio] (#Goal-Loss-Ratio).

- **Good trial**: Trial that is not bad is called good.

## Performance Spectrum
### Description

There are several equivalent ways to explain the Conditional Throughput
computation. One of the ways relies on performance
spectrum.

Take an intended load value, a trial duration value, and a finite set
of trial results, with all trials measured at that load value and duration value.

The performance spectrum is the function that maps
any non-negative real number into a sum of trial durations among all trials
in the set, that has that number, as their trial forwarding rate,
e.g. map to zero if no trial has that particular forwarding rate.

A related function, defined if there is at least one trial in the set,
is the performance spectrum divided by the sum of the durations
of all trials in the set.

That function is called the performance probability function, as it satisfies
all the requirements for probability mass function
of a discrete probability distribution,
the one-dimensional random variable being the trial forwarding rate.

These functions are related to the SUT performance spectrum,
as sampled by the trials in the set.

{::comment}
    [Middle of rewrite?]

    <mark>MKP1 The performance spectrum is the function that maps
    any non-negative real number into a sum of trial durations among all trials
    in the set, that has that number, as their trial forwarding rate,
    e.g. map to zero if no trial has that particular forwarding rate.</mark>

    <mark>MKP1 A related function, defined if there is at least one trial in the set,
    is the performance spectrum divided by the sum of the durations
    of all trials in the set.</mark>

    <mark>MKP1 That function is called the performance probability function, as it satisfies
    all the requirements for probability mass function
    of a discrete probability distribution,
    the one-dimensional random variable being the trial forwarding rate.</mark>

    <mark>MKP1 These functions are related to the SUT performance spectrum,
    as sampled by the trials in the set.</mark>

    <mark>MKP1 [VP] TODO: Introduce quantiles properly by incorporating the below.</mark>

    <mark>MKP1 [VP] TODO: "q-quantile" is plainly wrong. I meant the "p" in "p-quantile".

    - wikipedia: The 100-quantiles are called percentiles
    - also wiki: If, instead of using integers k and q, the "p-quantile" is based on a real number p with 0 < p < 1 then...
    - https://en.wikipedia.org/wiki/Quantile_function
    - exceed ratio is an input to a quantile function: percentage?
    </mark>

    <mark>MKP1 mk2 TODO for VP: Above is not making it clearer at all. Can't we really not explain the spectrum and exceed ratio with just percentiles and quantiles?</mark>

    As for any other probability function, we can talk about percentiles
    of the performance probability function, including the median.
    The Conditional Throughput will be one such quantile value
    for a specifically chosen set of trials.

    <mark>MKP2 As for any other probability function, we can talk about percentiles
    of the performance probability function, including the median.
    The Conditional Throughput will be one such quantile value
    for a specifically chosen set of trials.</mark>

{:/comment}

Take a set of all full-length trials performed at the Relevant Lower Bound,
sorted by decreasing trial forwarding rate.
The sum of the durations of those trials
may be less than the Goal Duration Sum, or not.
If it is less, add an imaginary trial result with zero trial forwarding rate,
such that the new sum of durations is equal to the Goal Duration Sum.
This is the set of trials to use.

If the quantile touches two trials,

{::comment}
    [Clarity.]

    <mark>mk edit note: What does it mean "quantile touches two trials"?
    Do you mean two trials are within specific quantile or percentile?</mark>

{:/comment}

the larger trial forwarding rate (from the trial result sorted earlier) is used.

{::comment}
    [Oh, unspecified exceed ratio?]

    <mark>the larger trial forwarding rate (from the trial result sorted earlier) is used.</mark>

    <mark>mk edit note: Why is that? Is it because you silently assumed that
    quantile here is median or 50th percentile?</mark>

{:/comment}

The resulting quantity is the Conditional Throughput of the goal in question.

{::comment}
    [Motivation has lead to code. Now code is definition, this should be equivalent.]

    <mark>The resulting quantity is the Conditional Throughput of the goal in question.</mark>

    <mark>mk edit note: Is this is supposed to be another definition of
    Conditional Throughput? If so, how does this relate to Performance
    Spectrum? I suggest to either remove these unclear paragraphs above and
    rely on examples below that are clear, or rework above so it fits the
    flow. Cause right now it's confusion. Even more so, that
    [Conditional Throughput] (#Conditional-Throughput) has been already
    defined elsewhere in the document.</mark>

{:/comment}

A set of examples follows.

### First Example

- [Goal Exceed Ratio] (#Goal-Exceed-Ratio) = 0 and [Goal Duration Sum] (#Goal-Duration-Sum) has been reached.
- Conditional Throughput is the smallest trial forwarding rate among the trials.

### Second Example

- Goal Exceed Ratio = 0 and Goal Duration Sum has not been reached yet.
- Due to the missing duration sum, the worst case may still happen, so the Conditional Throughput is zero.
- This is not reported to the user, as this load cannot become the Relevant Lower Bound yet.

### Third Example

- Goal Exceed Ratio = 50% and Goal Duration Sum is two seconds.
- One trial is present with the duration of one second and zero loss.
- The imaginary trial is added with the duration of one second and zero trial forwarding rate.
- The median would touch both trials, so the Conditional Throughput is the trial forwarding rate of the one non-imaginary trial.
- As that had zero loss, the value is equal to the offered load.

{::comment}
    [Middle of rewrite?]

    <mark>MKP2 mk edit note: how is the median "touching" both trials?
    Isn't median of even set of data samples
    the average of the two middle data points,
    in this case the non-imaginary trial and the imaginary one?</mark>

    <mark>MKP2 Note that Appendix B does not take into account short trial results.</mark>

    <mark>MKP2 mk edit note: Whis is this relevant here? Appendix B has not been mentioned in this section.</mark>

{:/comment}

### Summary

While the Conditional Throughput is a generalization of the trial forwarding rate,
its definition is not an obvious one.

Other than the trial forwarding rate, the other source of intuition
is the quantile in general, and the median the recommended case.

{::comment}
    [Next version of MLRsearch library may invent new quantity that is more stable.]

    <mark>In future, different quantities may prove more useful,
    especially when applying to specific problems,
    but currently the Conditional Throughput is the recommended compromise,
    especially for repeatability and comparability reasons.</mark>

    <mark>MKP2 mk edit note: This is future looking and hand wavy without
    specifics. What are the "specific problems" that are referred here?
    Networking, else?Some specific behaviours, if so, what sort? If
    something is classified as future work, it needs to be better defined.
    The same applies to any out of scope statements.</mark>

{:/comment}

##  Trials with Single Duration

{::comment}
    [Clarity.]

    <mark>MKP2 mk edit note: Need to improve explanations in this subsection.</mark>

{:/comment}

When goal attributes are chosen in such a way that every trial has the same
intended duration, the load classification is simpler.

The following description follows the motivation
of Goal Loss Ratio, Goal Exceed Ratio, and Goal Duration Sum.

If the sum of the durations of all trials (at the given load)
is less than the Goal Duration Sum, imagine two scenarios:

- **best case scenario**: all subsequent trials having zero loss, and 
- **worst case scenario**: all subsequent trials having 100% loss.

Here we assume there are as many subsequent trials as needed
to make the sum of all trials equal to the Goal Duration Sum.

The exceed ratio is defined using sums of durations
(and number of trials does not matter), so it does not matter whether
the "subsequent trials" can consist of an integer number of full-length trials.

In any of the two scenarios, best case and worst case, we can compute the load exceed ratio,
as the duration sum of good trials divided by the duration sum of all trials,
in both cases including the assumed trials.

Even if, in the best case scenario, the load exceed ratio is larger
than the Goal Exceed Ratio, the load is an upper bound.

MKP2 Even if, in the worst case scenario, the load exceed ratio is not larger
than the Goal Exceed Ratio, the load is a lower bound.

{::comment}
    [Middle of rewrite?]

    <mark>Even if</mark>, in the best case scenario, the load exceed ratio is larger
    than the Goal Exceed Ratio, the load is an upper bound.

    <mark>MKP2 Even if</mark>, in the worst case scenario, the load exceed ratio is not larger
    than the Goal Exceed Ratio, the load is a lower bound.

    <mark>MKP2 mk edit note: I am confused by "Even if" prefixing
    each of the above statements. And even more so by your version
    with "If even".</mark>

    <mark>mk edit note: I do not get how this statements are true, as they
    are counter-intuitive. For the best case scenario, if load exceed ratio
    is larger than the goal exceed ratio, I expect the load to be lower
    bound. Need more examples.</mark>

{:/comment}

More specifically:

- Take all trials measured at a given load.
- The sum of the durations of all bad full-length trials is called the bad sum.
- The sum of the durations of all good full-length trials is called the good sum.
- The result of adding the bad sum plus the good sum is called the measured sum.
- The larger of the measured sum and the Goal Duration Sum is called the whole sum.
- The whole sum minus the measured sum is called the missing sum.
- The optimistic exceed ratio is the bad sum divided by the whole sum.
- The pessimistic exceed ratio is the bad sum plus the missing sum, that divided by the whole sum.
- If the optimistic exceed ratio is larger than the Goal Exceed Ratio, the load is classified as an upper bound.
- If the pessimistic exceed ratio is not larger than the Goal Exceed Ratio, the load is classified as a lower bound.
- Else, the load is classified as undecided.

The definition of pessimistic exceed ratio is compatible with the logic in
the Conditional Throughput computation, so in this single trial duration case,
a load is a lower bound if and only if the Conditional Throughput
loss ratio is not larger than the Goal Loss Ratio.

{::comment}
    [Useful (depends on the whole chapter).]

    <mark>MKP2 mk edit note: I do not get the defintion of optimistic and
    pessmistic exceed ratios. Please define or describe what they
    are.</mark>

{:/comment}

If it is larger, the load is either an upper bound or undecided.

## Trials with Short Duration

### Scenarios

Trials with intended duration smaller than the goal final trial duration
are called short trials.
The motivation for load classification logic in the presence of short trials
is based around a counter-factual case: What would the trial result be
if a short trial has been measured as a full-length trial instead?

There are three main scenarios where human intuition guides
the intended behavior of load classification.

#### False Good Scenario

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

{::comment}
    [I agree.]

    <mark>MKP2 mk edit note: It may be worth adding why that is. i.e. because
    there is a risk that at longer trial this could turn into a bad
    trial.</mark>

{:/comment}

Effectively, we want the good short trials to be ignored, so they
do not contribute to comparisons with the Goal Duration Sum.

#### True Bad Scenario

When there is a frame loss in a short trial,
the counter-factual full-length trial is expected to lose at least as many
frames.

In practice, bad short trials are rarely turning into
good full-length trials.

In extreme cases, there are no good short trials.

In this scenario, we want the load classification
to classify the load as an upper bound just based on the abundance
of short bad trials.

Effectively, we want the bad short trials
to contribute to comparisons with the Goal Duration Sum,
so the load can be classified sooner.

#### Balanced Scenario

Some SUTs are quite indifferent to trial duration.
Performance probability function constructed from short trial results
is likely to be similar to the performance probability function constructed
from full-length trial results (perhaps with larger dispersion,
but without a big impact on the median quantiles overall).

{::comment}
    [Recheck after edits earlier.]

    <mark>MKP1 mk edit note: "Performance probability function" is this function
    defined anywhere? Mention in [Performance Spectrum] (#Performance Spectrum)
    is not a complete definition.</mark>

{:/comment}

For a moderate Goal Exceed Ratio value, this may mean there are both
good short trials and bad short trials.

This scenario is there just to invalidate a simple heuristic
of always ignoring good short trials and never ignoring bad short trials,
as that simple heuristic would be too biased.

Yes, the short bad trials
are likely to turn into full-length bad trials in the counter-factual case,
but there is no information on what would the good short trials turn into.

The only way to decide safely is to do more trials at full length,
the same as in False Good Scenario.

### Classification Logic

MLRsearch picks a particular logic for load classification
in the presence of short trials, but it is still RECOMMENDED
to use configurations that imply no short trials,
so the possible inefficiencies in that logic
do not affect the result, and the result has better explainability.

With that said, the logic differs from the single trial duration case
only in different definition of the bad sum.
The good sum is still the sum across all good full-length trials.

Few more notions are needed for defining the new bad sum:

- The sum of durations of all bad full-length trials is called the bad long sum.
- The sum of durations of all bad short trials is called the bad short sum.
- The sum of durations of all good short trials is called the good short sum.
- One minus the Goal Exceed Ratio is called the subceed ratio.
- The Goal Exceed Ratio divided by the subceed ratio is called the exceed coefficient.
- The good short sum multiplied by the exceed coefficient is called the balancing sum.
- The bad short sum minus the balancing sum is called the excess sum.
- If the excess sum is negative, the bad sum is equal to the bad long sum.
- Otherwise, the bad sum is equal to the bad long sum plus the excess sum.

Here is how the new definition of the bad sum fares in the three scenarios,
where the load is close to what would the relevant bounds be
if only full-length trials were used for the search.

#### False Good Scenario

If the duration is too short, we expect to see a higher frequency
of good short trials.
This could lead to a negative excess sum,
which has no impact, hence the load classification is given just by
full-length trials.
Thus, MLRsearch using too short trials has no detrimental effect
on result comparability in this scenario.
But also using short trials does not help with overall search duration,
probably making it worse.

#### True Bad Scenario

Settings with a small exceed ratio
have a small exceed coefficient, so the impact of the good short sum is small,
and the bad short sum is almost wholly converted into excess sum,
thus bad short trials have almost as big an impact as full-length bad trials.
The same conclusion applies to moderate exceed ratio values
when the good short sum is small.
Thus, short trials can cause a load to get classified as an upper bound earlier,
bringing time savings (while not affecting comparability).

#### Balanced Scenario

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

## Trials with Longer Duration

If there are trial results with an intended duration larger
than the goal trial duration, the precise definitions
in Appendix A and Appendix B treat them in exactly the same way
as trials with duration equal to the goal trial duration.

But in configurations with moderate (including 0.5) or small
Goal Exceed Ratio and small Goal Loss Ratio (especially zero),
bad trials with longer than goal durations may bias the search
towards the lower load values, as the noiseful end of the spectrum
gets a larger probability of causing the loss within the longer trials.

{::comment}
    [Use single goal when testing externaly, deviate freely in internal tests.]

    <mark>For some users, this is an acceptable price</mark>
    <mark>for increased configuration flexibility</mark>
    <mark>(perhaps saving time for the related goals),</mark>
    <mark>so implementations SHOULD allow such configurations.</mark>
    <mark>Still, users are encouraged to avoid such configurations</mark>
    <mark>by making all goals use the same final trial duration,</mark>
    <mark>so their results remain comparable across implementations.</mark>

    <mark>MKP2 mk edit note: This paragraph has no value in my view.
    Statements like "For some users, this is an acceptable price
    for increased configuration flexibility" do not make sense.
    Configuration flexibility for flexibility sake is not a valid argument
    in the specification that aims at standardising benchmarking methodologies.
    If one wants to test with longer durations,
    then one should configure these as Goal Final Trial Duration.
    Simple, no? Or am I reading this point wrong?</mark>

{:/comment}

{::comment}
    [MKP4 Out of scope here, subject for future work]

    # Current practices?

    <mark>MKP2 [VP] TODO: Even if not mentioned in spec (not even recommended),
    some tricks from CSIT code may be worth mentioning? Not sure.</mark>

    <mark>MKP2 [VP] TODO: Tricks with big impact on search time
    can be mentioned so that Addressed Problems : Long Test Duration
    has something specific to refer to.</mark>

    <mark>MKP2 [VP] TODO: It is important to mention trick that have impact
    on repeatability and comparability.</mark>

    <mark>MKP2 [VP] TODO: CSIT computes a discrete "grid" of load values to use.</mark>

    <mark>MKP2 [VP] TODO:
    If all Goal Widths are aligned, there is one common coarse grid.
    In that case, NDR (and even PDR conditional throughput
    for tests with zer-or-big losses) values are identical in trending,
    hiding the real performance variance, and causing fake anomaly
    when the performance shifts just one gridpoint.
    </mark>

    <mark>MKP2 [VP] TODO: Conversely, when Goal Width do not match well,
    CSIT needs to compute a fine-grained grid to match them all.
    In this case, similar performances can be "rounded differently",
    mostly based on specific loss that happened at Max Load,
    where SUT may be less stable than around PDR.
    This way trending sees higher variance (still within corresponding Goal Width),
    but at least there are no fake anomalies.
    </mark>

    <mark>MKP2 [VP] TODO: In general, do not trust stdev if not larged than width.</mark>

    <mark>MKP2 [VP] TODO: De we have a chapter section fosucing on design principles?
    - Make Controller API independent from Measurer API.
    - The "allowed if makes worse" principle:
      - RFC1242 specmanship happens when testing own DUTs.
      - Shortening trial wait times only risks making goal results lower.
      - So it is fine to save time aggressively when testing own DUTs.
      </mark>

{:/comment}


{::comment}
    [Will be nice if made substantial.]

    # Addressed Problems

    <mark>MKP1 all of this section requires updating based on the updated content.
    And it is for information only anyways. In fact not sure it's needed.
    Maybe in appendix for posterity.</mark>

    Now when MLRsearch is clearly specified and explained,
    it is possible to summarize how does MLRsearch specification help with problems.

    Here, "multiple trials" is a shorthand for having the goal final trial duration
    significantly smaller than the Goal Duration Sum.
    This results in MLRsearch performing multiple trials at the same load,
    which may not be the case with other configurations.

    ## Long Test Duration

    As shortening the overall search duration is the main motivation
    of MLRsearch library development, the library implements
    multiple improvements on this front, both big and small.

    Most of implementation details are not constrained by MLRsearch specification,
    so that future implementations may keep shortening the search duration even more.

    One exception is the impact of short trial results on the Relevant Lower Bound.
    While motivated by human intuition, the logic is not straightforward.
    In practice, configurations with only one common trial duration value
    are capable of achieving good overal search time and result repeatability
    without the need to consider short trials.

    ### Impact of goal attribute values

    From the required goal attributes, the Goal Duration Sum
    remains the best way to get even shorter searches.

    Usage of multiple trials can also save time,
    depending on wait times around trial traffic.

    The farther the Goal Exceed Ratio is from 0.5 (towards zero or one),
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

    Trivially suported by the Goal Loss Ratio attribute.

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
    and perhaps also a large value for the Goal Exceed Ratio.

    Implementations may offer other (optional) configuration attributes
    to become less conservative, but currently it is not clear
    what impact would that have on repeatability.

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

Some phrases and statements in this document were created
with help of Mistral AI (mistral.ai).

Many thanks to Alec Hothan of the OPNFV NFVbench project for thorough
review and numerous useful comments and suggestions in the earlier versions of this document.

Special wholehearted gratitude and thanks to the late Al Morton for his
thorough reviews filled with very specific feedback and constructive
guidelines. Thank you Al for the close collaboration over the years,
for your continuous unwavering encouragement full of empathy and
positive attitude. Al, you are dearly missed.

# Appendix A: Load Classification

This section specifies how to perform the load classification.

Any intended load value can be classified, according to a given [Search Goal] (#Search-Goal).

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the Measurer.

The block at the end of this appendix holds pseudocode
which computes two values, stored in variables named
`optimistic` and `pessimistic`.

{::comment}
    [We have other section re optimistic. Not going to talk about variable naming here.]

    <mark>MKP2 mk edit note: Need to add the description of what
    the `optimistic` and `pessimistic` variables represent.
    Or a reference to where this is described
    e.g. in [Single Trial Duration] (#Single-Trial-Duration) section.</mark>

{:/comment}

The pseudocode happens to be a valid Python code.

If values of both variables are computed to be true, the load in question
is classified as a lower bound according to the given Search Goal.
If values of both variables are false, the load is classified as an upper bound.
Otherwise, the load is classified as undecided.

The pseudocode expects the following variables to hold values as follows:

- `goal_duration_sum`: The duration sum value of the given Search Goal.

- `goal_exceed_ratio`: The exceed ratio value of the given Search Goal.

- `good_long_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  not higher than the Goal Loss Ratio.

- `bad_long_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  higher than the Goal Loss Ratio.

- `good_short_sum`: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with a Trial Loss Ratio
  not higher than the Goal Loss Ratio.

- `bad_short_sum`: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with a Trial Loss Ratio
  higher than the Goal Loss Ratio.

The code works correctly also when there are no trial results at a given load.

~~~ python
balancing_sum = good_short_sum * goal_exceed_ratio / (1.0 - goal_exceed_ratio)
effective_bad_sum = bad_long_sum + max(0.0, bad_short_sum - balancing_sum)
effective_whole_sum = max(good_long_sum + effective_bad_sum, goal_duration_sum)
quantile_duration_sum = effective_whole_sum * goal_exceed_ratio
optimistic = effective_bad_sum <= quantile_duration_sum
pessimistic = (effective_whole_sum - good_long_sum) <= quantile_duration_sum
~~~

# Appendix B: Conditional Throughput

This section specifies how to compute Conditional Throughput, as referred to in section [Conditional Throughput] (#Conditional-Throughput).

Any intended load value can be used as the basis for the following computation,
but only the Relevant Lower Bound (at the end of the search)
leads to the value called the Conditional Throughput for a given Search Goal.

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the Measurer.

The block at the end of this appendix holds pseudocode
which computes a value stored as variable `conditional_throughput`.

{::comment}
    [CT is CT. But text could make more obvious.]

    <mark>MKP2 mk edit note: Need to add the description of what does
    the `conditional_throughput` variable represent.
    Or a reference to where this is described
    e.g. in [Conditional Throughput] (#Conditional-Throughput) section.</mark>

{:/comment}

The pseudocode happens to be a valid Python code.

The pseudocode expects the following variables to hold values as follows:

- `goal_duration_sum`: The duration sum value of the given Search Goal.

- `goal_exceed_ratio`: The exceed ratio value of the given Search Goal.

- `good_long_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  not higher than the Goal Loss Ratio.

- `bad_long_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  higher than the Goal Loss Ratio.

- `long_trials`: An iterable of all trial results from trials with trial duration
  at least equal to the goal final trial duration,
  sorted by increasing the Trial Loss Ratio.
  A trial result is a composite with the following two attributes available:

  - `trial.loss_ratio`: The Trial Loss Ratio as measured for this trial.

  - `trial.duration`: The trial duration of this trial.

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

{::comment}
    [Final checklist.]

    <mark>[VP] Final Checks. Only mark as done when there are no active todos above.</mark>

    <mark>[VP] Rename chapter/sub-/section to better match their content.</mark>

    <mark>MKP3 [VP] TODO: Recheck the definition dependencies go bottom-up.</mark>

    <mark>[VP] TODO: Unify external reference style (brackets, spaces, section numbers and names).</mark>

    <mark>[VP] TODO: Add internal links wherever Captialized Term is mentioned.</mark>

    <mark>MKP2 [VP] TODO: Capitalization of New Terms: useful when editing and reviewing,
    but I still vote to remove capitalization before final submit,
    because all other RFCs I see only capitalize due to being section title.</mark>

    <mark>[VP] TODO: If time permits, keep improving formal style (e.g. using AI).</mark>

{:/comment}

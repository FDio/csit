---

title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-09
date: 2025-01-13

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
the data planes of software-based networking systems.

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

The purpose of this document is to describe the Multiple Loss Ratio search
(MLRsearch) methodology, optimized for determining
data plane throughput in software-based networking devices and functions.

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

To address these problems,
the MLRsearch test methodology specification employs the following enhancements:

- Allow multiple short trials instead of one big trial per load.
  - Optionally, tolerate a percentage of trial results with higher loss.
- Allow searching for multiple Search Goals, with differing loss ratios.
  - Any trial result can affect each Search Goal in principle.
- Insert multiple coarse targets for each Search Goal, earlier ones need
  to spend less time on trials.
  - Earlier targets also aim for lesser precision.
  - Use Forwarding Rate (FR) at maximum offered load
    [RFC2285] (Section 3.6.2) to initialize bounds.
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

DUT as:

- The network frame forwarding device to which stimulus is offered and
  response measured [RFC2285] (Section 3.1.1).

SUT as:

- The collective set of network devices as a single entity to which
  stimulus is offered and response measured [RFC2285] (Section 3.1.2).

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

[RFC1242] (Section 3.17) defines throughput as:
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
for the load that satisfies a non-zero Goal Loss Ratio.
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
throughput for non-zero Goal Loss Ratio values
(and other possible repeatability enhancements), while being precise enough
to force a specific way to resolve trial result inconsistencies.
But until such a definition is agreed upon, the correct way to handle
inconsistent trial results remains an open problem.

Relevant Lower Bound is the MLRsearch term that addresses this problem.

# MLRsearch Specification

MLRsearch specification describes all technical
definitions needed for evaluating whether a particular test procedure
complies with MLRsearch specification.

{::comment}
    [Good idea for 08, maybe ask BMWG first?]

    <mark>TODO VP: Separate Requirements and Recommendations/Suggestions
    paragraphs? (currently requirements are in discussion subsections -
    discussion should only clarify things without adding new
    requirements)</mark>
{:/comment}

Some terms used in the specification are capitalized.
It is just a stylistic choice for this document,
reminding the reader this term is introduced, defined or explained
elsewhere in the document.
Lowercase variants are equally valid.

Each per term subsection contains a short **Definition** paragraph
containing a minimal definition and all strict REQUIREMENTS, followed
by **Discussion** paragraphs containing some important consequences and
RECOMMENDATIONS.
Other text in this section discusses document structure
and non-authoritative summaries.

## Overview

MLRsearch Specification describes a set of abstract system components,
acting as functions with specified inputs and outputs.

A test procedure is said to comply with MLRsearch Specification
if it can be conceptually divided into analogous components,
each satisfying requirements for the corresponding MLRsearch component.
Any such compliant test procedure is called a MLRsearch Implementation.

The Measurer component is tasked to perform Trials,
the Controller component is tasked to select Trial Durations and Loads,
the Manager component is tasked to pre-configure everything
and to produce the test report.
The test report explicitly states Search Goals (as Controller inputs)
and corresponding Goal Results (Controller outputs).

The Manager calls the Controller once,
the Controller keeps calling the Measurer
until all stopping conditions are met.

The part where Controller calls the Measurer is called the Search.
Any activity done by the Manager before it calls the Controller
(or after Controller returns) is not considered to be part of the Search.

MLRsearch Specification prescribes regular search results and recommends
their stopping conditions. Irregular search results are also allowed,
they may have different requirements and stopping conditions.

Search results are based on Load Classification.
When measured enough, any chosen Load can either achieve or fail
each Search Goal (separately), thus becoming
a Lower Bound or an Upper Bound for that Search Goal.

When the Relevant Lower Bound is close enough to Relevant Upper Bound
according to Goal Width, the Regular Goal Result is found.
Search stops when all Regular Goal Results are found,
or when some Search Goals are proven to have only Irregular Goal Results.

{::comment}

    TODO-P1: An implementation may add additional attributes to inputs and outputs.

    TODO-P1: An implementation may require some attributes not required by specification.

    TODO-P1: An implementation may support "missing" attributes by applying "reasonable defaults".

{:/comment}

## Quantities

MLRsearch specification uses a number of specific quantities,
some of them can be expressed in several different units.

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

{::comment}

    TODO-P1: Merge into Glossary! MK - IMV this section should stay here as is.

{:/comment}

This specification relies on the following three documents that should
be consulted before attempting to make use of this document:

- RFC 1242 "Benchmarking Terminology for Network Interconnect Devices"
  contains basic term definitions. 

- RFC 2285 "Benchmarking Terminology for LAN Switching Devices" adds
  more terms and discussions, describing some known network
  benchmarking situations in a more precise way.

- RFC 2544 "Benchmarking Methodology for Network Interconnect Devices"
  contains discussions of a number of terms and additional methodology
  requirements.

Definitions of some central terms from above documents are copied and
discussed in the following subsections.

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
    - Data Rate of [RFC2544] (section 14. Bidirectional traffic)
     - seems equal to input frame rate [RFC2544] (23. Trial description).
    - [RFC2544] (section 21. Bursty traffic) suggests non-constant loads?
    - Intended Load of [RFC2285] (section 3.5.1 Intended load (Iload))
    - [RFC2285] (Section 3.5.2 Offered load (Oload))
    - Forwarding Rate as defined in [RFC2285] (section 3.6.1 Forwarding rate (FR))
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

{:/comment}

{::comment}
    [Important, just not enough time in 07.]
    
    <mark>MKP3 [VP] TODO: Verify that MLRsearch specification does not discuss
    meaning of existing terms without quoting their original definition.</mark>

{:/comment}

### SUT

Defined in [RFC2285] (Section 3.1.2) as follows.

Definition:

The collective set of network devices to which stimulus is offered
as a single entity and response measured.

Discussion:

An SUT consisting of a single network device is also allowed.

### DUT

Defined in [RFC2285] (Section 3.1.1) as follows.

Definition:

The network forwarding device to which stimulus is offered and
response measured.

Discussion:

DUT, as a sub-component of SUT, is only indirectly mentioned
in MLRsearch specification, but is of key relevance for its motivation.

### Trial

A trial is the part of the test described in [RFC2544] (Section 23).

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

The definition describes some traits, and it is not clear whether all of them
are REQUIRED, or some of them are only RECOMMENDED.

Trials are the only stimuli the SUT is expected to experience
during the Search.

For the purposes of the MLRsearch specification,
it is ALLOWED for the test procedure to deviate from the [RFC2544] description,
but any such deviation MUST be described explicitly in the test report.

In some discussion paragraphs, it is useful to consider the traffic
as sent and received by a tester, as implicitly defined
in [RFC2544] (Section 6).

{::comment}

    TODO-P2: Assert traffic is sent only in phase c) and received in phases c) and d).

{:/comment}

An example of deviation from [RFC2544] is using shorter wait times,
compared to those described in phases b), d) and e).

## Trial Terms

This section defines new and redefine existing terms for quantities
relevant as inputs or outputs of a Trial, as used by the Measurer component.

### Trial Duration

Definition:

Trial Duration is the intended duration of the traffic part of a Trial.

Discussion:

This quantity does not include any preparation nor waiting
described in section 23 of [RFC2544] (Section 23).

While any positive real value may be provided, some Measurer implementations
MAY limit possible values, e.g. by rounding down to nearest integer in seconds.
In that case, it is RECOMMENDED to give such inputs to the Controller
so the Controller only proposes the accepted values.

### Trial Load

Definition:

Trial Load is the per-interface Intended Load for a Trial.

Discussion:

For test report purposes, it is assumed that this is a constant load by default,
as specified in [RFC1242] (Section 3.4).

Trial Load MAY be only an average load,
e.g. when the traffic is intended to be bursty,
e.g. as suggested in [RFC2544] (Section 21).
In the case of non-constant load, the test report
MUST explicitly mention how exactly non-constant the traffic is.

Trial Load is equivalent to the quantities defined
as constant load of [RFC1242] (Section 3.4),
data rate of [RFC2544] (Section 14),
and Intended Load of [RFC2285] (Section 3.5.1),
in the sense that all three definitions specify that this value
applies to one (input or output) interface.

For test report purposes, multi-interface aggregate load MAY be reported,
and is understood as the same quantity expressed using different units.
From the report it MUST be clear whether a particular Trial Load value
is per one interface, or an aggregate over all interfaces.

Similarly to Trial Duration, some Measurers may limit the possible values
of trial load. Contrary to trial duration, the test report is NOT REQUIRED
to document such behavior, as in practice the load differences
are negligible (and frequently undocumented).

It is ALLOWED to combine Trial Load and Trial Duration values in a way
that would not be possible to achieve using any integer number of data frames.

If a particular Trial Load value is not tied to a single Trial,
e.g. if there are no Trials yet or if there are multiple Trials,
this document uses a shorthand **Load**.

{::comment}
    [I feel this is important, to be discussed separately (not in-scope).]

    <mark>MKP2 [VP] TODO: Explain why are we not using Oload.
    1. MLRsearch implementations cannot react correctly to big differences
    between Iload and Oload.
    2. The media between the tested and the DUT are thus considered to be part of SUT.
    If DUT causes congestion control, it is not expected to handle Iload.
    </mark>
    
    See further discussion in [Trial Forwarding Ratio](#trial-forwarding-ratio)
    and in [Measurer ](#measurer) sections for other related issues.
    
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
Trial Duration and Trial Load.

Discussion:

When talking about multiple Trials, it is common to say "Trial Inputs"
to denote all corresponding Trial Input instances.

A Trial Input instance acts as the input for one call of the Measurer component.

Contrary to other composite quantities, MLRsearch implementations
are NOT ALLOWED to add optional attributes here.
This improves interoperability between various implementations of
the Controller and the Measurer.

### Traffic Profile

Definition:

Traffic Profile is a composite quantity containing
all attributes other than Trial Load and Trial Duration,
that are needed for unique determination of the trial to be performed.

Discussion:

All the attributes are assumed to be constant during the search,
and the composite is configured on the Measurer by the Manager
before the search starts.
This is why the traffic profile is not part of the Trial Input.

As a consequence, implementations of the Manager and the Measurer
must be aware of their common set of capabilities, so that Traffic Profile
instance uniquely defines the traffic during the Search.
The important fact is that none of those capabilities
have to be known by the Controller implementations.

The Traffic Profile SHOULD contain some specific quantities defined elsewhere.
For example [RFC2544] (Section 9) governs
data link frame sizes as defined in [RFC1242] (Section 3.5).

Several more specific quantities may be RECOMMENDED, depending on media type.
For example, [RFC2544] (Appendix C) lists frame formats and protocol addresses,
as recommended in [RFC2544] (Section 8) and [RFC2544] (Section 12).

Depending on SUT configuration, e.g. when testing specific protocols,
additional attributes MUST be included in the traffic profile
and in the test report.

Example: [RFC8219] (Section 5.3) introduces traffic setups
consisting of a mix of IPv4 and IPv6 traffic - the implied traffic profile
therefore must include an attribute for their percentage.

Other traffic properties that need to be somehow specified in Traffic
Profile, if they apply to the test scenario, include:

- bidirectional traffic from [RFC2544] (Section 14),

- fully meshed traffic from [RFC2285] (Section 3.3.3),

- and modifiers from [RFC2544] (Section 11).

### Trial Forwarding Ratio

Definition:

The Trial Forwarding Ratio is a dimensionless floating point value.
It MUST range between 0.0 and 1.0, both inclusive.
It is calculated by dividing the number of frames
successfully forwarded by the SUT
by the total number of frames expected to be forwarded during the trial.

Discussion:

For most Traffic Profiles, "expected to be forwarded" means
"intended to get transmitted from Tester towards SUT".
Only if this is not the case, the test report MUST describe the Traffic Profile
in a way that implies how Trial Forwarding Ratio should be calculated.

Trial Forwarding Ratio MAY be expressed in other units
(e.g. as a percentage) in the test report.

Note that, contrary to loads, frame counts used to compute
trial forwarding ratio are aggregates over all SUT output interfaces.

Questions around what is the correct number of frames
that should have been forwarded
is generally outside of the scope of this document.

{::comment}

    TODO-P0: Mention iload/oload difference is also out of scope.

    TODO-P2: Mention duplicate, previous-trial and other "more than
    expected" frame counts are out of scope. Recommend to count them as
    loss? MK there should be a reference about the last TODO in 1242 2285
    or 2544.

{:/comment}

{::comment}
    [Part two of iload/oload discussion.]

    See discussion in [Measurer ](#measurer) section
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

The Trial Loss Ratio is equal to one minus the Trial Forwarding Ratio.

Discussion:

100% minus the Trial Forwarding Ratio, when expressed as a percentage.

This is almost identical to Frame Loss Rate of [RFC1242] (Section 3.6).
Te only minor differences are that Trial Loss Ratio
does not need to be expressed as a percentage,
and Trial Loss Ratio is explicitly based on aggregate frame counts.

### Trial Forwarding Rate

Definition:

The Trial Forwarding Rate is a derived quantity, calculated by
multiplying the Trial Load by the Trial Forwarding Ratio.

Discussion:

It is important to note that while similar, this quantity is not identical
to the Forwarding Rate as defined in [RFC2285] (Section 3.6.1).
The latter is specific to one output interface only,
whereas the Trial Forwarding Ratio is based
on frame counts aggregated over all SUT output interfaces.

In consequence, for symmetric traffic profiles the Trial Forwarding Rate value
is equal to arithmetric average of [RFC2285] Forwarding Rate values
across all active interfaces.

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

Trial Effective Duration is a time quantity related to the trial,
by default equal to the Trial Duration.

Discussion:

This is an optional feature.
If the Measurer does not return any Trial Effective Duration value,
the Controller MUST use the Trial Duration value instead.

Trial Effective Duration may be any time quantity chosen by the Measurer
to be used for time-based decisions in the Controller.

The test report MUST explain how the Measurer computes the returned
Trial Effective Duration values, if they are not always
equal to the Trial Duration.

This feature can be beneficial for users
who wish to manage the overall search duration,
rather than solely the traffic portion of it.
Simply measure the duration of the whole trial (including all wait times)
and use that as the Trial Effective Duration.

This is also a way for the Measurer to inform the Controller about
its surprising behavior, for example when rounding the Trial Duration value.

{::comment}
    [Not very important, but easy and nice recommendation.]

    <mark>MKP2 [VP] TODO: Recommend for Controller to return all trials at relevant bounds,
    as that may better inform users when surprisingly small amount of trials
    was performed, just because the the trial effective duration values were big.</mark>
    
    <mark>MKP2 [VP] TODO: Repeat that this is not here to deal with duration stretching.</mark>

{:/comment}

### Trial Output

Definition:

Trial Output is a composite quantity. The REQUIRED attributes are
Trial Loss Ratio, Trial Effective Duration and Trial Forwarding Rate.

Discussion:

When talking about multiple trials, it is common to say "Trial Outputs"
to denote all corresponding Trial Output instances.

Implementations may provide additional (optional) attributes.
The Controller implementations MUST ignore values of any optional attribute
they are not familiar with,
except when passing Trial Output instances to the Manager.

Example of an optional attribute:
The aggregate number of frames expected to be forwarded during the trial,
especially if it is not just (a rounded-down value)
implied by Trial Load and Trial Duration.

While [RFC2285] (Section 3.5.2) requires the Offered Load value
to be reported for forwarding rate measurements,
it is NOT REQUIRED in MLRsearch Specification,
as search results do not depend on it.

{::comment}

    TODO-P1: MK note - i know that Offered Load can be calculated from Trial
    Loss Ratio and Trial Forwarding Rate but still most/all network users
    would expect to know what Trial Load was used. Also, saying that search
    results do not depend on Offered Load or Trial Load is not true :)
    VP note - I partially disagree and partially do not understand.

{:/comment}

{::comment}

    [Side tangent from iload/oload discussion. Stilll recommendation is not obvious.]

    <mark>MKP2 mk edit note: we need to more explicitly address
    the relevance or irrelevance of [RFC2285] (Section 3.5.2 Offered load (Oload)).
    Current text in [Trial Load](#trial-load) is ambiguous - quoted below.</mark>
    
    <mark>MKP2 "Questions around what is the correct number of frames that should
    have been forwarded is generally outside of the scope of this document.
    See discussion in [Measurer ](#measurer) section for more details about
    calibrating test equipment."</mark>

{:/comment}

### Trial Result

Definition:

Trial Result is a composite quantity,
consisting of the Trial Input and the Trial Output.

Discussion:

When talking about multiple trials, it is common to say "trial results"
to denote all corresponding Trial Result instances.

While implementations SHOULD NOT include additional attributes
with independent values, they MAY include derived quantities.

## Goal Terms

This section defines new terms for quantities relevant (directly or indirectly)
for inputs or outputs of the Controller component.

Several goal attributes are defined before introducing
the main composite quantity: the Search Goal.

{::comment}

    TODO-P0: Mention definitions are not informative?
    E.g. Goal Final Trial Duration and Goal Initial Trial Duration
    have the same Definition text.
    Note that these are already fixed for now, but other attributes need review.

{:/comment}

Discussions within this section are short, informal,
and referencing future sections, with the impact on search results
discussed only after introducing complete set of auxiliary terms.

### Goal Final Trial Duration

{::comment}

    TODO-P0: review updated definition, check if any informal explanation is needed.

{:/comment}

Definition:

Minimum value for Trial Duration required for classifying the Load
as a Lower Bound.

Discussion:

This attribute value MUST be positive.

Informally, while MLRsearch is allowed to perform trials shorter than this value,
the results from such short trials have only limited impact on search results.

It is RECOMMENDED for all search goals to share the same
Goal Final Trial Duration value.
Otherwise, Trial Duration values larger than the Goal Final Trial Duration
may occur, weakening the assumptions
the [Load Classification Logic](#load-classification-logic) is based on.

{::comment}

    TODO-P2: Currently not covered well in Logic chapter?

    TODO-P2: Maybe change fourth goal there to show this?

{:/comment}

### Goal Duration Sum

Definition:

A threshold value for a particular sum of Trial Effective Duration values.

Discussion:

This attribute value MUST be positive.

Informally, this prescribes the maximum amount of trials performed
at a specific Trial Load and Goal Final Trial Duration during the search.

If the Goal Duration Sum is larger than the Goal Final Trial Duration,
multiple trials may need to be performed at the same load.

See [MLRsearch Compliant with TST009](#mlrsearch-compliant-with-tst009)
for an example where possibility of multiple trials at the same load is intended.

A Goal Duration Sum value lower than the Goal Final Trial Duration
(of the same goal) could save some search time, but is NOT RECOMMENDED.

{::comment}

    TODO-P2: Currently not covered in the classification logic chapter.

{:/comment}

### Goal Loss Ratio

Definition:

A threshold value for Trial Loss Ratio values.

Discussion:

Attribute value MUST be non-negative and smaller than one.

A trial with Trial Loss Ratio larger than this value
signals the SUT may be unable to process this Trial Load well enough.

See [Throughput with Non-Zero Loss](#throughput-with-non-zero-loss)
why users may want to set this value above zero.

### Goal Exceed Ratio

Definition:

A threshold value for a particular ratio of sums of Trial Effective Duration
values.

Discussion:

Attribute value MUST be non-negative and smaller than one.

Informally, up to this proportion of High-Loss Trials
(Trial Results with Trial Loss Ratio above Goal Loss Ratio)
is tolerated at a Lower Bound.

For explainability reasons, the RECOMMENDED value for exceed ratio is 0.5 (50%),
as it simplifies some concepts by relating them to the concept of median.
Also, the value of 50% leads to smallest variation in overall Search Duration
in practice.

See [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials)
section for more details.

### Goal Width

Definition:

A threshold value for deciding whether two Trial Load values are close enough.

Discussion:

It is an optional attribute. If present, the value MUST be positive.

Informally, this acts as a stopping condition,
controlling the precision of the search.
The search stops if every goal has reached its precision.

Implementations without this attribute
MUST give the Controller other ways to control the search stopping conditions.

Absolute load difference and relative load difference are two popular choices,
but implementations may choose a different way to specify width.

The test report MUST make it clear what specific quantity is used as Goal Width.

{::comment}

    TODO-P2: Comment: While not needed for precision purposes
    larger-than-width result (e.g. when time is up) is still an Irregular result,
    so this is the way to make sure it looks irregular in report.

{:/comment}

It is RECOMMENDED to set the Goal Width (as relative difference) value
to a value no smaller than the Goal Loss Ratio.
If the reason is not obvious, see the details in
[Generalized Throughput](#generalized-throughput).

### Goal Initial Trial Duration

{::comment}

    TODO-P0: review updated definition, check if any informal explanation is needed.

{:/comment}

Definition:

Minimum value for Trial Duration required for classifying the Load as any Bound.

Discussion:

This is an example of an OPTIONAL Search Goal some implementations may support.

The reasonable default value is equal to the Goal Final Trial Duration value.

If present, this value MUST be positive.

Informally, this is the smallest Trial Duration the Controller will select
when focusing on the goal.

Strictly speaking, Trial Results with smaller Trial Duration values
are still accepted by the Load Classification logic.
This is just a way for the user to discourage trials with Trial Duration
values deemed as too unreliable for this SUT and this Search Goal.

### Search Goal

Definition:

The Search Goal is a composite quantity consisting of several attributes,
some of them are required.

Required attributes:
- Goal Final Trial Duration
- Goal Duration Sum
- Goal Loss Ratio
- Goal Exceed Ratio

Optional attributes:
- Goal Initial Trial Duration
- Goal Width

Discussion:

Implementations MAY add their own attributes.
Those additional attributes may be required by the implementation
even if they are not required by MLRsearch specification.
But it is RECOMMENDED for those implementations
to support missing values by providing reasonable default values.

{::comment}

    TODO2: MK last sentence doesn't make sense.
    VP: Added TODOs to Overview section.

{:/comment}

See [Compliance ](#compliance) for important Search Goal instances.

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

For example, Traffic Profile is configured on the Measurer by the Manager,
without explicit assistance of the Controller.

{::comment}

    TODO-P0: This paragraph is for implementers.

    TODO2: MK implementation hints are fine, and do not have to be preceded
with any remark of the sort you're suggesting IMV.

{:/comment}

The order of Search Goal instances in a list SHOULD NOT
have a big impact on Controller Output,
but MLRsearch implementations MAY base their behavior on the order
of Search Goal instances in a list.

{::comment}
    [User recommendation, we should have separate section summarizing those.]
    
    Also, it is recommended to avoid "incomparable" goals, e.g. one with
    lower loss ratio but higher exceed ratio, and other with higher loss ratio
    but lower loss ratio. In worst case, this can make the search to last too long.
    Implementations are RECOMMENDED to sort the goals and start with
    stricter ones first, as bounds for those will not get invalidated
    byt measureing for less trict goal later in the search.

{:/comment}

#### Max Load

Definition:

Max Load is an optional attribute of Controller Input.
It is the maximal value the Controller is allowed to use for Trial Load values.

Discussion:

Max Load is an example of an optional attribute (outside the list of Search Goals)
required by some implementations of MLRsearch.

In theory, each search goal could have its own Max Load value,
but as all trials are possibly affecting all Search Goals,
it makes more sense for a single Max Load value to apply
to all Search Goal instances.

While Max Load is a frequently used configuration parameter, already governed
(as maximum frame rate) by [RFC2544] (Section 20)
and (as maximum offered load) by [RFC2285] (Section 3.5.3),
some implementations may detect or discover it
(instead of requiring a user-supplied value).

{::comment}

    TODO-P0: Move this (and goal width) to RUB discussion or other explanation instead.

    TODO2: MK i think it belongs here, as input parameter. may refer to
    section "Hard Performance Limit" though.

{:/comment}

In MLRsearch specification, one reason for listing
the [Relevant Upper Bound](#relevant-upper-bound) as a required attribute
is that it makes the search result independent of Max Load value.

{::comment}

    TODO2: MK RUB is not an attribute, it's Result Term. Hence above
    sentence does not make sense and should be removed.
    VP: RUB is an attribure of Goal Result composite quantity.

{:/comment}

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

#### Min Load

Definition:

Min Load is an optional attribute of Controller Input.
It is the minimal value the Controller is allowed to use for Trial Load values.

Discussion:

Min Load is another example of an optional attribute
required by some implementations of MLRsearch.
Similarly to Max Load, it makes more sense to prescribe one common value,
as opposed to using a different value for each Search Goal.

Min Load is mainly useful for saving time by failing early,
arriving at an Irregular Goal Result when Min Load gets classified
as an Upper Bound.

For implementations, it is useful to require Min Load to be non-zero
and large enough to result in at least one frame being forwarded
even at smallest allowed Trial Duration,
so Trial Loss Ratio is always well-defined,
and the implementation can use relative Goal Width
(without running into issues around zero Trial Load value).

{::comment}

    TODO2: MK last 3 lines need to be reworded, as they don't make sense,
    and i can't suggest alternative wording.

{:/comment}

## Auxiliary Terms

While the terms defined in this section are not strictly needed
when formulating MLRsearch requirements, they simplify the language used
in discussion paragraphs and explanation chapters.

### Current and Final Quantities

{::comment}

    TODO2: MK doesn't this content belong to "Quantities" section at the
    beginning of the doc?
    VP: Probably yes, should be moved.

{:/comment}

Some quantites are defined in a way that allows them to be computed
in the middle of the Search. Other quantities are specified in a way
that allows them to be computed only after the Search ends.
And some quantities are important only after the Search ended,
but are computable also before the Search ends.

The adjective **current** marks a quantity that is computable
before the Search ends, but the computed value may change during the Search.
When such value is relevant for the search result, the adjective **final**
may be used to denote the value at the end of the Search.

{::comment}

    TODO2: MK **current** and **final** adjectives seem to relate to values
    of quantities, and not quantities themselves, or?

{:/comment}

### Trial Classification

{::comment}

    TODO2: MK do we need this explanation below. Can't we just leave this
    section header and then list trial types as is?

{:/comment}

When one Trial Result instance is compared to one Search Goal instance,
several relations can be named using short adjectives.

As trial results do not affect each other, this **Trial Classification**
does not change during the Search.

{::comment}

    TODO-P0: Is it obvious the adjectives can be combined?

    TODO2: MK **current** and **final** adjectives seem to relate to values
    of quantities, and not quantities themselves, or?

{:/comment}

#### High-Loss Trial

A trial with Trial Loss Ratio larger than a Goal Loss Ratio value
is called a **high-loss trial**, with respect to given Search Goal
(or lossy trial, if Goal Loss Ratio is zero).

#### Low-Loss Trial

If a trial is not high-loss, it is called a **low-loss trial**
(or even zero-loss trial, if Goal Loss Ratio is zero).

#### Short Trial

A trial with Trial Duration shorter than the Goal Final Trial Duration
is called a **short trial** (with respect to the given Search Goal).

#### Full-Length Trial

A trial that is not short is called a **full-length** trial.

Note that this includes Trial Durations larger than Goal Final Trial Duration.

#### Long Trial

A trial with Trial Duration longer than the Goal Final Trial Duration
is called a **long trial**.

{::comment}

    TODO-P0: If used in Logic chapter, add to Glossary and maybe move before full-length.

    TODO-P2: Maybe change fourth goal there to show this better?

    TODO-P0: If not used, delete.

{:/comment}

### Load Classification

{::comment}

    TODO-P0: Turn into a precise definition paragraph.

{:/comment}

When the set of all Trial Result instances performed so far
at one Trial Load is compared to one Search Goal instance,
two relations can be named using the concept of a bound.

In general, such bounds are a current quantity,
even though cases of changing bounds is rare in practice.

#### Upper Bound

Definition:

A Trial Load value is called an Upper Bound if and only if it is classified
as such by [Appendix A: Load Classification](#appendix-a-load-classification)
algorithm for the given Search Goal at the current moment of the Search.

Discussion:

In more detail, the set of all Trial Results
performed so far at the Trial Load (and any Trial Duration)
is certain to fail to uphold all the requirements of the given Search Goal,
mainly the Goal Loss Ratio in combination with the Goal Exceed Ratio.
Here "certain to fail" relates to any possible results within the time
remaining till Goal Duration Sum.

{::comment}

    TODO2: MK not sure above paragraph adds any explanation value whatsover.
    It verges into the domain of discussing all possible outcomes and does
    nothing to clarify what upper bound is about. And as there is no clear
    explanation of upper bound i added one above.

{:/comment}

One search goal can have multiple different Trial Load values
classified as its Upper Bounds.
As search progresses and more trials are measured,
any load value can become an Upper Bound.

Also, a load can stop being an Upper Bound, but that
can only happen when more than Goal Duration Sum of trials are measured
(e.g. because another Search Goal needs more trials at this load).
In that case the load becomes a Lower Bound (see next subsection),
and we say the previous Upper Bound got Invalidated.

{::comment}
    [Medium priority, depends on how many user recommendations we have.]

    With non-zero exceed ratio values, a short high-loss trial may not be enough
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
    one high-loss trial (even short) is enough to pin the classification.

{:/comment}

#### Lower Bound

Definition:

A Trial Load value is called a Lower Bound if and only if it is classified
as such by [Appendix A: Load Classification](#appendix-a-load-classification)
algorithm for the given Search Goal at the current moment of the search.

Discussion:

{::comment}

    MK:
    It is the minimum value in a range being searched, together with Upper
    Bound, defining the interval within which MLRsearch operates for
    specific Search Goal, iteratively narrowing down to arrive to Search
    Result.
    
    VP: That is wrong in situations with Loss Inversions.

{:/comment}

In more detail, the set of all Trial Results
performed so far at the Trial Load (and any Trial Duration)
is certain to uphold all the requirements of the given Search Goal,
mainly the Goal Loss Ratio in combination with the Goal Exceed Ratio.
Here "certain to uphold" relates to any possible results within the time
remaining till Goal Duration Sum.

{::comment}

    TODO2: MK similar to previous section - not sure above paragraph adds
    any explanation value whatsover. It verges into the domain of
    discussing all possible outcomes and does nothing to clarify what upper
    bound is about. And as there is no clear explanation of upper bound i
    added one above.

{:/comment}

One search goal can have multiple different Trial Load values
classified as its Lower Bounds.
As search progresses and more trials are measured,
any load value can become a Lower Bound.

No load can be both an Upper Bound and a Lower Bound for the same Search goal
at the same time, but it is possible for a higher load to be a Lower Bound
while a smaller load is an Upper Bound.

Also, a load can stop being a Lower Bound, but that
can only happen when more than Goal Duration Sum of trials are measured
(e.g. because another Search Goal needs more trials at this load).
In that case the load becomes an Upper Bound,
and we say the previous Lower Bound got Invalidated.

## Result Terms

Before defining the full structure of Controller Output,
it is useful to define the composite quantity called Goal Result.
The following subsections define its attribute first,
before describing the Goal Result quantity.

There is a correspondence between Search Goals and Goal Results.
Most of the following subsections refer to a given Search Goal,
when defining their terms.
Conversely, at the end of the search, each Search Goal instance
has its corresponding Goal Result instance.

### Relevant Upper Bound

Definition:

The Relevant Upper Bound is the smallest Trial Load value
classified as an Upper Bound for the given Search Goal at the end of the search.

Discussion:

If no measured load had enough high-loss trials,
the Relevant Upper Bound MAY be not-existent.
For example, when Max Load is classified as a Lower Bound.

{::comment}

    TODO-P0: Delete or move:

    TODO2: MK duplicate content explaining the same as above but with
    inverse logic.

{:/comment}

Conversely, if Relevant Upper Bound exists,
it is not affected by Max Load value.

### Relevant Lower Bound

Definition:

The Relevant Lower Bound is the largest Trial Load value
among those smaller than the Relevant Upper Bound, that got classified
as a Lower Bound for the given Search Goal at the end of the search.

Discussion:

If no load had enough low-loss trials, the relevant lower bound
MAY be non-existent.

Strictly speaking, if the Relevant Upper Bound does not exist,
the Relevant Lower Bound also does not exist.
In a typical case, Max Load is classified as a Lower Bound,
but it is not clear whether a higher value
would be found as a Lower Bound if the search was not limited
by this Max Load value.

### Conditional Throughput

Definition:

Conditional Throughput is a value computed at the Relevant Lower Bound
according to algorithm defined in
[Appendix B: Conditional Throughput](#appendix-b-conditional-throughput).

Discussion:

The Relevant Lower Bound is defined only at the end of the search,
and so is the Conditional Throughput.
But the algorithm can be applied at any time on any Lower Bound load,
so the final Conditional Throughput value may appear sooner
than at the end of the search.

Informally, the Conditional Throughput should be
a typical Trial Forwarding Rate, expected to be seen
at the Relevant Lower Bound of the given Search Goal.

But frequently it is only a conservative estimate thereof,
as MLRsearch implementations tend to stop gathering more trials
as soon as they confirm the value cannot get worse than this estimate
within the Goal Duration Sum.

This value is RECOMMENDED to be used when evaluating repeatability
and comparability of different MLRsearch implementations.

See [Generalized Throughput](#generalized-throughput) for more details.

{::comment}
    [Low priority but useful for comparabuility.]

    <mark>[VP] TODO: Add subsection for Trial Results At Relevant Bounds
    as an optional attribute of Goal Result.</mark>

{:/comment}

### Goal Results

MLRsearch specification is based on a set of requirements
for a "regular" result. But in practice, it is not always possible
for such result instance to exist, so also "irregular" results
need to be supported.

#### Regular Goal Result

Definition:

Regular Goal Result is a composite quantity consisting of several attributes.
Relevant Upper Bound and Relevant Lower Bound are REQUIRED attributes,
Conditional Throughput is a RECOMMENDED attribute.
Stopping conditions for the corresponding Search Goal MUST be satisfied.

Discussion:

Both relevant bounds MUST exist.

If the implementation offers Goal Width as a Search Goal attribute,
the distance between the Relevant Lower Bound
and the Relevant Upper Bound MUST NOT be larger than the Goal Width,

Implementations MAY add their own attributes.

Test report MUST display Relevant Lower Value,
Displaying Relevant Upper Bound is NOT REQUIRED, but it is RECOMMENDED,
especially if the implementation does not use Goal Width.

#### Irregular Goal Result

Definition:

Irregular Goal Result is a composite quantity. No attributes are required.

Discussion:

It is RECOMMENDED to report any useful quantity even if it does not
satisfy all the requirements. For example if Max Load is classified
as a Lower Bound, it is fine to report it as the Relevant Lower Bound,
and compute Conditional Throughput for it. In this case,
only the missing Relevant Upper Bound signals this result instance is irregular.

Similarly, if both revevant bounds exist, it is RECOMMENDED
to include them as Irregular Goal Result attributes,
and let the Manager decide if their distance is too far for users' purposes.

If test report displays some Irregular Goal Result attribute values,
they MUST be clearly marked as comming from irregular results.

The implementation MAY define additional attributes.

{::comment}
    [Useful.]

    <mark>MKP2 [VP] TODO: Also allways-fail. Link to bounds to avoid duplication.</mark>

{:/comment}

#### Goal Result

Definition:

Goal Result is a composite quantity. Each instance is either a Regular Goal Result
or an Irregular Goal Result.

Discussion:

The Manager MUST be able to distinguish whether the instance is regular or not.

### Search Result

Definition:

The Search Result is a single composite object
that maps each Search Goal instance to a corresponding Goal Result instance.

Discussion:

Alternatively, the Search Result can be implemented as an ordered list
of the Goal Result instances, matching the order of Search Goal instances.

The Search Result (as a mapping)
MUST map from all the Search Goal instances present in the Controller Input.

Identical Goal Result instances MAY be listed for different Search Goals,
but their status as regular or irregular may be different.
For example if two goals differ only in Goal Width value,
and the relevant bound values are close enough according to only one of them.

{::comment}
    [Not important.]

    <mark>[VP] Postponed: API independence, modularity.</mark>

{:/comment}

### Controller Output

Definition:

The Controller Output is a composite quantity returned from the Controller
to the Manager at the end of the search.
The Search Result instance is its only REQUIRED attribute.

Discussion:

MLRsearch implementation MAY return additional data in the Controller Output,
for example number of trials performed and the total Search duration.

{::comment}

    TODO-P0: "max search time exceeded" flag?

{:/comment}

## MLRsearch Architecture

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

The Measurer is an abstract system component that when called
with a [Trial Input](#trial-input) instance, performs one [Trial ](#trial),
and returns a [Trial Output](#trial-output) instance.

Discussion:

This definition assumes the Measurer is already initialized.
In practice, there may be additional steps before the Search,
e.g. when the Manager configures the traffic profile
(either on the Measurer or on its tester sub-component directly)
and performs a warmup (if the test procedure requires one).

It is the responsibility of the Measurer implementation to uphold
any requirements and assumptions present in MLRsearch specification,
e.g. Trial Forwarding Ratio not being larger than one.

Implementers have some freedom.
For example [RFC2544] (Section 10)
gives some suggestions (but not requirements) related to
duplicated or reordered frames.
Implementations are RECOMMENDED to document their behavior
related to such freedoms in as detailed a way as possible.

It is RECOMMENDED to benchmark the test equipment first,
e.g. connect sender and receiver directly (without any SUT in the path),
find a load value that guarantees the Offered Load is not too far
from the Intended Load, and use that value as the Max Load value.
When testing the real SUT, it is RECOMMENDED to turn any big difference
between the Intended Load and the Offered Load into increased Trial Loss Ratio.

Neither of the two recommendations are made into requirements,
because it is not easy to tell when the difference is big enough,
in a way thay would be dis-entangled from other Measurer freedoms.

### Controller

Definition:

The Controller is an abstract system component
that when called once with a Controller Input instance
repeatedly computes Trial Input instance for the Measurer,
obtains corresponding Trial Output instances,
and eventually returns a Controller Output instance.

Discussion:

Informally, the Controller has big freedom in selection of Trial Inputs,
and the implementations want to achieve all the Search Goals
in the shortest expected time.

The Controller's role in optimizing the overall search time
distinguishes MLRsearch algorithms from simpler search procedures.

Informally, each implementation can have different stopping conditions.
Goal Width is only one example.
In practice, implementation details do not matter,
as long as Goal Result instances are regular.

### Manager

Definition:

The Manager is an abstract system component that is reponsible for
configuring other components, calling the Controller component once,
and for creating the test report following the reporting format as
defined in [RFC2544] (Section 26).

Discussion:

The Manager initializes the SUT, the Measurer (and the Tester if independent)
with their intended configurations before calling the Controller.

The Manager does not need to be able to tweak any Search Goal attributes,
but it MUST report all applied attribute values even if not tweaked.

In principle, there should be a "user" (human or CI)
that "starts" or "calls" the Manager and receives the report.
The Manager MAY be able to be called more than once whis way,
thus triggering multiple independent Searches.

{::comment}
    [Not important, unless anybody else asks.]

    <mark>MKP2 The Manager may use the Measurer or other system components
    to perform other tests, e.g. back-to-back frames,
    as the Controller is only replacing the search from
    [RFC2544] (Section 26.1).</mark>

{:/comment}

{::comment}

    TODO-P2: Summarize test report requirements here?

{:/comment}

## Compliance

This section discusses compliance relations between MLRsearch
and other test procedures.

### Test Procedure Compliant with MLRsearch

Any networking measurement setup where there can be logically delineated
system components and there are abstract components satisfying requirements
for the Measurer, the Controller and the Manager,
is considered to be compliant with MLRsearch specification.

These components can be seen as abstractions present in any testing procedure.
For example, there can be a single component acting both
as the Manager and the Controller, but as long as values of required attributes
of Search Goals and Goal Results are visible in the test report,
the Controller Input instance and Controller Output instance are implied.

For example, any setup for conditionally (or unconditionally)
compliant [RFC2544] throughput testing
can be understood as a MLRsearch architecture,
as long as there is enough data to reconstruct the Relevant Upper Bound.
See the next subsection for an equivalent Search Goal.

Any test procedure that can be understood as (one call to the Manager of)
MLRsearch architecture is said to be compliant with MLRsearch specification.

{::comment}

    TODO-P0: Delete occurances of "MLRsearch Implementation", review
    occurances of "MLRsearch implementation".

{:/comment}

### MLRsearch Compliant with RFC2544

The following Search Goal instance makes the corresponding Search Result
unconditionally compliant with [RFC2544] (Section 24).

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 60 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 0%

The latter two attributes, Goal Loss Ratio and Goal Exceed Ratio,
are enough to make the Search Goal conditionally compliant.
Adding the first attribute, Goal Final Trial Duration,
makes the Search Goal unconditionally compliant.

The second attribute (Goal Duration Sum) only prevents MLRsearch
from repeating zero-loss full-length trials.

The presence of other Search Goals does not affect the compliance
of this Goal Result.
The Relevant Lower Bound and the Conditional Throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

{::comment}

    TODO-P1: Move the rest into Load Classification Logic chapter.

{:/comment}

Non-zero exceed ratio is not strictly disallowed, but it could
needlessly prolong the search when low-loss short trials are present.

{::comment}

    TODO-P2: Also it would open more questions re Loss Inversion,
    but no need to say that anywhere.

{:/comment}

### MLRsearch Compliant with TST009

One of the alternatives to [RFC2544] is Binary search with loss verification
as described in [TST009] (Section 12.3.3).

The idea there is to repeat high-loss trials, hoping for zero loss on second try,
so the results are closer to the noiseless end of performance sprectum,
thus more repeatable and comparable.

Only the variant with "z = infinity" is achievable with MLRsearch.

{::comment}
    [Low priority, unless a short sentence is found.]

    <mark>MKP2 MK note: Shouldn't we add a note about how MLRsearch goes about
    addressing the TST009 point related to z, that is "z is threshold of
    Lord(r) to override Loss Verification when the count of lost frames is
    very high and unnecessary verification trials."? i.e. by have Goal Loss
    Ratio. Thoughts?</mark>

{:/comment}

For example, for "max(r) = 2" variant, the following Search Goal instance
should be used to get compatible Search Result:

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 120 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 50%

If the first 60s trial has zero loss, it is enough for MLRsearch to stop
measuring at that load, as even a second high-loss trial
would still fit within the exceed ratio.

But if the first trial is high-loss, MLRsearch needs to perform also
the second trial to classify that load.
Goal Duration Sum is twice as long as Goal Final Trial Duration,
so third full-length trial is never needed.

# Further Explanations

This chapter provides further explanations of MLRsearch behavior,
mainly in comparison to a simple bisection for [RFC2544] Throughput.

## Binary Search

A typical binary search implementation for [RFC2544]
tracks only the two tightest bounds.
To start, the search needs both Max Load and Min Load values.
Then, one trial is used to confirm Max Load is an Upper Bound,
and one trial to confirm Min Load is a Lower Bound.

Then, next Trial Load is chosen as the mean of the current tightest upper bound
and the current tightest lower bound, and becomes a new tightest bound
depending on the Trial Loss Ratio.

After some number of trials, the tightest lower bound becomes the throughput,
but [RFC2544] does not specify when, if ever, the search should stop.
In practice, the search stops either at some distance
between the tightest upper bound and the tightest lower bound,
or after some number of Trials.

For a given pair of Max Load and Min Load values,
there is one-to-one correspondence between number of Trials
and final distance between the tightest bounds.
Thus, the search always takes the same time,
assuming initial bounds are confirmed.

## Stopping Conditions and Precision

MLRsearch specification requires listing both Relevant Bounds for each
Search Goal, and the difference between the bounds implies
whether the result precision achieved.
Therefore it is not necessary to report the specific stopping condition used.

MLRsearch implementations may use Goal Width
to allow direct control of result precision,
and indirect control of the search duration.

Other MLRsearch implementations may use different stopping conditions;
for example based on the search duration, trading off precision control
for duration control.

Due to various possible time optimizations, there is no longer a strict
correspondence between the overall search duration and Goal Width values.
In practice, noisy SUT performance increases both average search time
and its variance.

## Loss Ratios and Loss Inversion

The most obvious difference between MLRsearch and [RFC2544] binary search
is in the goals of the search.
[RFC2544] has a single goal, based on classifying a single full-length trial
as either zero-loss or non-zero-loss.
MLRsearch supports searching for multiple goals at once,
usually differing in their Goal Loss Ratio values.

### Single Goal and Hard Bounds

Each bound in [RFC2544] simple binary search is "hard",
in the sense that all further Trial Load values
are smaller than any current upper bound and larger than any current lower bound.

This is also possible for MLRsearch implementations,
when the search is started with only one Search Goal instance.

### Multiple Goals and Loss Inversion

MLRsearch supports multiple goals, making the search procedure
more complicated compared to binary search with single goal,
but most of the complications do not affect the final results much.
Except for one phenomenon: Loss Inversion.

Depending on Search Goal attributes, Load Classification results may be resistant
to small amounts of [Inconsistent Trial Results](#inconsistent-trial-results).
But for larger amounts, a Load that is classified
as an Upper Bound for one Search Goal
may still be a Lower Bound for another Search Goal.
And, due to this other goal, MLRsearch will probably perform subsequent Trials
at Trial Loads even higher than the original value.

{::comment}

    TODO-P2: Unify load adjectives: higher/lower xor larger/smaller. => higher/lower.

{:/comment}

This introduces questions any many-goals search algorithm has to address.
What to do when all such higher load trials happen to have zero loss?
Does it mean the earlier upper bound was not real?
Does it mean the later low-loss trials are not considered a lower bound?

The situation where a smaller load is classified as an Upper Bound,
while a larger load is classified as a Lower Bound (for the same search goal),
is called Loss Inversion.

Conversely, only single-goal search algorithms can have hard bounds
that shield them from Loss Inversion.

### Conservativeness and Relevant Bounds

MLRsearch is conservative when dealing with Loss Inversion:
the Upper Bound is considered real, and the Lower Bound
is considered to be a fluke, at least when computing the final result.

This is formalized using definitions of
[Relevant Upper Bound](#relevant-upper-bound) and
[Relevant Lower Bound](#relevant-lower-bound).
The Relevant Upper Bound (for specific goal) is the smallest load classified
as an Upper Bound. But the Relevant Lower Bound is not simply
the largest among Lower Bounds. It is the largest load among loads
that are Lower Bounds while also being smaller than the Relevant Upper Bound.

With these definitions, the Relevant Lower Bound is always smaller
than the Relevant Upper Bound (if both exist), and the two relevant bounds
are used analogously as the two tightest bounds in the binary search.
When they meet the stopping conditions, the Relevant Bounds are used in the output.

### Consequences

The consequence of the way the Relevant Bounds are defined is that
every Trial Result can have an impact
on any current Relevant Bound larger than that Trial Load,
namely by becoming a new Upper Bound.

This also applies when that trial happens
before that bound could have become current.

This means if your SUT (or your Traffic Generator) needs a warmup,
be sure to warm it up before starting the Search.

Also, for MLRsearch implementation, it means it is better to measure
at smaller loads first, so bounds found earlier are less likely
to get invalidated later.

## Exceed Ratio and Multiple Trials

The idea of performing multiple Trials at the same Trial Load comes from
a model where some Trial Results (those with high Trial Loss Ratio) are affected
by infrequent effects, causing poor repeatability of [RFC2544] Throughput results.
See the discussion about noiseful and noiseless ends
of the SUT performance spectrum in section [DUT in SUT](#dut-in-sut).
Stable results are closer to the noiseless end of the SUT performance spectrum,
so MLRsearch may need to allow some frequency of high-loss trials
to ignore the rare but big effects near the noiseful end.

For MLRsearch to perform such Trial Result filtering, it needs
a configuration option to tell how frequent can the "infrequent" big loss be.
This option is called the [Goal Exceed Ratio](#goal-exceed-ratio).
It tells MLRsearch what ratio of trials (more specifically,
what ratio of Trial Effective Duration seconds)
can have a [Trial Loss Ratio](#trial-loss-ratio)
larger than the [Goal Loss Ratio](#goal-loss-ratio)
and still be classified as a [Lower Bound](#lower-bound).

Zero exceed ratio means all trials must have a Trial Loss Ratio
equal to or smaller than the Goal Loss Ratio.

When more than one trial is intended to classify a Load,
MLRsearch also needs something that controls the number of trials needed.
Therefore, each goal also has an attribute called Goal Duration Sum.

The meaning of a [Goal Duration Sum](#goal-duration-sum) is that
when a load has (full-length) trials
whose Trial Effective Durations when summed up give a value at least as big
as the Goal Duration Sum value,
the load is guaranteed to be classified either as an Upper Bound
or a Lower Bound for that Search Goal instance.

{::comment}

    TODO-P2: Move some discussion on Trial Effective Duration from spec chapter
    to around here? Probably no time to dwell on this, delete the todo.
    TODO2: my pref is to keep it in spec section

{:/comment}

## Short Trials and Duration Selection

MLRsearch requires each goal to specify its Goal Final Trial Duration.

Section 24 of [RFC2544] already anticipates possible time savings
when Short Trials are used.

Any MLRsearch implementation MAY include its own configuration options
which control when and how MLRsearch chooses to use short trial durations.

While MLRsearch implementations are free to use any logic to select
Trial Input values, comparability between MLRsearch implementations
is only assured when the Load Classification logic
handles any possible set of Trial Results in the same way.

The presence of short trial results complicates
the load classification logic, see details in
[Load Classification Logic](#load-classification-logic) chapter.

While the Load Classification algorithm is designed to avoid any unneeded Trials,
for explainability reasons it is RECOMMENDED for users to use
such Controller Input instances that lead to all Trial Duration values
selected by Controller to be the same,
e.g. by setting any Goal Initial Trial Duration to be a single value
also used in all Goal Final Trial Duration attributes.

{::comment}

    TODO-P0: last statement is confusing. it implies GITD = GFTD, which doesn't make sense to me.

    TODO-P0: below to be removed once Load Classification Logic is done.

{:/comment}

In a nutshell, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the Relevant Lower Bound,
below what would classification say when considering full-length trials only.

{::comment}
    [Important. Keeping compatibility slows search considerably.]

    <mark>Alas, such configurations are usually not compliant with [RFC2544] requirements,
    or not time-saving enough.</mark>
    
    <mark>mk edit note: This statement does not make sense to me. Suggest to remove it.</mark>

{:/comment}

## Generalized Throughput

Due to the fact that testing equipment takes the Intended Load
as an input parameter for a trial measurement,
any load search algorithm needs to deal with Intended Load values internally.

But in the presence of goals with a non-zero [Goal Loss Ratio](#goal-loss-ratio),
the Intended Load usually does not match
the user's intuition of what a throughput is.
The forwarding rate (as defined in [RFC2285] section 3.6.1) is better,
but it is not obvious how to generalize it
for loads with multiple trials and a non-zero goal loss ratio.

The best example is also the main motivation: hard performance limit.

### Hard Performance Limit

Even if bandwidth of the medium allows higher performance,
the SUT interfaces may have their additional own limitations,
e.g. a specific frames-per-second limit on the NIC (a common occurance).

Ideally, those should be known and provided as [Max Load](#max-load).
But if Max Load is set higher than what the interface can receive or transmit,
there will be a "hard limit" observed in trial results.

Imagine the hard limit is at hundred million frames per second (100 Mfps),
Max Load is higher, and the goal loss ratio is 0.5%.
If DUT has no additional losses, 0.5% loss ratio will be achieved
at Relevant Lower Bound of 100.5025 Mfps.
But it is not intuitive to report SUT performance as a value that is
larger than the known hard limit.
We need a generalization of RFC2544 throughput,
different from just the Relevant Lower Bound.

MLRsearch defines one such generalization,
the [Conditional Throughput](#conditional-throughput).
It is the Trial Forwarding Rate from one of the full-length trials
performed at the Relevant Lower Bound.
The algorithm to determine which trial exactly is in
[Appendix B: Conditional Throughput](#appendix-b-conditional-throughput).

In the hard limit example, 100.5025 Mfps load will still have
only 100.0 Mfps forwarding rate, nicely confirming the known limitation.

### Performance Variability

With non-zero Goal Loss Ratio, and without hard performance limits,
low-loss trials at the same Load may achieve different Trial Forwarding Rate
values just due to DUT performance variability.

By comparing the best case (all Relevant Lower Bound trials have zero loss)
and the worst case (all Trial Loss Ratios at Relevant Lower Bound
are equal to the Goal Loss Ratio), we find the possible Conditional Throughput
values may have up to the Goal Loss Ratio relative difference.

Therefore, it is rarely needed to set the Goal Width (if expressed
as the relative difference of loads) below the Goal Loss Ratio.
In other words, setting the Goal Width below the Goal Loss Ratio
may cause the Conditional Throughput for a larger loss ratio to become smaller
than a Conditional Throughput for a goal with a smaller Goal Loss Ratio,
which is counter-intuitive, considering they come from the same search.
Therefore it is RECOMMENDED to set the Goal Width to a value no smaller
than the Goal Loss Ratio.

Despite this variability, in practice Conditional Throughput behaves better
than Relevant Lower Bound for comparability purposes.

{::comment}

    TODO-P0: Move the rest into the last chapter.

{:/comment}

Conditional Throughput is partially related to load classification.
If a load is classified as a Relevant Lower Bound for a goal,
the Conditional Throughput comes from a trial result,
that is guaranteed to have Trial Loss Ratio no larger than the Goal Loss Ratio.

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

# MLRsearch Logic and Example

This section uses informal language to describe two pieces of MLRsearch logic,
Load Classification and Conditional Throughput,
reflecting formal pseudocode representation present in
[Appendix A: Load Classification](#appendix-a-load-classification)
and [Appendix B: Conditional Throughput](#appendix-b-conditional-throughput).
This is followed by example search.

{::comment}

    TODO-P1: Move this paragraph to a better place.
    TODO-P1: This is an answer to the questions of "why are algorithms this strict"?
    TODO-P1: Pose that question somewhere, pose this answer there or in another place.

{:/comment}

For repeatability and comparability reasons, it is important that
all implementations of MLRsearch classify the load equivalently,
based on all trials measured at the given load.

## Load Classification Logic

Note: For explanation clarity variables are taged as (I)nput,
(T)emporary, (O)utput.

- Take all Trial Result instances (I) measured at a given load.

- Full-length high-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length high-loss trials (I).
- Full-length low-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length low-loss trials (I).
- Short high-loss sum is the sum (T)  of Trial Effective Duration values
  of all short high-loss trials (I).
- Short low-loss sum is the sum (T) of Trial Effective Duration values
  of all short low-loss trials (I).

- Subceed ratio (T) is One minus the Goal Exceed Ratio (I).
- Exceed coefficient (T) is the Goal Exceed Ratio divided by the subceed
  ratio.

- Balancing sum (T) is the short low-loss sum
  multiplied by the exceed coefficient.
- Excess sum (T) is the short high-loss sum minus the balancing sum.
- Positive excess sum (T) is the maximum of zero and excess sum.
- Effective high-loss sum (T) is the full-length high-loss sum
  plus the positive excess sum.
- Effective full sum (T) is the effective high-loss sum
  plus the full-length low-loss  sum.
- Effective whole sum (T) is the larger of the effective full sum
  and the Goal Duration Sum.
- Missing sum (T) is the effective whole sum minus the effective full sum.

- Pessimistic high-loss sum (T) is the effective high-loss sum
  plus the missing sum.
- Optimistic exceed ratio (T) is the effective high-loss sum
  divided by the effective whole sum.
- Pessimistic exceed ratio (T) is the pessimistic high-loss sum
  divided by the effective whole sum.

- The load is classified as an Upper Bound (O) if the optimistic exceed
  ratio is larger than the Goal Exceed Ratio.
- The load is classified as a Lower Bound (O) if the pessimistic exceed
  ratio is not larger than the Goal Exceed Ratio.
- The load is classified as undecided (O) otherwise.

## Conditional Throughput Logic

Note: For explanation clarity variables are taged as (I)nput,
(T)emporary, (O)utput.

- Take all Trial Result instances (I) measured at a given Load.

- Full-length high-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length high-loss trials (I).
- Full-length low-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length low-loss trials (I).
- Full-length sum (T) is the full-length high-loss sum (I) plus the
  full-length low-loss sum (I).

- Subceed ratio (T) is One minus the Goal Exceed Ratio (I) is called.
- Remaining sum (T) initially is full-lengths sum multiplied by subceed
  ratio.
- Current loss ratio (T) initially is 100%.

- For each full-length trial result, sorted in increasing order by Trial
  Loss Ratio:
  - If remaining sum is not larger than zero, exit the loop.
  - Set current loss ratio to this trial's Trial Loss Ratio (I).
  - Decrease the remaining sum by this trial's Trial Effective
    Duration (I).

- Current forwarding ratio (T) is One minus the current loss ratio.
- Conditional Throughput (T) is the current forwarding ratio multiplied
  by the Load value.

{::comment}
    TODO-P0: Move somewhere else? MK: I think it's okay to leave it here.
{:/comment}

By definition, Conditional Throughput logic results in a value
that represents Trial Loss Ratio at most equal to Goal Loss Ratio.

## SUT Behaviors

In [DUT in SUT](#dut-in-sut), the notion of noise has been introduced.
In this section we rely on new terms defined since then
to describe possible SUT behaviors more precisely.

From measurement point of view, noise is visible as inconsistent trial results.
See [Inconsistent Trial Results](#inconsistent-trial-results) for general points
and [Loss Ratios and Loss Inversion](#loss-ratios-and-loss-inversion)
for specifics when comparing different Load values.

Load Classification and Conditional Throughput apply to a single Load value,
but even the set of Trial Results measured at that Trial Load value
may appear inconsistent.

As MLRsearch aims to save time, it executes only a small number of Trials,
getting only a limited amount of information about SUT behavior.
It is useful to introduce an "SUT expert" point of view to contrast
with that limited information.

### Expert Predictions

Imagine that before the Search starts, a human expert had unlimited time
to measure SUT and obtain all reliable information about it.
The information is not perfect, as there is still random noise influencing SUT.
But the expert is familiar with possible noise events, even the rare ones,
and thus the expert can do probabilistic predictions about future Trial Outputs.

When several outcomes are possible,
the expert can asses probability of each outcome.

### Exceed Probability

When the Controller selects new Trial Duration and Trial Load,
and just before the Measurer starts performing the Trial,
the SUT expert can envision possible Trial Results.

With respect to a particular Search Goal instance, the possibilities
can be summarized into a single number: Exceed Probability.
It is the probability (according to the expert) that the measured
Trial Loss Ratio will be higher than the Goal Loss Ratio.

{::comment}

    TODO-P2: Do we need to say small EP means low load?

    TODO-P3: Mention how ER relates to EP here?

    TODO-P2: Tie to Relevant Lower Bound and Conditional Throughput somewhere.

{:/comment}

### Trial Duration Dependence

When comparing Exceed Probability values for the same Trial Load value
but different Trial Duration values,
there are several patterns that commonly occur in practice.

#### Strong Increase

Exceed Probability is very small at short durations but very high at full-length.
This SUT behavior is undesirable, and may hint at faulty SUT,
e.g. SUT leaks resources and is unable to sustain the desired performance.

But this behavior is also seen when SUT uses large amount of buffers.
This is the main reasons users may want to set high Goal Final Trial Duration.

#### Mild Increase

Short trials have smaller exceed probability, but the difference is not as high.
This behavior is quite common if the noise contains infrequent but large
loss spikes, as the more performant parts of a full-length trial
are unable to compensate for all the frame loss from a less performant part.

#### Independence

Short trials have basically the same Exceed Probability as full-length trials.
This is possible only if loss spikes are small (so other parts can compensate)
and if Goal Loss Ratio is more than zero (otherwise other parts
cannot compensate at all).

#### Decrease

Short trials have larger Exceed Probability than full-length trials.
This can be possible only for non-zero Goal Loss Ratio,
for example if SUT needs to "warm up" to best performance within each trial.
Not sommonly seen in practice.

{::comment}

    TODO-P2: Define loss spikes? Mention loss spikes when discussing noise?

{:/comment}

{::comment}

    ### Loss Spikes
    
    #### Frequent Small Loss Spikes
    
    #### Rare Big Loss Spikes

{:/comment}

## Example Search

The following example Search is related to
one hypothetical run of a Search test procedure
that has been started with multiple Search Goals.
Several points in time are chosen, in order to show how the logic works,
with specific sets of Trial Result available.
The trial results themselves are not very realistic, as
the intention is to show several corner cases of the logic.

In all Trials, the Effective Trial Duration is equal to Trial Duration.

Only one Trial Load is in focus, its value is one million frames per second.
Trial Results at other Trial Loads are not mentioned,
as the parts of logic present here do not depend on those.
In practice, Trial Results at other Load values would be present,
e.g. MLRsearch will look for a Lower Bound smaller than any Upper Bound found.

In all points in time, only one Search Goal instance is marked as "in focus".
That explains Trial Duration of the new Trials,
but is otherwise unrelated to the logic applied.

MLRsearch implementations are not required to "focus" on one goal at time,
but this example is useful to show a load can be classified
also for goals not "in focus".

### Example Goals

The following four Search Goal instances are selected for the example Search.
Each goal has a readable name and dense code,
the code is useful to show Search Goal attribute values.

As the variable "exceed coefficient" does not depend on trial results,
it is also precomputed here.

Goal 1:

    name: RFC2544
    Goal Final Trial Duration: 60s
    Goal Duration Sum: 60s
    Goal Loss Ratio: 0%
    Goal Exceed Ratio: 0%
    exceed coefficient: 0% / (100% / 0%) = 0.0
    code: 60f60d0l0e

Goal 2:

    name: TST009
    Goal Final Trial Duration: 60s
    Goal Duration Sum: 120s
    Goal Loss Ratio: 0%
    Goal Exceed Ratio: 50%
    exceed coefficient: 50% / (100% - 50%) = 1.0
    code: 60f120d0l50e

Goal 3:

    name: 1s final
    Goal Final Trial Duration: 1s
    Goal Duration Sum: 120s
    Goal Loss Ratio: 0.5%
    Goal Exceed Ratio: 50%
    exceed coefficient: 50% / (100% - 50%) = 1.0
    code: 1f120d.5l50e

Goal 4:

    name: 20% exceed
    Goal Final Trial Duration: 60s
    Goal Duration Sum: 60s
    Goal Loss Ratio: 0.5%
    Goal Exceed Ratio: 20%
    exceed coefficient: 20% / (100% - 20%) = 0.25
    code: 60f60d0.5l20e

The first two goals are important for compliance reasons,
the other two cover less frequent cases.

### Example Trial Results

{::comment}

    TODO-P1: Merge this with Point computations so all trial data is localized.

{:/comment}

The following six sets of trial results are selected for the example Search.
The sets are defined as points in time, describing which Trial Results
were added since the previous point.

Each point has a readable name and dense code,
the code is useful to show Trial Output attribute values
and number of times identical results were added.

Point 1:

    name: first short good
    goal in focus: 1s final (1f120d.5l50e)
    added Trial Results: 59 trials, each 1 second and 0% loss
    code: 59x1s0l

Point 2:

    name: first short bad
    goal in focus: 1s final (1f120d.5l50e)
    added Trial Result: one trial, 1 second, 1% loss
    code: 59x1s0l+1x1s1l

Point 3:

    name: last short bad
    goal in focus: 1s final (1f120d.5l50e)
    added Trial Results: 59 trials, 1 second each, 1% loss each
    code: 59x1s0l+60x1s1l

Point 4:

    name: last short good
    goal in focus: 1s final (1f120d.5l50e)
    added Trial Results: one trial 1 second, 0% loss
    code: 60x1s0l+60x1s1l

Point 5:

    name: first long bad
    goal in focus: TST009 (60f120d0l50e)
    added Trial Results: one trial, 60 seconds, 0.1% loss
    code: 60x1s0l+60x1s1l+1x60s.1l

Point 6:

    name: first long good
    goal in focus: TST009 (60f120d0l50e)
    added Trial Results: one trial, 60 seconds, 0% loss
    code: 60x1s0l+60x1s1l+1x60s.1l+1x60s0l

Comments on point in time naming:

- When a name contains "short", it means the added trial
  had Trial Duration of 1 second, which is Short Trial for 3 of the Search Goals,
  but it is a Full-Length Trial for the "1s final" goal.

- Similarly, "long" in name means the added trial
  had Trial Duration of 60 seconds, which is Full-Length Trial for 3 goals
  but Long Trial for the "1s final" goal.

- When a name contains "good" it means the added trial is Low-Loss Trial
  for all the goals.

- When a name contains "short bad" it means the added trial is High-Loss Trial
  for all the goals.

- When a name contains "long bad", it means the added trial
  is a High-Loss Trial for goals "RFC2544" and "TST009",
  but it is a Low-Loss Trial for the two other goals.

### Load Classification Computations

This section shows how Load Classification logic is applied
by listing all temporary values at the specific time point.

#### Point 1

This is the "first short good" point.
Code for available results is: 59x1s0l

Goal name                 | RFC2544     | TST009       | 1s final     | 20% exceed
--------------------------|-------------|--------------|--------------|--------------
Goal code                 | 60f60d0l0e  | 60f120d0l50e | 1f120d.5l50e | 60f60d0.5l20e
Full-length high-loss sum | 0s          | 0s           | 0s           | 0s
Full-length low-loss sum  | 0s          | 0s           | 59s          | 0s
Short high-loss sum       | 0s          | 0s           | 0s           | 0s
Short low-loss sum        | 59s         | 59s          | 0s           | 59s
Balancing sum             | 0s          | 59s          | 0s           | 14.75s
Excess sum                | 0s          | -59s         | 0s           | -14.75s
Positive excess sum       | 0s          | 0s           | 0s           | 0s
Effective high-loss sum   | 0s          | 0s           | 0s           | 0s
Effective full sum        | 0s          | 0s           | 59s          | 0s
Effective whole sum       | 60s         | 120s         | 120s         | 60s
Missing sum               | 60s         | 120s         | 61s          | 60s
Pessimistic high-loss sum | 60s         | 120s         | 61s          | 60s
Optimistic exceed ratio   | 0%          | 0%           | 0%           | 0%
Pessimistic exceed ratio  | 100%        | 100%         | 50.833%      | 100%
Classification Result     | Undecided   | Undecided    | Undecided    | Undecided

This is the last point in time where all goals have this load as Undecided.

#### Point 2

This is the "first short bad" point.
Code for available results is: 59x1s0l+1x1s1l

Goal name                 | RFC2544     | TST009       | 1s final     | 20% exceed
--------------------------|-------------|--------------|--------------|--------------
Goal code                 | 60f60d0l0e  | 60f120d0l50e | 1f120d.5l50e | 60f60d0.5l20e
Full-length high-loss sum | 0s          | 0s           | 1s           | 0s
Full-length low-loss sum  | 0s          | 0s           | 59s          | 0s
Short high-loss sum       | 1s          | 1s           | 0s           | 1s
Short low-loss sum        | 59s         | 59s          | 0s           | 59s
Balancing sum             | 0s          | 59s          | 0s           | 14.75s
Excess sum                | 1s          | -58s         | 0s           | -13.75s
Positive excess sum       | 1s          | 0s           | 0s           | 0s
Effective high-loss sum   | 1s          | 0s           | 1s           | 0s
Effective full sum        | 1s          | 0s           | 60s          | 0s
Effective whole sum       | 60s         | 120s         | 120s         | 60s
Missing sum               | 59s         | 120s         | 60s          | 60s
Pessimistic high-loss sum | 60s         | 120s         | 61s          | 60s
Optimistic exceed ratio   | 1.667%      | 0%           | 0.833%       | 0%
Pessimistic exceed ratio  | 100%        | 100%         | 50.833%      | 100%
Classification Result     | Upper Bound | Undecided    | Undecided    | Undecided

Due to zero Goal Loss Ratio, RFC2544 goal must have mild or strong increase
of exceed probability, so the one lossy trial would be lossy even if measured
at 60 second duration.
Due to zero exceed ratio, one High-Loss Trial is enough to preclude this Load
from becoming a Lower Bound for RFC2544. That is why this Load
is classified as an Upper Bound for RFC2544 this early.

This is an example how significant time can be saved, compared to 60-second trials.

#### Point 3

This is the "last short bad" point.
Code for available trial results is: 59x1s0l+60x1s1l

Goal name                 | RFC2544     | TST009       | 1s final     | 20% exceed
--------------------------|-------------|--------------|--------------|--------------
Goal code                 | 60f60d0l0e  | 60f120d0l50e | 1f120d.5l50e | 60f60d0.5l20e
Full-length high-loss sum | 0s          | 0s           | 60s          | 0s
Full-length low-loss sum  | 0s          | 0s           | 59s          | 0s
Short high-loss sum       | 60s         | 60s          | 0s           | 60s
Short low-loss sum        | 59s         | 59s          | 0s           | 59s
Balancing sum             | 0s          | 59s          | 0s           | 14.75s
Excess sum                | 60s         | 1s           | 0s           | 45.25s
Positive excess sum       | 60s         | 1s           | 0s           | 45.25s
Effective high-loss sum   | 60s         | 1s           | 60s          | 45.25s
Effective full sum        | 60s         | 1s           | 119s         | 45.25s
Effective whole sum       | 60s         | 120s         | 120s         | 60s
Missing sum               | 0s          | 119s         | 1s           | 14.75s
Pessimistic high-loss sum | 60s         | 120s         | 61s          | 60s
Optimistic exceed ratio   | 100%        | 0.833%       | 50%          | 75.417%
Pessimistic exceed ratio  | 100%        | 100%         | 50.833%      | 100%
Classification Result     | Upper Bound | Undecided    | Undecided    | Upper Bound

This is the last point for "1s final" goal to have this Load still Undecided.
Only one 1-second trial is missing within the 120-second Goal Duration Sum,
but its result will decide the classification result.

The "20% exceed" started to classify this load as an Upper Bound
somewhere between points 2 and 3.

#### Point 4

This is the "last short good" point.
Code for available trial results is: 60x1s0l+60x1s1l

Goal name                 | RFC2544     | TST009       | 1s final     | 20% exceed
--------------------------|-------------|--------------|--------------|--------------
Goal code                 | 60f60d0l0e  | 60f120d0l50e | 1f120d.5l50e | 60f60d0.5l20e
Full-length high-loss sum | 0s          | 0s           | 60s          | 0s
Full-length low-loss sum  | 0s          | 0s           | 60s          | 0s
Short high-loss sum       | 60s         | 60s          | 0s           | 60s
Short low-loss sum        | 60s         | 60s          | 0s           | 60s
Balancing sum             | 0s          | 60s          | 0s           | 15s
Excess sum                | 60s         | 0s           | 0s           | 45s
Positive excess sum       | 60s         | 0s           | 0s           | 45s
Effective high-loss sum   | 60s         | 0s           | 60s          | 45s
Effective full sum        | 60s         | 0s           | 120s         | 45s
Effective whole sum       | 60s         | 120s         | 120s         | 60s
Missing sum               | 0s          | 120s         | 0s           | 15s
Pessimistic high-loss sum | 60s         | 120s         | 60s          | 60s
Optimistic exceed ratio   | 100%        | 0%           | 50%          | 75%
Pessimistic exceed ratio  | 100%        | 100%         | 50%          | 100%
Classification Result     | Upper Bound | Undecided    | Lower Bound  | Upper Bound

The one missing trial for "1s final" was low-loss,
half of trial results are low-loss which exactly matches 50% exceed ratio.
This shows time savings are not guaranteed.

#### Point 5

This is the "first long bad" point.
Code for available trial results is: 60x1s0l+60x1s1l+1x60s.1l

Goal name                 | RFC2544     | TST009       | 1s final     | 20% exceed
--------------------------|-------------|--------------|--------------|--------------
Goal code                 | 60f60d0l0e  | 60f120d0l50e | 1f120d.5l50e | 60f60d0.5l20e
Full-length high-loss sum | 60s         | 60s          | 60s          | 0s
Full-length low-loss sum  | 0s          | 0s           | 120s         | 60s
Short high-loss sum       | 60s         | 60s          | 0s           | 60s
Short low-loss sum        | 60s         | 60s          | 0s           | 60s
Balancing sum             | 0s          | 60s          | 0s           | 15s
Excess sum                | 60s         | 0s           | 0s           | 45s
Positive excess sum       | 60s         | 0s           | 0s           | 45s
Effective high-loss sum   | 120s        | 60s          | 60s          | 45s
Effective full sum        | 120s        | 60s          | 180s         | 105s
Effective whole sum       | 120s        | 120s         | 180s         | 105s
Missing sum               | 0s          | 60s          | 0s           | 0s
Pessimistic high-loss sum | 120s        | 120s         | 60s          | 45s
Optimistic exceed ratio   | 100%        | 50%          | 33.333%      | 42.857%
Pessimistic exceed ratio  | 100%        | 100%         | 33.333%      | 42.857%
Classification Result     | Upper Bound | Undecided    | Lower Bound  | Lower Bound

As designed for TST009 goal, one Full-Length High-Loss Trial can be tolerated.
120s worth of 1-second trials is not useful, as this is allowed when
Exceed Probability does not depend on Trial Duration.
As Goal Loss Ratio is zero, it is not really possible for 60-second trials
to compensate for losses seen in 1-second results.
But Load Classification logic does not have that knowledge hardcoded,
so optimistic exceed ratio is still only 50%.

But the 0.1% Trial Loss Ratio is smaller than "20% exceed" Goal Loss Ratio,
so this unexpected Full-Length Low-Loss trial changed the classification result
of this Load to Lower Bound.

#### Point 6

This is the "first long good" point.
Code for available trial results is: 60x1s0l+60x1s1l+1x60s.1l+1x60s0l

Goal name                 | RFC2544     | TST009       | 1s final     | 20% exceed
--------------------------|-------------|--------------|--------------|--------------
Goal code                 | 60f60d0l0e  | 60f120d0l50e | 1f120d.5l50e | 60f60d0.5l20e
Full-length high-loss sum | 60s         | 60s          | 60s          | 0s
Full-length low-loss sum  | 60s         | 60s          | 180s         | 120s
Short high-loss sum       | 60s         | 60s          | 0s           | 60s
Short low-loss sum        | 60s         | 60s          | 0s           | 60s
Balancing sum             | 0s          | 60s          | 0s           | 15s
Excess sum                | 60s         | 0s           | 0s           | 45s
Positive excess sum       | 60s         | 0s           | 0s           | 45s
Effective high-loss sum   | 120s        | 60s          | 60s          | 45s
Effective full sum        | 180s        | 120s         | 240s         | 165s
Effective whole sum       | 180s        | 120s         | 240s         | 165s
Missing sum               | 0s          | 0s           | 0s           | 0s
Pessimistic high-loss sum | 120s        | 60s          | 60s          | 45s
Optimistic exceed ratio   | 66.667%     | 50%          | 25%          | 27.273%
Pessimistic exceed ratio  | 66.667%     | 50%          | 25%          | 27.273%
Classification Result     | Upper Bound | Lower Bound  | Lower Bound  | Lower Bound

This is the Low-Loss Trial the "TST009" goal was waiting for.
This Load is now classified for all goals, the search may end.
Or, more realistically, it can focus on higher load only,
as the three goals will want an Upper Bound (unless this Load is Max Load).

### Conditional Throughput Computations

At the end of the hypothetical search, "RFC2544" goal has this load
classified as an Upper Bound, so it is not eligible for Conditional Throughput
calculations. But the remaining three goals calssify this Load as a Lower Bound,
and if we assume it has also became the Relevant Lower Bound,
we can compute Conditional Throughput values for all three goals.

As a reminder, the Load value is one million frames per second.

#### Goal 2

The Conditional Throughput is computed from sorted list
of Full-Length Trial results. As TST009 Goal Final Trial Duration is 60 seconds,
only two of 122 Trials are considered Full-Length Trials.
One has Trial Loss Ratio of 0%, the other of 0.1%.

- Full-length high-loss sum is 60 seconds.
- Full-length low-loss sum is 60 seconds.
- Full-length is 120 seconds.
- Subceed ratio is 50%.
- Remaining sum initially is 0.5x12s = 60 seconds.
- Current loss ratio initially is 100%.

- For first result (duration 60s, loss 0%):
  - Remaining sum is larger than zero, not exiting the loop.
  - Set current loss ratio to this trial's Trial Loss Ratio which is 0%.
  - Decrease the remaining sum by this trial's Trial Effective Duration.
  - New remaining sum is 60s - 60s = 0s.
- For second result (duration 60s, loss 0.1%):
 - Remaining sum is not larger than zero, exiting the loop.
- Current forwarding ratio was most recently set to 0%.

- Current forwarding ratio is one minus the current loss ratio, so 100%.
- Conditional Throughput is the current forwarding ratio multiplied by the Load value.
- Conditional Throughput is one million frames per second.

#### Goal 3

The "1s final" has Goal Final Trial Duration of 1 second,
so all 122 Trial Results are considered Full-Length Trials.
They are ordered like this:

    60 1-second 0% loss trials,
    1 60-second 0% loss trial,
    1 60-second 0.1% loss trial,
    60 1-second 1% loss trials.

The result does not depend on the order of 0% loss trials.

- Full-length high-loss sum is 60 seconds.
- Full-length low-loss sum is 180 seconds.
- Full-length is 240 seconds.
- Subceed ratio is 50%.
- Remaining sum initially is 0.5x240s = 120 seconds.
- Current loss ratio initially is 100%.

- For first 61 results (duration varies, loss 0%):
  - Remaining sum is larger than zero, not exiting the loop.
  - Set current loss ratio to this trial's Trial Loss Ratio which is 0%.
  - Decrease the remaining sum by this trial's Trial Effective Duration.
  - New remaining sum varies.
- After 61 trials, we have subtracted 60x1s + 1x60s from 120s, remaining 0s.
- For 62-th result (duration 60s, loss 0.1%):
  - Remaining sum is not larger than zero, exiting the loop.
- Current forwarding ratio was most recently set to 0%.

- Current forwarding ratio is one minus the current loss ratio, so 100%.
- Conditional Throughput is the current forwarding ratio multiplied by the Load value.
- Conditional Throughput is one million frames per second.

#### Goal 4

The Conditional Throughput is computed from sorted list
of Full-Length Trial results. As "20% exceed" Goal Final Trial Duration
is 60 seconds, only two of 122 Trials are considered Full-Length Trials.
One has Trial Loss Ratio of 0%, the other of 0.1%.

- Full-length high-loss sum is 60 seconds.
- Full-length low-loss sum is 60 seconds.
- Full-length is 120 seconds.
- Subceed ratio is 80%.
- Remaining sum initially is 0.8x120s = 96 seconds.
- Current loss ratio initially is 100%.

- For first result (duration 60s, loss 0%):
  - Remaining sum is larger than zero, not exiting the loop.
  - Set current loss ratio to this trial's Trial Loss Ratio which is 0%.
  - Decrease the remaining sum by this trial's Trial Effective Duration.
  - New remaining sum is 96s - 60s = 36s.
- For second result (duration 60s, loss 0.1%):
  - Remaining sum is larger than zero, not exiting the loop.
  - Set current loss ratio to this trial's Trial Loss Ratio which is 0.1%.
  - Decrease the remaining sum by this trial's Trial Effective Duration.
  - New remaining sum is 36s - 60s = -24s.
- No more trials (and also remaining sum is not larger than zero), exiting loop.
- Current forwarding ratio was most recently set to 0.1%.

- Current forwarding ratio is one minus the current loss ratio, so 99.9%.
- Conditional Throughput is the current forwarding ratio multiplied by the Load value.
- Conditional Throughput is 999 thousand frames per second.

Due to stricter Goal Exceed Ratio, this Conditional Throughput
is smaller than Conditional Throughput of the other two goals.

{::comment}

    TODO-P2: Example of long trial being too strict?
    
    TODO-P2: Unless a set of Search Goals is recommended, comparability is not there.
    
    TODO-P2: Spell out how MLRsearch addressed the Problems.

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

Special wholehearted gratitude and thanks to the late Al Morton for his
thorough reviews filled with very specific feedback and constructive
guidelines. Thank you Al for the close collaboration over the years,
for your continuous unwavering encouragement full of empathy and
positive attitude. Al, you are dearly missed.

Many thanks to Alec Hothan of the OPNFV NFVbench project for thorough
review and numerous useful comments and suggestions in the earlier versions of this document.

Some phrases and statements in this document were created
with help of Mistral AI (mistral.ai).

# Appendix A: Load Classification

This section specifies how to perform the load classification.

Any Trial Load value can be classified,
according to a given [Search Goal](#search-goal).

The algorithm uses (some subsets of) the set of all available trial results
from trials measured at a given intended load at the end of the search.
All durations are those returned by the Measurer.

The block at the end of this appendix holds pseudocode
which computes two values, stored in variables named
`optimistic_is_lower` and `pessimistic_is_lower`.

{::comment}
    [We have other section re optimistic. Not going to talk about variable naming here.]

    <mark>MKP2 mk edit note: Need to add the description of what
    the `optimistic` and `pessimistic` variables represent.
    Or a reference to where this is described
    e.g. in [Single Trial Duration](#single-trial-duration) section.</mark>

{:/comment}

The pseudocode happens to be valid Python code.

If values of both variables are computed to be true, the load in question
is classified as a lower bound according to the given Search Goal.
If values of both variables are false, the load is classified as an upper bound.
Otherwise, the load is classified as undecided.

The pseudocode expects the following variables to hold the following values:

- `goal_duration_sum`: The duration sum value of the given Search Goal.

- `goal_exceed_ratio`: The exceed ratio value of the given Search Goal.

- `full_length_low_loss_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  not higher than the Goal Loss Ratio.

- `full_length_high_loss_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  higher than the Goal Loss Ratio.

- `short_low_loss_sum`: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with a Trial Loss Ratio
  not higher than the Goal Loss Ratio.

- `short_high_loss_sum`: Sum of durations across trials with trial duration
  shorter than the goal final trial duration and with a Trial Loss Ratio
  higher than the Goal Loss Ratio.

The code works correctly also when there are no trial results at a given load.

~~~ python
exceed_coefficient = goal_exceed_ratio / (1.0 - goal_exceed_ratio)
balancing_sum = short_low_loss_sum * exceed_coefficient
positive_excess_sum = max(0.0, short_high_loss_sum - balancing_sum)
effective_high_loss_sum = full_length_high_loss_sum + positive_excess_sum
effective_full_length_sum = full_length_low_loss_sum + effective_high_loss_sum
effective_whole_sum = max(effective_full_length_sum, goal_duration_sum)
quantile_duration_sum = effective_whole_sum * goal_exceed_ratio
pessimistic_high_loss_sum = effective_whole_sum - full_length_low_loss_sum
pessimistic_is_lower = pessimistic_high_loss_sum <= quantile_duration_sum
optimistic_is_lower = effective_high_loss_sum <= quantile_duration_sum
~~~

# Appendix B: Conditional Throughput

This section specifies how to compute Conditional Throughput, as referred to in section [Conditional Throughput](#conditional-throughput).

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
    e.g. in [Conditional Throughput](#conditional-throughput) section.</mark>

{:/comment}

The pseudocode happens to be valid Python code.

The pseudocode expects the following variables to hold the following values:

- `goal_duration_sum`: The duration sum value of the given Search Goal.

- `goal_exceed_ratio`: The exceed ratio value of the given Search Goal.

- `full_length_low_loss_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  not higher than the Goal Loss Ratio.

- `full_length_high_loss_sum`: Sum of durations across trials with trial duration
  at least equal to the goal final trial duration and with a Trial Loss Ratio
  higher than the Goal Loss Ratio.

- `full_length_trials`: An iterable of all trial results from trials with trial duration
  at least equal to the goal final trial duration,
  sorted by increasing the Trial Loss Ratio.
  A trial result is a composite with the following two attributes available:

  - `trial.loss_ratio`: The Trial Loss Ratio as measured for this trial.

  - `trial.duration`: The trial duration of this trial.

The code works correctly only when there if there is at least one
trial result measured at a given load.

~~~ python
full_length_sum = full_length_low_loss_sum + full_length_high_loss_sum
whole_sum = max(goal_duration_sum, full_length_sum)
remaining = whole_sum * (1.0 - goal_exceed_ratio)
quantile_loss_ratio = None
for trial in full_length_trials:
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

# Index

{::comment}

    TODO-P2: There are long lines.

{:/comment}

- Bound: Lower Bound or Upper Bound.
- Bounds: Lower Bound and Upper Bound.
- Conditional Throughput: defined in [Conditional Throughput](#conditional-throughput), discussed in [Generalized Throughput](#generalized-throughput).
- Controller: introduced in [Overview ](#overview), defined in [Controller ](#controller).
- Controller Input: defined in [Controller Input](#controller-input).
- Controller Output: defined in [Controller Output](#controller-output).
- Full-Length Trial: defined in [Full-Length Trial](#full-length-trial).
- Goal Duration Sum: defined in [Goal Duration Sum](#goal-duration-sum), discussed in [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials).
- Goal Exceed Ratio: defined in [Goal Exceed Ratio](#goal-exceed-ratio), discussed in [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials).
- Goal Final Trial Duration: defined in [Goal Final Trial Duration](#goal-final-trial-duration).
- Goal Initial Trial Duration: defined in [Goal Initial Trial Duration](#goal-initial-trial-duration).
- Goal Loss Ratio: defined in [Goal Loss Ratio](#goal-loss-ratio).
- Goal Result: defined in [Goal Result](#goal-result).
- Goal Width: defined in [Goal Width](#goal-width).
- Exceed Probability: defined in [Exceed Probability](#exceed-probability)
- High-Loss Trial: defined in [High-Loss Trial](#high-loss-trial).
- Intended Load: defined in [RFC2285] (Section 3.5.1).
- Irregular Goal Result: defined in [Irregular Goal Result](#irregular-goal-result).
- Load: introduced in [Trial Load](#trial-load).
- Load Classification: Introduced in [Overview ](#overview), defined in [Load Classification](#load-classification), discussed in [Load Classification Logic](#load-classification-logic).
- Loss Inversion: Situation introduced in [Inconsistent Trial Results](#inconsistent-trial-results), defined in [Loss Ratios and Loss Inversion](#loss-ratios-and-loss-inversion).
- Low-Loss Trial: defined in [Low-Loss Trial](#low-loss-trial).
- Lower Bound: defined in [Lower Bound](#lower-bound).
- Manager: introduced in [Overview ](#overview), defined in [Manager ](#manager).
- Max Load: defined in [Max Load](#max-load).
- Measurer: introduced in [Overview ](#overview), defined in [Meaurer ](#measurer).
- Min Load: defined in [Min Load](#min-load).
- MLRsearch Specification: introduced in [Purpose and Scope](#purpose-and-scope)
and in [Overview ](#overview), defined in [Test Procedure Compliant with MLRsearch](#test-procedure-compliant-with-mlrsearch).
- MLRsearch Implementation: defined in [Test Procedure Compliant with MLRsearch](#test-procedure-compliant-with-mlrsearch).
- Offered Load: defined in [RFC2285] (Section 3.5.2).
- Regular Goal Result: defined in [Regular Goal Result](#regular-goal-result).
- Relevant Bound: Relevant Lower Bound or Relevant Upper Bound.
- Relevant Bounds: Relevant Lower Bound and Relevant Upper Bound.
- Relevant Lower Bound: defined in [Relevant Lower Bound](#relevant-lower-bound), discussed in [Conservativeness and Relevant Bounds](#conservativeness-and-relevant-bounds).
- Relevant Upper Bound: defined in [Relevant Upper Bound](#relevant-upper-bound).
- Search: defined in [Overview ](#overview).
- Search Duration: introduced in [Purpose and Scope](#purpose-and-scope) and in [Long Search Duration](#long-search-duration), discussed in [Stopping Conditions and Precision](#stopping-conditions-and-precision).
- Search Goal: defined in [Search Goal](#search-goal).
- Search Result: defined in [Search Result](#search-result).
- Short Trial: defined in [Short Trial](#short-trial).
- Throughput: defined in [RFC1242] (Section 3.17), Methodology specified in [RFC2544] (Section 26.1).
- Trial: defined in [Trial ](#trial).
- Trial Duration: defined in [Trial Duration](#trial-duration).
- Trial Effective Duration: defined in [Trial Effective Duration](#trial-effective-duration).
- Trial Forwarding Rate: defined in [Trial Forwarding Rate](#trial-forwarding-rate).
- Trial Forwarding Ratio: defined in [Trial Forwarding Ratio](#trial-forwarding-ratio).
- Trial Input: defined in [Trial Input](#trial-input).
- Trial Loss Ratio: defined in [Trial Loss Ratio](#trial-loss-ratio).
- Trial Load: defined in [Trial Load](#trial-load).
- Trial Output: defined in [Trial Output](#trial-output).
- Trial Result: defined in [Trial Result](#trial-result).
- Upper Bound: defined in [Upper Bound](#upper-bound).

{::comment}

    - Test Procedure: defined in [RFC2544] (Section 26), TODO-P3: That lists several procedures in subsection,
      but does not define what "a test procedure" is.
    - Test Report: defined in [RFC2544] (Section 26), TODO-P3: Lists reporting formats without actually defining what the report is.
    - Tester: defined in [RFC2544] (Section 6), TODO-P3: Not used enough to be in Glossary.

{:/comment}

--- back

{::comment}
    [Final checklist.]

    <mark>[VP] Final Checks. Only mark as done when there are no active todos above.</mark>
    
    <mark>[VP] Rename chapter/sub-/section to better match their content.</mark>
    
    <mark>MKP3 [VP] TODO: Recheck the definition dependencies go bottom-up.</mark>
    
    <mark>[VP] TODO: Unify external reference style (brackets, spaces, section numbers and names).</mark>
    
    <mark>MKP2 [VP] TODO: Capitalization of New Terms: useful when editing and reviewing,
    but I still vote to remove capitalization before final submit,
    because all other RFCs I see only capitalize due to being section title.</mark>
    
    <mark>[VP] TODO: If time permits, keep improving formal style (e.g. using AI).</mark>

{:/comment}

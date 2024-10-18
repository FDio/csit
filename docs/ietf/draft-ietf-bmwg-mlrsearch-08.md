---

title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-08
date: 2024-08-28

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

{:/comment}

[toc]

# Glossary

TODO: Add all capitalized terms, with links where introduced, defined or explained.

TODO: Bound := Lower Bound or Upper Bound

TODO: Bounds := Lower Bound and Upper Bound

TODO: Relevant Bound := Relevant Lower Bound or Relevant Upper Bound

TODO: Relevant Bounds := Relevant Lower Bound and Relevant Upper Bound

**Conditional Throughput**:<br>
Defined in [Conditional Throughput](#conditional-throughput).<br>
Discussed in [Generalized Throughput](#generalized-throughput).

**Controller**:<br>
Introduced in [Overview ](#overview).<br>
Defined in [Controller ](#controller).

**Controller Input**:<br>
Defined in [Controller Input](#controller-input).

**Controller Output**:<br>
Defined in [Controller Output](#controller-output).

**Full-Length Trial**:<br>
Defined in [Full-Length Trial](#full-length-trial).

**Goal Duration Sum**:<br>
Defined in [Goal Duration Sum](#goal-duration-sum).<br>
Discussed in [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials).

**Goal Exceed Ratio**:<br>
Defined in [Goal Exceed Ratio](#goal-exceed-ratio).<br>
Discussed in [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials).

TODO: Add also Exceed Probability is used in last chapter.

**Goal Final Trial Duration**:<br>
Defined in [Goal Final Trial Duration](#goal-final-trial-duration).

**Goal Initial Trial Duration**:<br>
Defined in [Goal Initial Trial Duration](#goal-initial-trial-duration).

**Goal Loss Ratio**:<br>
Defined in [Goal Loss Ratio](#goal-loss-ratio).

**Goal Result**:<br>
Defined in [Goal Result](#goal-result).

**Goal Width**:<br>
Defined in [Goal Width](#goal-width).

**High-Loss Trial**:<br>
Defined in [High-Loss Trial](#high-loss-trial).

**Intended Load**:<br>
Defined in [RFC2285] (Section 3.5.1).

**Irregular Goal Result**:<br>
Defined in [Irregular Goal Result](#irregular-goal-result).

**Load**:<br>
Introduced in [Trial Load](#trial-load).

**Load Classification**:<br>
Introduced in [Overview ](#overview).<br>
Defined in [Load Classification](#load-classification).<br>
Discussed in [Load Classification Logic](#load-classification-logic).

**Loss Inversion**:<br>
Situation introduced in [Inconsistent Trial Results](#inconsistent-trial-results).<br>
Defined in [Loss Ratios and Loss Inversion](#loss-ratios-and-loss-inversion).

**Low-Loss Trial**:<br>
Defined in [Low-Loss Trial](#low-loss-trial).

**Lower Bound**:<br>
Defined in [Lower Bound](#lower-bound).

**Manager**:<br>
Introduced in [Overview ](#overview).<br>
Defined in [Manager ](#manager).

**Max Load**:<br>
Defined in [Max Load](#max-load).

**Measurer**:<br>
Introduced in [Overview ](#overview).<br>
Defined in [Meaurer ](#measurer).

**Min Load**:<br>
Defined in [Min Load](#min-load).

**MLRsearch Specification**:<br>
Introduced in [Purpose and Scope](#purpose-and-scope)
and in [Overview ](#overview).<br>
Defined in [Test Procedure Compliant with MLRsearch](#test-procedure-compliant-with-mlrsearch).

**MLRsearch Implementation**:<br>
Defined in [Test Procedure Compliant with MLRsearch](#test-procedure-compliant-with-mlrsearch).

**Offered Load**:<br>
Defined in [RFC2285] (Section 3.5.2).

**Regular Goal Result**:<br>
Defined in [Regular Goal Result](#regular-goal-result).

**Relevant Lower Bound**:<br>
Defined in [Relevant Lower Bound](#relevant-lower-bound).<br>
Discussed in [Consevativeness and Relevant Bounds](#consevativeness-and-relevant-bounds).

**Relevant Upper Bound**:<br>
Defined in [Relevant Upper Bound](#relevant-upper-bound).

**Search**:<br>
Defined in [Overview ](#overview).

**Search Duration**:<br>
Introduced in [Purpose and Scope](#purpose-and-scope)
and in [Long Search Duration](#long-search-duration).<br>
Discussed in [Stopping Conditions and Precision](#stopping-conditions-and-precision).

**Search Goal**:<br>
Defined in [Search Goal](#search-goal).

**Search Result**:<br>
Defined in [Search Result](#search-result).

**Short Trial**:<br>
Defined in [Short Trial](#short-trial).

**Test Procedure**:<br>
Defined in [RFC2544] (Section 26).<br>
TODO: That lists several procedures in subsection,
but does not define what "a test procedure" is.

**Test Report**:<br>
Defined in [RFC2544] (Section 26).<br>
TODO: Lists reporting formats without actually defining what the report is.

**Tester**:<br>
Defined in [RFC2544] (Section 6).<br>
TODO: Not used enough to be in Glossary.

**Throughput**:<br>
Defined in [RFC1242] (Section 3.17).<br>
Methodology specified in [RFC2544] (Section 26.1).

**Trial**:<br>
Defined in [Trial ](#trial).

**Trial Duration**:<br>
Defined in [Trial Duration](#trial-duration).

**Trial Effective Duration**:<br>
Defined in [Trial Effective Duration](#trial-effective-duration).

**Trial Forwarding Rate**:<br>
Defined in [Trial Forwarding Rate](#trial-forwarding-rate).

**Trial Forwarding Ratio**:<br>
Defined in [Trial Forwarding Ratio](#trial-forwarding-ratio).

**Trial Input**:<br>
Defined in [Trial Input](#trial-input).

**Trial Loss Ratio**:<br>
Defined in [Trial Loss Ratio](#trial-loss-ratio).

**Trial Load**:<br>
Defined in [Trial Load](#trial-load).

**Trial Output**:<br>
Defined in [Trial Output](#trial-output).

**Trial Result**:<br>
Defined in [Trial Result](#trial-result).

**Upper Bound**:<br>
Defined in [Upper Bound](#upper-bound).

# Purpose and Scope

The purpose of this document is to describe the Multiple Loss Ratio search
(MLRsearch) methodology, optimized for determining
data plane throughput in software-based networking devices.

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
    [RFC2285] (Section 3.6.2) to initialize the initial targets.
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
    response measured [RFC2285] (Section 3.1.1).
- SUT as
  - The collective set of network devices to which stimulus is offered
    as a single entity and response measured [RFC2285] (Section 3.1.2).

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

TODO: Mention that the Relevant Lower Bound is such a definition?

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

Some terms used in the specification are capitalized.
It is just a stylistic choice for this document,
reminding the reader this term is introduced, defined or explained
elsewhere in the document.
Lowercase variants are equally valid.

A subsection that focuses on a particular term contains a short paragraph
marked Definition, it contains a minimal definition and all strict REQUIREMENTS.
That is followed by few paragraphs marked as Discussion, that contain
some important consequences and RECOMMENDATIONS.
Other text in this chapter usually discusses document structure
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
When measured enough, any chosen Load can either achieve of fail
each Search Goal (separately), thus becoming
a Lower Bound or an Upper Bound for that Search Goal.

When the relevant bounds are at Loads that are close enough
(according to Goal Width), the Regular Goal Result is found.
Search stops when all Regular Goal Result are found,
or when some Search Goals are proven to have only Irregular Goal Results.

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

TODO: Merge into Glossary!

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

The definition describes some traits, it is not clear whether all of them
are REQUIRED, or some of them are only RECOMMENDED.

Trials are the only stimuli the SUT is expected to experience
during the Search.

For the purposes of the MLRsearch specification,
it is ALLOWED for the test procedure to deviate from the [RFC2544] description,
but any such deviation MUST be described explicitly in the test report.

In some discussion paragraphs, it is useful to consider the traffic
as sent and received by a tester, as implicitly defined
in [RFC2544] (Section 6).

TODO: Assert traffic is sent in C and received in C and D.

An example of deviation from [RFC2544] is using shorter wait times
(in phases b, d and e).

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
In the case on non-constant load, the test report
MUST explicitly mention how exactly non-constant the traffic is.

Trial Load is equivalent to the quantities defined
as constant load of [RFC1242] (Section 3.4),
data rate of [RFC2544] (Section 14),
and Intended Load of [RFC2285] (Section 3.5.1),
in the sense that all three definitions specify that this value
applies to one (input or output) interface.

For test report purposes, multi-interface aggregate load MAY be reported,
this is understood as the same quantity expressed using different units.
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
all attributes other than trial load and trial duration,
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

The Traffic Profile SHOULD contain some specific quantities defined elsewhere,
for example [RFC2544] (Section 9) governs
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

Other traffic properties that (if they apply) need to be somehow specified
in Traffic Profile include:

- Bidirectional traffic from [RFC2544] (Section 14),

- Fully meshed traffic from [RFC2285] (Section 3.3.3),

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

TODO: Mention iload/oload difference is also out of scope.

TODO: Mention duplicate, previous-trial and other "more than expected"
frame counts are out of scope. Recommend to count them as loss?

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

This is almost identical to Frame Loss Rate of [RFC1242] (Section 3.6),
the only minor differences are that Trial Loss Ratio
does not need to be expressed as a percentage,
and Trial Loss Ratio is explicitly based on aggregate frame counts.

### Trial Forwarding Rate

Definition:

The Trial Forwarding rate is a derived quantity, calculated by
multiplying the Trial Load by the Trial Forwarding Ratio.

Discussion:

It is important to note that while similar, this quantity is not identical
to the Forwarding Rate as defined in [RFC2285] (Section 3.6.1).
The latter is specific to one output interface only,
whereas the Trial Forwarding Ratio is based
on frame counts aggregated over all SUT output interfaces.

As a consequence, for symmetric traffic profiles the Trial Forwarding Rate value
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

Also, this is a way for the Measurer to inform the Controller about
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

Discussions within this section are short, informal,
and referencing future sections, because the impact on search results
is better be discussed only after introducing further auxiliary terms.

### Goal Final Trial Duration

Definition:

A threshold value for Trial Duration values.

Discussion:

This attribute value MUST be positive.

Informally, while MLRsearch is allowed to perform trials shorter than this value,
the results from such short trials have only limited impact on search results.

But, it is RECOMMENDED for all search goals to share the same
Goal Final Trial Duration value, because otherwise
Trial Duration values larger than the Goal Final Trial Duration may occur,
weakening the intuitions behind
[Load Classification Logic](#load-classification-logic).

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
TODO: Add link to explanation, probably in classification logic chapter.

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

Informally, up to this proportion of trials with Trial Loss Ratio above
Goal Loss Ratio is tolerated at a Lower Bound.

For explainability reasons, the RECOMMENDED value for exceed ratio is 0.5,
as it simplifies some concepts by relating them to the concept of median.

See [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials)
section for more details.

### Goal Width

Definition:

A threshold value for deciding whether two Trial Load values are close enough.

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
TODO: Is this MUST too strong?

It is RECOMMENDED to set the Goal Width (as relative difference) value
to a value no smaller than the Goal Loss Ratio.
The reason is not obvious, the details are in
[Generalized Throughput](#generalized-throughput).

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

TODO: Move (parts of) this paragraph to overview:

Implementations MAY add their own attributes.
Those additional attributes may be required by the implementation
even if they are not required by MLRsearch specification.
But it is RECOMMENDED for those implementations
to support missing values by providing reasonable default values.

TODO: Create subsection fo MLRsearch Implementation.

The meaning of listed attributes is formally given only by their indirect effect
on the search results.

See [Compliance ](#compliance) for important Search Goal instances.

#### Goal Initial Trial Duration

Definition:

A threshold value for Trial Duration values.

Discussion:

This is an example of an OPTIONAL Search Goal some implementations may support.

This attribute value MUST be positive.

Informally, this is the smallest Trial Duration the Controller will select
when focusing on this goal.

The reasonable default in this case is using the Goal Final Trial Duration
value.

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

TODO: This paragraph is for implementers.
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
but as all trials as possibly affecting all Search Goals,
it makes more sense for a single Max Load value to apply
to all Search Goal instances.

While Max Load is a frequently used configuration parameter, already governed
(as maximum frame rate) by [RFC2544] (Section 20)
and (as maximum offered load) by [RFC2285] (Section 3.5.3),
some implementations may detect or discover it
(instead of requiring a user-supplied value).

TODO: Move this (and goal width) to RUB discussion or other explanation instead.
In MLRsearch specification, one reason for listing
the [Relevant Upper Bound](#relevant-upper-bound) as a required attribute
as that it makes the search result independent of Max Load value.

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
Similarly top Max Load, it makes more sense to prescribe one common value,
as opposed to using a different value for each Search Goal.

Min Load is mainly useful for saving time by failing early,
arriving at an Irregular Goal Result when Min Load is classified
as an Upper Bound.

For implementations, it is useful to require Min Load to be non-zero
and large enough to result in at least one frame being forwarded
even at smallest allowed Trial Duration,
so Trial Loss Ratio is always well-defined,
and the implementation can use relative Goal Width
(without running into issues around zero Trial Load value).

## Auxiliary Terms

While the terms defined in this section are not strictly needed
when formulating MLRsearch requirements, they simplify the language used
in discussion paragraphs and explanation chapters.

### Current and Final Quantities

Some quantites are defined in a way that allows them to be computed
in the middle of the Search. Other quantities are specified in a way
that allows them to be computed only after the Search ends.
And some quantities are important only after the Search ended,
but are computable also before the Search ends.

The adjective **current** marks a quantity that is computable
before the Search ends, but the computed value may change during the Search.
When such value is relevant for the search result, the adjective **final**
may be used to denote the value at the end of the Search.

TODO: How to unify with the Glossary?

### Trial Classification

When one Trial Result instance is compared to one Search Goal instance,
several relations can be named using short adjectives.

As trial results do not affect each other, this **Trial Classification**
does not change during the Search.

TODO: Is it obvious the adjectives can be combined?

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

TODO: Maybe use "full-length" only when the duration is equal,
and "long" if not short (e.g. when equal or longer)?

### Load Classification

TODO: Turn into a precise definition paragraph?

When the set of all Trial Result instances performed (so far)
at one Trial Load are compared to one Search Goal instance,
two relations can be named using the concept of a bound.

In general, such bounds are a current quantity,
even though cases of changing bounds is rare in practice.

#### Upper Bound

Definition:

A Trial Load value is called an Upper Bound if and only if it is classified
as such by [Appendix A: Load Classification](#appendix-a-load-classification)
algorithm for the given Search Goal at the current moment of the Search.

Discussion:

In more detail, the set of all trial outputs (both short and full-length)
performed so far at the Trial Load is certain to fail to uphold
all the requirements of the given Search Goal, mainly the Goal Loss Ratio
in combination with the Goal Exceed Ratio.
Here "certain to fail" relates to any possible results within the time
remaining till Goal Duration Sum.

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

In more detail, the set of all trial outputs (both short and full-length)
performed so far at the Trial Load is certain to uphold all the requirements
of the given Search Goal, mainly the Goal Loss Ratio
in combination with the Goal Exceed Ratio.
Here "certain to uphold" relates to any possible results within the time
remaining till Goal Duration Sum.

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

TODO: Delete or move:
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

As the Relevant Lower Bound is defined only at the end of the search,
so is the Conditional Throughput.
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

TODO: "max search time exceeded" flag?

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

TODO: Summarize test report requirements here?

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

TODO: Define "MLRsearch Implementation" here.

TODO: Explain "MLRsearch" denotes "any MLRsearch Implementation"?

### MLRsearch Compliant with RFC2544

The following Search Goal instance makes the corresponding Search Result
unconditionally compliant with [RFC2544] (Section 24).

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 60 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 0%

The latter two attributes are enough to make the search goal
conditionally compliant, adding the first attribute
makes it unconditionally compliant.

The second attribute (Goal Duration Sum) only prevents MLRsearch
from repeating zero-loss full-length trials.

The presence of other Search Goals does not affect the compliance
of this Goal Result.
The Relevant Lower Bound and the Conditional Throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

TODO: Move the rest into Load Classification Logic chapter.

Non-zero exceed ratio is not strictly disallowed, but it could
needlessly prolong the search when low-loss short trials are present.

TODO: Also it would open more questions re Loss Inversion,
but no need to say that anywhere.

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
As Goal Duration Sum is twice as long as Goal Final Trial Duration,
third full-length trial is never needed.

# Further Explanations

This chapter provides further explanations of MLRsearch behavior,
mainly in comparison to a simple bisection for [RFC2544] Throughput.

## Binary Search

A typical binary search implementation for [RFC2544]
tracks only the two tightest bounds.
To start with, the search needs both Max Load and Min Load values,
one trial is used to confirm Max Load is an Upper Bound,
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
and final distance between the tightest bounds,
so the search always takes the same time (assuming initial bounds are confirmed).

## Stopping Conditions and Precision

MLRsearch specification requires listing both Relevant Bounds for each
Search Goal, and the difference between the bounds implies
the result precision achieved,
making it unnecessary to report the specific stopping condition used.

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
is in the goals of the search. [RFC2544] has a single goal,
based on classifying a single full-length trial
as either zero-loss or non-zero-loss.

MLRsearch, supports searching for multiple goals at once,
usually differing in their Goal Loss Ratio values.

### Single Goal and Hard Bounds

Each bound in [RFC2544] simple binary search is "hard",
in the sense that all futher Trial Load values
are smaller than any current upper bound and larger than any current lower bound.

This is also possible for MLRsearch implementations,
when the search is started with only one Search Goal instance.

### Multiple Goals and Loss Inversion

MLRsearch supports multiple goals, making the search procedure
more complicated compared to binary search with a single goal,
but most of the complications do not affect the final results much.
Except for one phenomenon: Loss Inversion.

Depending on Search Goal attributes, Load Classification results may be resistant
to small amounts of [Inconsistent Trial Results](#inconsistent-trial-results).
But for larger amounts, a Load that is classified
as an Upper Bound for one Search Goal
may still be a Lower Bound for another Search Goal.
And, due to this other goal, MLRsearch will probably perform subsequent Trials
at Trial Loads even higher than the original value.

TODO: Unify load adjectives: higher/lower xor larger/smaller. => higher/lower.

This introduces questions any many-goals search algorithm has to address.
What to do when all such higher load trials happen to have zero loss?
Does it mean the earlier upper bound was not real?
Does it mean the later low-loss trials are not considered a lower bound?

The situation where a smaller load is classified as an Upper Bound,
while a larger load is classified as a Lower Bound (for the same search goal),
is called Loss Inversion.

Conversely, only single-goal search algorithms can have hard bounds
that shield them from Loss Inversion.

### Consevativeness and Relevant Bounds

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

TODO VP: Unclear which content you mean - i don't see anything in
earlier sections that would fit here. but i may be wrong.

TODO: Move some discussion on Trial Effective Duration from spec chapter
to around here? => MK not sure i see any content earlier that would fit here.

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

TODO VP: unlear why GITD should be equal to GFTD.

TODO: Discuss chains of intermediate goals? Probably not. => Definitely not :)

TODO note: below to be removed once Load Classification Logic is done.

In a nutshell, results from short trials
may cause a load to be classified as an upper bound.
This may cause loss inversion, and thus lower the Relevant Lower Bound,
below what would classification say when considering full-length trials only.

TODO VP: above paragraph doesn't seem to fit here.

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
values may have up to the Goal Loss Ratio relative difference of loads.

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

TODO: Move the rest into the last chapter.

Conditional Throughput is partially related to load classification.
If a load is classified as a Relevant Lower Bound for a goal,
the Conditional Throughput comes from a trial result,
that is guaranteed to have Trial Loss Ratio no larger than the Goal Loss Ratio.

TODO VP: above paragraph doesn't seem to fit here.

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

# Load Classification Logic

TODO: Some text here.

## Introductory Remarks

TODO: Outdated, will be rewritten or replaced.

TODO: Move this paragraph to a better place.
For repeatability and comparability reasons, it is important that
all implementations of MLRsearch classify the load equivalently,
based on all trials measured at the given load.

This chapter continues with explanations,
but this time more precise definitions are needed
for readers to follow the explanations.

Descriptions in this section are wordy and implementers should read
[MLRsearch Specification](#mlrsearch-specification) section
and Appendices for more concise definitions.

The two areas of focus here are load classification
and the Conditional Throughput.

To start with [Performance Spectrum](#performance-spectrum)
subsection contains definitions needed to gain insight
into what Conditional Throughput means.
Remaining subsections discuss load classification.

## Algorithms

TODO: Some text re "pseudocode translated into senteces".

### Load Classification Algorithm

TODO: Link to the appendix.

TODO: Make more readable, e.g. by distinguishing inputs from temporary variables.

- Take all trials measured at a given load.

- Full-length high-loss sum is the sum of Trial Effective Duration values of all full-length high-loss trials.
- Full-length low-loss sum is the sum of Trial Effective Duration values of all full-length low-loss trials.
- Short high-loss sum is the sum of Trial Effective Duration values of all short high-loss trials.
- Short low-loss sum is the sum of Trial Effective Duration values of all short low-loss trials.

- Subceed ratio is One minus the Goal Exceed Ratio.
- Exceed coefficient is the Goal Exceed Ratio divided by the subceed ratio.

- Balancing sum is the short low-loss sum multiplied by the exceed coefficient.
- Excess sum is the short high-loss sum minus the balancing sum.
- Positive excess sum is the maximum of zero and excess sum.
- High-loss sum is the full-length high-loss sum plus the positive excess sum.
- Measured sum is the high-loss sum plus the full-length low-loss sum.
- Whole sum is the larger of the measured sum and the Goal Duration Sum.
- Missing sum is the whole sum minus the measured sum.

- Pessimistic high loss sum is the high-loss sum plus the missing sum.
- Optimistic exceed ratio is the high-loss sum divided by the whole sum.
- Pessimistic exceed ratio is the pessimistic high-loss sum divided by the whole sum.

- The load is classified as an Upper Bound if the optimistic exceed ratio is larger than the Goal Exceed Ratio.
- The load is classified as a Lower Bound if the pessimistic exceed ratio is not larger than the Goal Exceed Ratio.
- The load is classified as undecided otherwise.

### Conditional Throughput Algorithm

TODO: Link to the appendix.

- Take all trials measured at a given Load.

- Full-length high-loss sum is the sum of Trial Effective Duration values of all full-length high-loss trials.
- Full-length low-loss sum is the sum of Trial Effective Duration values of all full-length low-loss trials is called.
- Full-length sum is the full-length high-loss sum plus the full-length low-loss sum.

- Subceed ratio is One minus the Goal Exceed Ratio is called.
- Remaining sum initially is full-lengths sum multiplied by subceed ratio.
- Current loss ratio initially is 100%.

- For each full-length trial result, sorted in increasing order by Trial Loss Ratio:
 - If remaining sum is not larger than zero, exit the loop.
 - Else:
  - Set current loss ratio to this trial's Trial Loss Ratio.
  - Decrease the remaining sum by this trial's Trial Effective Duration.

- Current forwarding ratio is One minus the current loss ratio.
- Conditional Throughput is the current forwarding ratio multiplied by the Load value.

TODO: Move somewhere else.

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

## SUT behaviors

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
During the Search the expert can also comment on past Trial Results.

TODO: Lucky if less than expected number of high-loss trials?

### Exceed Probability

When the Controller selects new Trial Duration and Trial Load,
and just before the Measurer starts performing the Trial,
the SUT expert can envision possible Trial Results.

With respect to a particular Search Goal instance, the possibilities
can be summarized into a single number: Exceed Probability.
It is the probability (according to the expert) that the measured
Trial Loss Ratio will be higher than the Goal Loss Ratio.

TODO: Do we need to say small EP means low load?

TODO: Mention how ER relates to EP here?

TODO: Tie to Relevant Lower Bound and Conditional Throughput somewhere.

### Trial Duration Dependence

When comparing Exceed Probability values for the same Trial Load
but different Trial Duration, there are several patterns that commonly occur
in practice.

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

TODO: Define loss spike? Mention loss spikes when discussing noise?

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

    ### Loss Spikes

    #### Frequent Small Loss Spikes

    #### Rare Big Loss Spikes

{:/comment}

## Scenarios

TODO: (selected examples where we have intuition)

TODO: Replace "intuition" with something more appropriate.

In all scenarios, the SUT is well-behaved in the sense that
all Exceed Probability values are constant during the Search
(the Trial Results are independent).

In all scenarios, Effective Trial Duration is equal to Trial Duration.

In all scenarios, only one Trial Load value is in focus,
Trial Results at other Loads are possible but not mentioned.

In all scenarios, only one Search Goal instance is in focus,
but there may be other goals causing otherwise unneeded Trials.


TODO: Divide scenarios so each scenario is one point in time.
This means chaining scenarios, some are possible futures of others.
The SUT expert predictions are important only for scenario chaining,
not for classification.

### Scenario 1

"Same Duration Best Case" scenario.

Goal attributes:
- Goal Final Trial Duration = 1 second.
- Goal Duration Sum = 7 seconds.
- Goal Loss Ratio = 0%.
- Goal Exceed Eatio = 50%.

SUT behavior at the current load:
- Exceed Probability is almost zero.

Trials measured so far at the current load:
- Three 1-second trials, each of zero loss.
- This is likely situation for the SUT behavior.

Intuition:
- Still needs measuring, as Goal Duration Sum is not reached yet.

Likely future according to SUT expert:
- 1 more 1-second trial will be measured,
- probably with zero-loss result.
- Then there is enough data to mark the Load as a Lower Bound.

Comments:
- This shows time can be saved when results are one-sided.

Algorithms:
- full-length high-loss sum = 0s.
- full-length low-loss sum = 3 x 1s = 3s.
- short high-loss sum = 0s.
- short low-loss sum = 0s.
- subceed ratio = 100% - 50% = 50%.
- exceed coefficient = 50% / 50% = 1.0.
- balancing sum = 0s x 1.0 = 0s.
- excess sum = 0s - 0s = 0s.
- high-loss sum = 0s + 0s = 0s.
- measured sum = 3s + 0s = 3s.
- whole sum = max(7s, 3s) = 7s.
- missing sum = 7s - 3s = 4s.
- optimistic exceed ratio = 0s / 7s = 0%.
- pessimistic exceed ratio = (0s + 4s) / 7s = 57.14%.
- 0% <= 50% < 57.14% so load is classified as undecided.

TODO: Conditional Throughput does not apply. Show how algo fails?

TODO: Finish this stub.

### Scenario 2

"Same Duration Worst Case" scenario.

Goal attributes:
- Goal Final Trial Duration = 1 second.
- Goal Duration Sum = 7 seconds.
- Goal Loss Ratio = 0%.
- Goal Exceed Eatio = 50%.

SUT behavior at the current load:
- Exceed Probability is almost 100%.

Trials measured so far at the current load:
- Three 1-second trials, each of zero loss.
- This is very unlikely situation according to SUT expert.

Intuition:
- Still needs measuring, as Goal Duration Sum is not reached yet.

Likely future according to SUT expert:
- 4 more 1-second trials, probably all of them high-loss.
- Then there is enough data to mark the Load as an Upper Bound.

Comments:
- This shows time savings are not guaranteed (all 7 trials needed).
- Scenarios 1 and 2 have the same data, only expectations are different.

Algorithms:
- full-length high-loss sum = 0s.
- full-length low-loss sum = 3 x 1s = 3s.
- short high-loss sum = 0s.
- short low-loss sum = 0s.
- subceed ratio = 100% - 50% = 50%.
- exceed coefficient = 50% / 50% = 1.0.
- balancing sum = 0s x 1.0 = 0s.
- excess sum = 0s - 0s = 0s.
- high-loss sum = 0s + 0s = 0s.
- measured sum = 3s + 0s = 3s.
- whole sum = max(7s, 3s) = 7s.
- missing sum = 7s - 3s = 4s.
- optimistic exceed ratio = 0s / 7s = 0%.
- pessimistic exceed ratio = (0s + 4s) / 7s = 57.14%.
- 0% <= 50% < 57.14% so load is classified as undecided.

TODO: Conditional Throughput does not apply. Show how algo fails?

TODO: Finish this stub.

### Scenario 3

"Mixed Duration False Good" scenario.

Goal attributes:
- Goal Final Trial Duration = 10 seconds.
- Goal Duration Sum = 70 seconds.
- Goal Loss Ratio = 0%.
- Goal Exceed Eatio = 50%.

SUT behavior at the current load:
- Exceed probabilities depend heavily on Trial Durations.
- Exceed Probability is high at 10-second Trial Duration,
- but low at 1-second Trial Duration (e.g. due to large buffers).

Trials measured so far at the current load:
- Fourty 1-second trials, zero loss each.
- This is somewhat likely situation for the SUT behavior.

Intuition:
- Still needs measuring.
- If short trials were reliable, Goal Duration Sum would be reached.
- But Goal Final Trial Duration is large for a reason,
- so low-loss short trials are not enough to classify the Load as a Lower Bound.

Likely future knowing SUT behavior:
- 4 more 10-second trials, probably all of them lossy.
- Then there is enough data to mark the Load as an Upper Bound.

Comments:
- This shows time savings from short trials are not guaranteed.

Algorithms:
- full-length high-loss sum = 0s.
- full-length low-loss sum = 0s.
- short high-loss sum = 0s.
- short low-loss sum = 40 x 1s = 40s.
- subceed ratio = 100% - 50% = 50%.
- exceed coefficient = 50% / 50% = 1.0.
- balancing sum = 40s x 1.0 = 40s.
- excess sum = 0s - 40s = -40s.
- high-loss sum = 0s.
- measured sum = 0s + 0s = 0s.
- whole sum = max(70s, 0s) = 70s.
- missing sum = 70s - 0s = 70s.
- optimistic exceed ratio = 0s / 70s = 0%.
- pessimistic exceed ratio = (0s + 70s) / 70s = 100%.
- 0% <= 50% < 100% so load is classified as undecided.

TODO: Conditional Throughput does not apply. Show how algo fails?

TODO: Finish this stub.

### Scenario 4

"Mixed Duration True Bad" scenario.

Goal attributes:
- Goal Final Trial Duration = 10 seconds.
- Goal Duration Sum = 70 seconds.
- Goal Loss Ratio = 0%.
- Goal Exceed Eatio = 50%.

SUT behavior at the current load:
- Exceed probabilities depend on Trial Durations,
- but only as "independent subtrials". (TODO: Explain.)
- Exceed Probability is very high at 10-second Trial Duration,
- but only somewhat high at 1-second Trial Duration.

Trials measured so far at the current load:
- Fourty 1-second trials, each lossy.
- It is somewhat unlikely to see no low-loss trial,
- but not strongly enough to consider this scenario to be very unlikely.

Intuition:
- No need to measure more.
- If a frame is lost in the first second of a short trial,
- it would also been lost in first second of a full-length trial.
  (TODO: Explain, stress the role of zero Goal Loss Ratio, discuss nonzero?)
- So high-loss short trials are enough to classify the Load as an Upper Bound.

Likely future knowing SUT behavior:
- Any 10-second trial will be almost surely lossy.

Comments:
- This shows high-loss short trials may replaceme missing full-length trials.
- Real MLRsearch implementations are unlikely to see this many short trials
  (unless there is another goal specifically to cause them).

Algorithms:
- full-length high-loss sum = 0s.
- full-length low-loss sum = 0s.
- short high-loss sum = 40 x 1s = 40s.
- short low-loss sum = 0s.
- subceed ratio = 100% - 50% = 50%.
- exceed coefficient = 50% / 50% = 1.0.
- balancing sum = 0s x 1.0 = 0s.
- excess sum = 40s - 0s = 40s.
- high-loss sum = 0s + 40s = 40s.
- measured sum = 0s + 40s = 40s.
- whole sum = max(70s, 40s) = 70s.
- missing sum = 70s - 40s = 30s.
- optimistic exceed ratio = 40s / 70s = 57.14%.
- pessimistic exceed ratio = (30s + 40s) / 70s = 100%.
- 50% < 57.14% so load is classified as Upper Bound.

TODO: Conditional Throughput does not apply. Show how algo fails?

TODO: Finish this stub.

TODO: Use only 25x1s data so one full-length trial is still needed?

### Scenario 5

"Mixed Duration Balanced" scenario.

Goal attributes:
- Goal Final Trial Duration = 10 seconds.
- Goal Duration Sum = 70 seconds.
- Goal Loss Ratio = 0.5%.
- Goal Exceed Eatio = 50%.

SUT behavior at the current load:
- Exceed probabilities do not depend on Trial Durations,
- Exceed Probability is around 50% for any Trial Duration.
- This is possible just because Goal Loss Ratio is non-zero.
- Unrealistic, precludes big loss spikes at noisy end (TODO: explain or delete).

Trials measured so far at the current load:
- Fourty 1-second trials.
- Twenty of them are high-loss, twenty of them are low-loss.
- This is a likely set of trial results,
- but in practice it is unlikely for the Search to hit a Load this balanced.

Intuition:
- Not enough data to classify the load yet.
- MLRsearch cannot assume low-loss short trials are unreliable
  (as they were in Scenario 3).
- MLRsearch may assume high-loss short trials are reliable
  (as they were in Scenario 4) but their frequency is not high enough.
- Full-length Trial Results are needed to finish the classification.

Likely future knowing SUT behavior:
- Some number of 10-second Trial Results will be needed.
- Maybe full 7 of them, maybe less if results are not balanced.

Comments:
- This shows low-loss short trials can be only used to "nullify"
  some high-loss short trial results.

Algorithms:
- full-length high-loss sum = 0s.
- full-length low-loss sum = 0s.
- short high-loss sum = 20 x 1s = 20s.
- short low-loss sum = 20 x 1s = 20s.
- subceed ratio = 100% - 50% = 50%.
- exceed coefficient = 50% / 50% = 1.0.
- balancing sum = 20s x 1.0 = 20s.
- excess sum = 20s - 20s = 0s.
- high-loss sum = 0s + 0s = 0s.
- measured sum = 0s + 0s = 0s.
- whole sum = max(70s, 0s) = 70s.
- missing sum = 70s - 0s = 70s.
- optimistic exceed ratio = 0s / 70s = 0%.
- pessimistic exceed ratio = (0s + 70s) / 70s = 100%.
- 0 <= 50% < 100% so load is classified as undecided.

TODO: Conditional Throughput does not apply. Show how algo fails?

TODO: Finish this stub.

TODO: Add a scenario with partial nullification?

### Scenario 6

Mixed With Long Durations scenario.

Goal attributes:
- Goal Final Trial Duration = 1 seconds.
- Goal Duration Sum = 7 seconds.
- Goal Loss Ratio = 0%.
- Goal Exceed Eatio = 50%.

SUT behavior at the current load:
- Exceed probabilities do depend on Trial Durations.
- only as "independent subtrials" as in Scenario 4.
- Exceed Probability is 64% at 20-second trials,
- but 5% for 1-second trials.

Trials measured so far at the current load:
- Single 20-second trial, that happened to be lossy.
- This is quite probable at this SUT behavior.
- There had to be a different Search Goal asking for that trial.

Intuition:
- This should be inconclusive as one 20-second trial does not predict
  how would seven 1-second trial measure.

Likely future knowing SUT behavior:
- No more trials, "incorrectly" classified as an Upper Bound.
- Without 20-second trial and with seven 1-second trials,
  there would be 85% chance to get "correctly" classified as a Lower Bound.

Comments:
- This shows current Load Classification is not good in presence
of longer-than-needed trials.

Algorithms:
- full-length high-loss sum = 20s.
- full-length low-loss sum = 0s.
- short high-loss sum = 0s.
- short low-loss sum = 0s.
- subceed ratio = 100% - 50% = 50%.
- exceed coefficient = 50% / 50% = 1.0.
- balancing sum = 0s x 1.0 = 0s.
- excess sum = 0s - 0s = 0s.
- high-loss sum = 20s + 0s = 20s.
- measured sum = 20s + 0s = 20s.
- whole sum = max(7s, 20s) = 20s.
- missing sum = 20s - 20s = 0s.
- optimistic exceed ratio = 20s / 20s = 100%.
- pessimistic exceed ratio = (20s + 0s) / 20s = 100%.
- 50% < 100% so load is classified as Upper Bound.

TODO: Conditional Throughput does not apply. Show how algo fails?

TODO: Finish this stub.

## Trials with Short Duration

TODO: Outdated, will be rewritten or replaced.

### Scenarios

TODO: Outdated, will be rewritten or replaced.

Trials with intended duration smaller than the goal final trial duration
are called short trials.
The motivation for load classification logic in the presence of short trials
is based around a counter-factual case: What would the trial result be
if a short trial has been measured as a full-length trial instead?

There are three main scenarios where human intuition guides
the intended behavior of load classification.

#### False Good Scenario

TODO: Outdated, will be rewritten or replaced.

The user had their reason for not configuring a shorter goal
final trial duration.
Perhaps SUT has buffers that may get full at longer
trial durations.
Perhaps SUT shows periodic decreases in performance
the user does not want to be treated as noise.

In any case, many short low-loss trials may become full-length high-loss trials
in the counter-factual case.

In extreme cases, there are plenty of short low-loss trials and no short high-loss trials.

In this scenario, we want the load classification NOT to classify the load
as a lower bound, despite the abundance of short low-loss trials.

{::comment}
    [I agree.]

    <mark>MKP2 mk edit note: It may be worth adding why that is. i.e. because
    there is a risk that at longer trial this could turn into a high-loss
    trial.</mark>

{:/comment}

Effectively, we want the short low-loss trials to be ignored, so they
do not contribute to comparisons with the Goal Duration Sum.

#### True Bad Scenario

TODO: Outdated, will be rewritten or replaced.

When there is a frame loss in a short trial,
the counter-factual full-length trial is expected to lose at least as many
frames.

In practice, short high-loss trials are rarely turning into
full-length low-loss trials.

In extreme cases, there are no short low-loss trials.

In this scenario, we want the load classification
to classify the load as an upper bound just based on the abundance
of short high-loss trials.

Effectively, we want the short high-loss trials
to contribute to comparisons with the Goal Duration Sum,
so the load can be classified sooner.

#### Balanced Scenario

TODO: Outdated, will be rewritten or replaced.

Some SUTs are quite indifferent to trial duration.
Performance probability function constructed from short trial results
is likely to be similar to the performance probability function constructed
from full-length trial results (perhaps with larger dispersion,
but without a big impact on the median quantiles overall).

{::comment}
    [Recheck after edits earlier.]

    <mark>MKP1 mk edit note: "Performance probability function" is this function
    defined anywhere? Mention in [Performance Spectrum](#performance-spectrum)
    is not a complete definition.</mark>

{:/comment}

For a moderate Goal Exceed Ratio value, this may mean there are both
short low-loss trials and short high-loss trials.

This scenario is there just to invalidate a simple heuristic
of always ignoring short low-loss trials and never ignoring short high-loss trials,
as that simple heuristic would be too biased.

Yes, the short high-loss trials
are likely to turn into full-length high-loss trials in the counter-factual case,
but there is no information on what would the short low-loss trials turn into.

The only way to decide safely is to do more trials at full length,
the same as in False Good Scenario.

### Classification Logic

TODO: Outdated, will be rewritten or replaced.


#### False Good Scenario

TODO: Outdated, will be rewritten or replaced.

If the duration is too short, we expect to see a higher frequency
of short low-loss trials.
This could lead to a negative excess sum,
which has no impact, hence the load classification is given just by
full-length trials.
Thus, MLRsearch using too short trials has no detrimental effect
on result comparability in this scenario.
But also using short trials does not help with overall search duration,
probably making it worse.

#### True Bad Scenario

TODO: Outdated, will be rewritten or replaced.

Settings with a small exceed ratio
have a small exceed coefficient, so the impact of the short low-loss sum is small,
and the short high-loss sum is almost wholly converted into excess sum,
thus short high-loss trials have almost as big an impact as full-length high-loss trials.
The same conclusion applies to moderate exceed ratio values
when the short low-loss sum is small.
Thus, short trials can cause a load to get classified as an upper bound earlier,
bringing time savings (while not affecting comparability).

#### Balanced Scenario

TODO: Outdated, will be rewritten or replaced.

Here excess sum is small in absolute value, as the balancing sum
is expected to be similar to the short high-loss sum.
Once again, full-length trials are needed for final load classification;
but usage of short trials probably means MLRsearch needed
a shorter overall search time before selecting this load for measurement,
thus bringing time savings (while not affecting comparability).

Note that in presence of short trial results,
the comparibility between the load classification
and the Conditional Throughput is only partial.
The Conditional Throughput still comes from a full-length low-loss trial,
but a load higher than the Relevant Lower Bound may also compute to a low-loss value.

## Trials with Longer Duration

TODO: Outdated, will be rewritten or replaced.

If there are trial results with an intended duration larger
than the goal trial duration, the precise definitions
in Appendix A and Appendix B treat them in exactly the same way
as trials with duration equal to the goal trial duration.

But in configurations with moderate (including 0.5) or small
Goal Exceed Ratio and small Goal Loss Ratio (especially zero),
high-loss trials with longer than goal durations may bias the search
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

Any Trial Load value can be classified,
according to a given [Search Goal](#search-goal).

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
balancing_sum = short_low_loss_sum * goal_exceed_ratio / (1.0 - goal_exceed_ratio)
effective_high_loss_sum = full_length_high_loss_sum + max(0.0, short_high_loss_sum - balancing_sum)
effective_whole_sum = max(full_length_low_loss_sum + effective_high_loss_sum, goal_duration_sum)
quantile_duration_sum = effective_whole_sum * goal_exceed_ratio
optimistic = effective_high_loss_sum <= quantile_duration_sum
pessimistic = (effective_whole_sum - full_length_low_loss_sum) <= quantile_duration_sum
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
all_full_length_sum = max(goal_duration_sum, full_length_low_loss_sum + full_length_high_loss_sum)
remaining = all_full_length_sum * (1.0 - goal_exceed_ratio)
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

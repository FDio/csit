---

title: Multiple Loss Ratio Search
abbrev: MLRsearch
docname: draft-ietf-bmwg-mlrsearch-11
date: 2025-07-07

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
  RFC2119:
  RFC2285:
  RFC2544:
  RFC8174:

informative:
  RFC5180:
# Comment: This part before first --- is not markdown but YAML, so comments need different escape.
#{::comment}
#
#    MB116: Please move to information, as this was provided only as an example.
#
#    VP: Ok.
#
#    MK: Moved.
#
#{:/comment}
  RFC6349:
  RFC8219:
#{::comment}
#
#    MB117: Idem as the other entry.
#
#    VP: Ok.
#
#    MK: Moved.
#
#{:/comment}
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
  Lencze-Shima:
    target: https://datatracker.ietf.org/doc/html/draft-lencse-bmwg-rfc2544-bis-00
    title: "An Upgrade to Benchmarking Methodology for Network Interconnect Devices"
#{::comment}
#
#    MB118: This was expired since 2020. Please remove. Idem for all similar entries
#
#    VP: Hmm, ok.
#
#    MK: Disagree. It is still a useful reference. Marking as expired,
#          but keeping it here. Can we add following entry:
#
#          [Lencze-Shima] Lencse, G., "Benchmarking Methodology for IP
#          Forwarding Devices - RFC 2544bis", Work in Progress,
#          Internet-Draftdraft-lencse-bmwg-rfc2544-bis-009 March 2015.
#          (Expired.)
#
#    VP: TODO: Delete or update or replace the active item.
#
#{:/comment}
  Lencze-Kovacs-Shima:
    target: http://dx.doi.org/10.11601/ijates.v9i2.288
    title: "Gaming with the Throughput and the Latency Benchmarking Measurement Procedures of RFC 2544"
  Ott-Mathis-Semke-Mahdavi:
    target: https://www.cs.cornell.edu/people/egs/cornellonly/syslunch/fall02/ott.pdf
    title: "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm"

--- abstract

This document specifies extensions to "Benchmarking Methodology for
Network Interconnect Devices" (RFC 2544) throughput search by

{::comment}

    MB2: The abstract should self-contained. Hence the need to expand the RFC title.

    VP: Ok.

    MK: Ok. Edited.

{:/comment}

defining a new methodology called Multiple Loss Ratio search

{::comment}

    MB1: This may trigger automatically a comment whether we change (update or amend) any of RFC2544 text.
    Do we?

    VP: Pending BMWG decision.
    VP: For draft11: Officially independent.

    MK: MLRsearch extends RFC2544. Does not change it, nor does it amend it.

    VP: The idea was to extend in sense of adding one new benchmark.
    But as we added more requirements and possible deviations around trials,
    the new methodology is independent from (while possible to combine with) MLR2544.

    VP: Informative context in MLRsearch Position. Normative summary in Scope.

{:/comment}

(MLRsearch). MLRsearch aims to minimize search duration,
support multiple loss ratio searches, and improve result repeatability
and comparability.

MLRsearch is motivated by the pressing need to address the challenges of
evaluating and testing the various data plane solutions, especially in
software- based networking systems based on Commercial Off-the-Shelf
(COTS) CPU hardware vs purpose-built ASIC / NPU / FPGA hardware.

{::comment}

    MB3: What is meant here? What is specific to these systems?
    Do we need to have this mention at this stage?

    VP: Do not distinguish in abstract

    MK: Updated text to focus on COTS hardware vs purpose-built
          hardware. Let us know if this requires further text in abstract.
         (We should keep it concise.)

{:/comment}

{::comment}

    MB4: Too detailed for an abstract. Can be mentioned in an overview/introduction section

    VP: Agreed, we no not need to list the options here.

    MK: OK.
    MK: Removed.

{:/comment}

--- middle

{::comment}

    As we use Kramdown to convert from Markdown,
    we use this way of marking comments not to be visible in the rendered draft.
    https://stackoverflow.com/a/42323390
    If another engine is used, convert to this way:
    https://stackoverflow.com/a/20885980

{:/comment}

[toc]

# Introduction

This document describes the Multiple Loss Ratio search
(MLRsearch) methodology, optimized for determining data plane
throughput in software-based networking functions running on commodity systems with
x86/ARM CPUs (vs purpose-built ASIC / NPU / FPGA). Such network
functions can be deployed on dedicated physical appliance (e.g., a
standalone hardware device) or as virtual appliance (e.g., Virtual
Network Function running on shared servers in the compute cloud).

## Purpose

{::comment}

    MK: Suggest to change title to Purpose, as it does not provide
    brief overview of the document's structure and key content areas.

    VP: Done.

{:/comment}

The purpose of this document is to describe the Multiple Loss Ratio search
(MLRsearch) methodology, optimized for determining
data plane throughput in software-based networking devices and functions.

{::comment}

    MB6: Should be defined.
    Not sure what is specific as any networking device is a software-based device. Even hardware, it is not more than frozen software ;)

    VP: We can mention "noisiness" here, not sure how detailed

    MK: Good point. Added text clarifying the difference. See if this
          is good enough, or does this need any more explanation.
    MK: Edited.

{:/comment}

Applying the vanilla throughput binary search,
as specified for example in [TST-009]

{::comment}

    MB7: Can we have an explicit reference for the method?

    VP: Need to search but should be doable

    MK: RFC2544 mentions binary-search style procedure without fully
          specifying the algorithm. The only other standard that defines is
          ETSI GS NFV-TST 009 - adding it here.
    MK: Edited.

    VP: Removed RFC 2544 as I understand MB wants reference to specifics.

{:/comment}

to software devices under test (DUTs) results in several problems

{::comment}

    MB8: Expand

    VP: Ok (point to DUT).

    MK: Edited.

{:/comment}

- Binary search takes long as most trials are done far from the

{::comment}

    MB9: Can we have a public reference to share here?

    VP: Need to search but should be doable).

    MK: Removed "too". Explanation and public references are provided
          in the Identified Problems section.
    MK: Edited.

{:/comment}

  eventually found throughput.
- The required final trial duration and pauses between trials
  prolong the overall search duration.
- Software DUTs show noisy trial results,
  leading to a big spread of possible discovered throughput values.
- Throughput requires a loss of exactly zero frames, but the industry best practices

{::comment}

    MB10: What is meant there?

    VP: Expand (industry).

    MK: Improved clarity, by referring to loss tolerance. Added references.
    MK: Edited.

{:/comment}

  frequently allow for low but non-zero losses tolerance ([Y.1564], test-equipment manuals).
- The definition of throughput is not clear when trial results are inconsistent.
  (e.g., When successive trials at the same - or even a higher - offered
  load yield different loss ratios, the classical RFC 1242/RFC 2544
  throughput metric can no longer be pinned to a single, unambiguous
  value.)

{::comment}

    MB11: Can we expand on this one?

    VP: Some soft intro to inconsistent trials may be needed here.

    MK: Added text in brackets. See if it is sufficient.
    MK: Edited.

{:/comment}

To address these problems,
the MLRsearch test methodology employs the following enhancements:

1. Allow multiple short trials instead of one big trial per load.
   - Optionally, tolerate a percentage of trial results with higher loss.
2. Allow searching for multiple Search Goals, with differing loss ratios.
   - Any trial result can affect each Search Goal in principle.
3. Insert multiple coarse targets for each Search Goal, earlier ones need
   to spend less time on trials.
   - Earlier targets also aim for lesser precision.
   - Use Forwarding Rate (FR) at Maximum Offered Load (FRMOL), as defined
     in Section 3.6.2 of [RFC2285], to initialize bounds.

{::comment}

    MB12: There is no such section in the document.
    Do you meant Section 3.6.2 of [RFC2285]?
    If so, please update accordingly.
    Idem for all similar occurrences in the document. Thanks.

    VP: Clarify. Check for every external section referenced.

    MK: Yes Section 3.6.2 of [RFC2285] defining FRMOL.
    MK: Edited.

{:/comment}

4. Be careful when dealing with inconsistent trial results.
   - Reported throughput is smaller than the smallest load with high loss.
   - Smaller load candidates are measured first.
5. Apply several time-saving load selection heuristics that deliberately
   prevent the bounds from narrowing unnecessarily.

{::comment}

    MB13: Maximizing means?

    VP: Reformulate.

    MK: Edited.

{:/comment}

{::comment}

    VP: Item 3 is also mostly out of scope,
    if we do not count Goal Initial Trial Duration
    (it is and example of optional attribute, not a recommendation).

    TODO: Either say the list talks about CSIT implementation,
    or downgrade item 3 to level of item 5 (example optimization
    that is ultimately out of scope of MLRsearch Specification).

{:/comment}

The first four enhancements

{::comment}

    MB14: Which ones?

    VP: Describe the lists better so "some" is not needed here.

    MK: Edited.

{:/comment}

are formalized as MLRsearch Specification within this document.

{::comment}

    MB15: Where? In this document?

    VP: Yes.

    MK: Edited.

{:/comment}

The remaining enhancements are treated as implementation details,
thus achieving high comparability without limiting future improvements.

MLRsearch configuration options

{::comment}

    MB16: Where are those defined? Please add a pointer to the appropriate section.

    VP: Add pointer.

    MK: TODO.

{:/comment}

are flexible enough to

{::comment}

    MB17: "flexibe" is ambiguous. Simply, state what we do.

    VP: Reformulate.

    MK: TODO.

{:/comment}

support both conservative settings and aggressive settings.
Conservative enough settings lead to results
unconditionally compliant with [RFC2544],
but without much improvement on search duration and repeatability.
Conversely, aggressive settings lead to shorter search durations
and better repeatability, but the results are not compliant with [RFC2544].

{::comment}

    MB18: Add pointers where this is further elaborated.

    VP: Point to specific subsection.

    MK: TODO.

{:/comment}

This document does not change or obsolete any part of [RFC2544].

{::comment}

    MB19: List the set of terms/definitions used in this document.
    I guess we should at least leverage terms defined in 2544/1242.

    VP: Move list of terms here?

    MK: Relevant existing terms, including the ones from rfcs 1242,
          2285 and 2544, are captured in section 4.3 Existing Terms, followed
          by the new terms that form the MLRsearch Specification. We went
          through quite a few iterations of getting it right, including a
          separate terminology section at the beginning of the document, and
          following BMWG comments and reviews ended up with the current
          document structure. Reworking it back is substantial work

    MK: Instead I propose we list one liners explaining the term in
          the context of the benchmarking domain.

    VP: See the comment in first Specification paragraph.
    For specific MB comment, I propose to say no edit needed,
    but ask on bmwg mailer to confirm.

{:/comment}

{::comment}

    MB20: Also, please add a statement that the convention used in bmwg
    are followed here as well (def, discussion, etc.)

    VP: Ok

    MK: The Requirements Language text is the standard one we use in
         BMWG. There are no any strict BMWG conventions that are followed in
         this document. Rather, the convention used for terms that are
         specific to this document, is described in the Section 4 of this
         document, and forms part of the MLRsearch Specification.

    VP: I think this is done, covered by edits elsewhere.

{:/comment}

{::comment}

    TODO: Update the subsection above when the subsections below are complete enough

{:/comment}

## Positioning within BMWG Methodologies

The Benchmarking Methodology Working Group (BMWG) produces recommendations (RFCs)
that describe various benchmarking methodologies for use in a controlled laboratory environment.
A large number of these benchmarks are based on the terminology from [RFC1242]
and the foundational methodology from [RFC2544].
A common pattern has emerged where BMWG documents reference the methodology of [RFC2544]
and augment it with specific requirements for testing particular network systems or protocols,
without modifying the core benchmark definitions.

While BMWG documents are formally recommendations,
they are widely treated as industry norms to ensure the comparability of results between different labs.
The set of benchmarks defined in [RFC2544], in particular,
became a de facto standard for performance testing.
In this context, the MLRsearch Specification formally defines a new
class of benchmarks that fits within the wider [RFC 2544] framework
(see [Scope ](#scope)).

A primary consideration in the design of MLRsearch is the trade-off
between configurability and comparability. The methodology's flexibility,
especially the ability to define various sets of Search Goals,
supporting both single-goal and multiple-goal benchmarks in an unified way
is powerful for detailed characterization and internal testing.
However, this same flexibility is detrimental to inter-lab comparability
unless a specific, common set of Search Goals is agreed upon.

Therefore, MLRsearch should not be seen as a direct extension
nor a replacement for the RFC 2544 Throughput benchmark.
Instead, this document provides a foundational methodology
that future BMWG documents can use to define new, specific, and comparable benchmarks
by mandating particular Search Goal configurations.
For operators of existing test procedures, it is worth noting
that many test setups measuring RFC 2544 Throughput
can be adapted to produce results compliant with the MLRsearch Specification,
often without affecting Trials,
merely by augmenting the content of the final test report.

# Overview of RFC 2544 Problems

This section describes the problems affecting usability
of various performance testing methodologies,
mainly a binary search for [RFC2544] unconditionally compliant throughput.

## Long Search Duration

The proliferation of software DUTs, with frequent software updates and a

{::comment}

    MB21: Is this really new?

    VP: Not sure, ask Maciek

    MK: Changed "emergence" to "proliferation". And yes, the
          proliferation and their importance is new.
    MK: Edited.

{:/comment}

number of different frame processing modes and configurations,
has increased both the number of performance tests
required to verify the DUT update and the frequency of running those tests.
This makes the overall test execution time even more important than before.

The throughput definition per [RFC2544] restricts the potential

{::comment}

    MB22: Won't age well

    VP: I agree, should be reformulated, not sure how.

    MK: Accepted proposed text change.
    MK: Edited.

{:/comment}

for time-efficiency improvements.

{::comment}

    MB23: Concretely, be affirmative if we provide an elaborated def,
    otherwise this statement can be removed.

    VP: Reformulate to affirm and point.

    MK: Agree. This is problem statement, not solution description, so
          removed this paragraph.
    MK: Removed.

{:/comment}

The bisection method, when used in a manner unconditionally compliant
with [RFC2544], is excessively slow  due to two main factors.

{::comment}

    MB24: Can we have a reference?

    VP: Find references.

    MK: Added wording connecting to the following paragraphs with
          explanations.
    MK: Edited.

{:/comment}

Firstly, a significant amount of time is spent on trials
with loads that, in retrospect, are far from the final determined throughput.

{::comment}

    MB25: Define "users".

    VP: Yes, we should be more careful around role names.

    MK: Added text.
    MK: Edited.

{:/comment}

Secondly, [RFC2544] does not specify any stopping condition for
throughput search, so users of testing equipment implementing the
procedure already have access to a limited trade-off
between search duration and achieved precision.
However, each of the full 60-second trials doubles the precision.

{::comment}

    MB26: Can we include a reminder of the 2544 search basics? (no need to be verbose, though)?

    VP: Maybe, not sure how feasible.

    MK: Added.
    MK: Edited.

{:/comment}

As such, not many trials can be removed without a substantial loss of precision.

For reference, here is a brief [RFC2544] throughput binary
(bisection) reminder, based on Sections 24 and 26 of [RFC2544:

* Set Max = line-rate and Min = a proven loss-free load.
* Run a single 60-s trial at the midpoint.
* Zero-loss -> midpoint becomes new Min; any loss-> new Max.
* Repeat until the Max-Min gap meets the desired precision, then report
  the highest zero-loss rate for every mandatory frame size.

## DUT in SUT

[RFC2285] defines:

DUT as:

- The network frame forwarding device to which stimulus is offered and
  response measured Section 3.1.1 of [RFC2285].

{::comment}

    MB27: Double check

    VP: Ok.

    MK: Checked. OK.
    MK: Edited.

{:/comment}

SUT as:

- The collective set of network devices as a single entity to which
  stimulus is offered and response measured Section 3.1.2 of [RFC2285].

Section 19 of [RFC2544] specifies a test setup with an external tester
stimulating the networking system, treating it either as a single
Device Under Test (DUT), or as a system of devices, a System Under
Test (SUT).


For software-based data-plane forwarding running on commodity x86/ARM
CPUs, the SUT comprises not only the forwarding application itself, the
DUT, but the entire execution environment: host hardware, firmware and
kernel/hypervisor services, as well as any other software workloads
that share the same CPUs, memory and I/O resources.

{::comment}

    MB28: This makes assumptions on the software architecture. We need to make sure this is generic enough.
    For example, what is a server? Etc.
    Does it applies to container, microservice, SF a la RFC7665, VNF a la ETSI, etc.?

    VP: Ask Maciek.

    MK: Rewritten it a bit to make it more generic. See if this helps.
    MK: Edited.

{:/comment}

Given that a SUT is a shared multi-tenant environment,

{::comment}

    MB29: Such as?

    VP: We should reformulate. Other components may differ (give few examples) but interference is general.

    MK: Removed surplus text, as it is now explained in preceding paragraph.
    MK: Edited.

{:/comment}

the DUT might inadvertently
experience interference from the operating system
or other software operating on the same server.

Some of this interference can be mitigated.
For instance, in multi-core CPU systems, pinning DUT program threads to
specific CPU cores

{::comment}

    MB30: If many? Or do we assume there are always many?

    VP: Reformulate.

    MK: Made it explicit for this paragraph.
    MK: Edited.

{:/comment}

and isolating those cores can prevent context switching.

Despite taking all feasible precautions, some adverse effects may still impact
the DUT's network performance.
In this document, these effects are collectively
referred to as SUT noise, even if the effects are not as unpredictable
as what other engineering disciplines call noise.

A DUT can also exhibit fluctuating performance itself,
for reasons not related to the rest of SUT. For example, this can be
due to pauses in execution as needed for internal stateful processing.
In many cases this may be an expected per-design behavior,
as it would be observable even in a hypothetical scenario
where all sources of SUT noise are eliminated.
Such behavior affects trial results in a way similar to SUT noise.
As the two phenomena are hard to distinguish,
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

In this simple model, a SUT does not have a single performance value, it has a spectrum.
One end of the spectrum is the idealized noiseless performance value,
the other end can be called a noiseful performance.
In practice, trial results close to the noiseful end of the spectrum
happen only rarely.
The worse a possible performance value is, the more rarely it is seen in a trial.
Therefore, the extreme noiseful end of the SUT spectrum is not observable
among trial results.

Furthermore, the extreme noiseless end of the SUT spectrum is unlikely
to be observable, this time because minor noise events almost always
occur during each trial, nudging the measured performance slightly
below the theoretical maximum.

{::comment}

    MB31: I don't parse this one. Please reword.

    VP: Ok.

    MK: Rephrased. Hope it reads better now.
    MK: Edited.

{:/comment}

Unless specified otherwise, this document's focus is
on the potentially observable ends of the SUT performance spectrum,
as opposed to the extreme ones.

When focusing on the DUT, the benchmarking effort should ideally aim
to eliminate only the SUT noise from SUT measurements.
However, this is currently not feasible in practice,
as there are no realistic enough models that would be capable
to distinguish SUT noise from DUT fluctuations
(based on the available literature at the time of writing).

{::comment}

    MB32: As we need to reflect the view of the WG/IETF, not only authors

    VP: Ask Maciek.

    MK: Proposed text looks good. OK.
    MK: Edited.

{:/comment}

Provided SUT execution environment and any co-resident workloads place
only negligible demands on SUT shared resources, so that

{::comment}

    MB33: That is?

    VP: Reformulate.

    MK: Clarified.
    MK: Edited.

{:/comment}

the DUT remains the principal performance limiter,
the DUT's ideal noiseless performance is defined

{::comment}

    MB34: Please avoid "we" constructs.

    VP: Ok. Search and replace all into passive voice.

    MK: for the whole document.

    VP: Done here, created separate comments elsewhere.

{:/comment}

as the noiseless end of the SUT performance spectrum

{::comment}

    MB35: Can we cite an example?

    VP: Yes for latency

    MK: Focus of mlrsearch is finding throughput. On 2nd thought,
          removing reference to latency as it is not applicable.
    MK: Edited.

{:/comment}

Note that by this definition, DUT noiseless performance
also minimizes the impact of DUT fluctuations, as much as realistically possible
for a given trial duration.

The MLRsearch methodology aims to solve the DUT in SUT problem
by estimating the noiseless end of the SUT performance spectrum
using a limited number of trial results.

Improvements to the throughput search algorithm, aimed at better dealing
with software networking SUT and DUT setups, should adopt methods that
explicitly model SUT-generated noise, enabling to derive surrogate
metrics that approximate the (proxies for) DUT noiseless performance
across a range of SUT noise-tolerance levels.

{::comment}

    MB36: ?

    VP: Reformulate.

    MK: Edited.

{:/comment}

## Repeatability and Comparability

[RFC2544] does not suggest repeating throughput search. Also, note that
from simply one discovered throughput value,
it cannot be determined how repeatable that value is.
Unsatisfactory repeatability then leads to unacceptable comparability,
as different benchmarking teams may obtain varying throughput values
for the same SUT, exceeding the expected differences from search precision.
Repeatability is important also when the test procedure is kept the same,
but SUT is varied in small ways. For example, during development
of software-based DUTs, repeatability is needed to detect small regressions.

[RFC2544] throughput requirements (60 seconds trial and
no tolerance of a single frame loss) affect the throughput result as follows:

The SUT behavior close to the noiseful end of its performance spectrum
consists of rare occasions of significantly low performance,
but the long trial duration makes those occasions not so rare on the trial level.
Therefore, the binary search results tend to wander away from the noiseless end
of SUT performance spectrum, more frequently and more widely than shorter
trials would, thus causing unacceptable throughput repeatability.

The repeatability problem can be better addressed by defining a search procedure
that identifies a consistent level of performance,
even if it does not meet the strict definition of throughput in [RFC2544].

According to the SUT performance spectrum model, better repeatability
will be at the noiseless end of the spectrum.
Therefore, solutions to the DUT in SUT problem
will help also with the repeatability problem.

Conversely, any alteration to [RFC2544] throughput search
that improves repeatability should be considered
as less dependent on the SUT noise.

An alternative option is to simply run a search multiple times, and
report some statistics (e.g., average and standard deviation, and/or
percentiles like p95).

{::comment}

    MB37: What about at some other representative percentiles?

    VP: Ok.

    MK: Added percentiles.
    MK: Edited.

{:/comment}

This can be used for a subset of tests deemed more important,
but it makes the search duration problem even more pronounced.

## Throughput with Non-Zero Loss

Section 3.17 of [RFC1242] defines throughput as:
    The maximum rate at which none of the offered frames
    are dropped by the device.

Then, it says:
    Since even the loss of one frame in a
    data stream can cause significant delays while
    waiting for the higher-level protocols to time out,
    it is useful to know the actual maximum data
    rate that the device can support.

However, many benchmarking teams accept a low,
non-zero loss ratio as the goal for their load search.

Motivations are many:

- Networking protocols tolerate frame loss better,

{::comment}

    MB38: 1242 was also modern at the time they were published ;)
            This can be easily stale. Let's avoid that

    VP: Ok.

    MK: OK.

{:/comment}

  compared to the time when [RFC1242] and [RFC2544] were specified.

- Increased link speeds require trials sending way more frames within the same duration,

{::comment}

    MB39: Won't age well.

    VP: Ok, but some things did change over time (in focus if not in existence). Ask Maciek.

    MK: Edited.

{:/comment}

  increasing the chance of a small SUT performance fluctuation
  being enough to cause frame loss.

- Because noise-related drops usually arrive in small bursts, their
  impact on the trial's overall frame loss ratio is diluted by the
  longer intervals in which the SUT operates close to its noiseless
  performance; consequently, the averaged Trial Loss Ratio can still
  end up below the specified Goal Loss Ratio value.

{::comment}

    MB40: Please split. Too long

    VP: At this point we probably should add a subsection somewhere,
          discussing how short-time performance may fluctuate within reasonable-duration trial
          (even as short as 1s).

    MK: Split with some rewording.
    MK: Edited.

{:/comment}

- If an approximation of the SUT noise impact on the Trial Loss Ratio is known,

{::comment}

    MB41: Help readers find where to look for an authoritative definition.

    VP: The original paragraph maybe describes periodic processes eating CPU or even impact
          of reconfiguration during traffic, but both may be too exotic for this specification.
          I recommend to delete this paragraph. Otherwise, add link.

    MK: Added.
    MK: Edited.

{:/comment}

  it can be set as the Goal Loss Ratio (see definitions of
  Trial and Goal terms in Sections 4.4 and 4.5 of this document).

{::comment}

    MB42: Help readers find where to look for an authoritative definition.

    VP: Add link if not deleted?

    MK: Added.
    MK: Edited.

{:/comment}

- For more information, see an earlier draft [Lencze-Shima] (Section 5)
  and references there.

Regardless of the validity of all similar motivations,
support for non-zero loss goals makes a

{::comment}

    MB43: We cant claim that

    VP: Ok, but also current sentence has circular dependency between non-zero rates
          and specific user-friendliness. Reformulate.

    MK: done.
    MK: Edited.

{:/comment}

search algorithm more user-friendly.
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

At the time of writing there does not seem to be a consensus in the industry

{::comment}

    MB44: Among?
    Also, indicate "at the time of writing".

    VP: Ok.

    MK: done.
    MK: Edited.

{:/comment}

on which ratio value is the best.
For users, performance of higher protocol layers is important, for
example, goodput of TCP connection (TCP throughput, [RFC6349]), but relationship
between goodput and loss ratio is not simple. Refer to
[Lencze-Kovacs-Shima] for examples of various corner cases,
Section 3 of [RFC6349] for loss ratios acceptable for an accurate
measurement of TCP throughput, and [Ott-Mathis-Semke-Mahdavi] for
models and calculations of TCP performance in presence of packet loss.

## Inconsistent Trial Results

While performing throughput search by executing a sequence of
measurement trials, there is a risk of encountering inconsistencies
between trial results.

Examples include, but are not limited to:

- A trial at the same load (same or different trial duration) results
  in a different Trial Loss Ratio.
- A trial at a larger load (same or different trial duration) results
  in a lower Trial Loss Ratio.

The plain bisection never encounters inconsistent trials.
But [RFC2544] hints about the possibility of inconsistent trial results,
in two places in its text.
The first place is Section 24 of [RFC2544],

{::comment}

    MB45: ??

    VP: Full reference is needed.

    MK: done.
    MK: Edited.

{:/comment}

where full trial durations are required,
presumably because they can be inconsistent with the results
from short trial durations.
The second place is Section 26.3 of [RFC2544],

{::comment}

    MB46: ??

    VP: Also full reference.

    MK: done.
    MK: Edited.

{:/comment}

where two successive zero-loss trials
are recommended, presumably because after one zero-loss trial
there can be a subsequent inconsistent non-zero-loss trial.

A robust throughput search algorithm needs to decide how to continue
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

# Requirements Language

{::comment}

    MB5: Move after the intro

    VP: Ok.

    MK: OK.
    MK: Moved.

    VP: Currently the "intro" is quite long, so moved after "problems" now
    so this is situated closer to Specification.

{:/comment}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in BCP 14 [RFC2119]

{::comment}

    The two references have to come one after another to avoid boilerplate nit,
    but the xml2rfc processing (web service) is buggy and strips rfc2119 brackets.
    Luckily, having this comment here avoids the bug and creates correct .xml file.

    VP: TODO: Verify the .txt render is still ok.

{:/comment}

[RFC8174] when, and only when, they appear in all capitals, as shown here.

This document is categorized as an Informational RFC.
While it does not mandate the adoption of the MLRsearch methodology,
it uses the normative language of BCP 14 to provide an unambiguous specification.
This ensures that if a test procedure or test report claims compliance with the MLRsearch Specification,
it MUST adhere to all the absolute requirements defined herein.
The use of normative language is intended to promote repeatable and comparable results
among those who choose to implement this methodology.

{::comment}

    VP: TODO: Mention conditional requirements if not clear from usage.
    For example, RFC 2544 Trial requirements must be either honored or deviations must be reported.

{:/comment}

# MLRsearch Specification

{::comment}

    VP: TODO: Explain there is no separate list for terminology,
    subsections under "Terms" sections are terminology items,
    packaged together with related requirements and discussions.

{:/comment}

This chapter provides all technical definitions
needed for evaluating whether a particular test procedure
complies with MLRsearch Specification.

Some terms used in the specification are capitalized.
It is just a stylistic choice for this document,
reminding the reader this term is introduced, defined or explained
elsewhere in the document.

Lowercase variants are equally valid.

{::comment}

    MB47: Please move this to the terminology section
    where we can group all conventions used in the document.

    VP: Ok.

    MK: There is no terminology section per se in this
          document. See my note to your comments in the Requirements Language
          section.

{:/comment}

Each per term subsection contains a short *Definition* paragraph
containing a minimal definition and all strict requirements, followed
by *Discussion* paragraphs focusing on important consequences and
recommendations. Requirements about how other components can use the
defined quantity are also included in the discussion.

{::comment}

    MB48: Not sure this brings much

    VP: Ok, delete.

    MK: done.
    MK: Edited.

{:/comment}

## Scope

This document specifies the Multiple Loss Ratio search (MLRsearch) methodology.
The MLRsearch Specification details a new class of benchmarks
by listing all terminology definitions and methodology requirements.
The definitions support "multi-goal" benchmarks, with "single-goal" as a subset.

The normative scope of this specification includes:

* The terminology for all required quantities and their attributes.

* An abstract architecture consisting of functional components
  (Manager, Controller, Measurer) and the requirements for their inputs and outputs.

* The required structure and attributes of the Controller Input,
  including one or more Search Goal instances.

* The required logic for Load Classification, which determines whether a given Trial Load
  qualifies as a Lower Bound or an Upper Bound for a Search Goal.

* The required structure and attributes of the Controller Output,
  including a Goal Result for each Search Goal.

#### Relationship to RFC 2544

MLRsearch Specification is an independent methodology and does not change or obsolete any part of [RFC2544].

This specification permits deviations from the Trial procedure as described in [RFC2544].
Any deviation from the [RFC2544] procedure MUST be documented explicitly
in the test report, and such variations remain outside the scope of the
original [RFC2544] benchmarks.

A specific single-goal MLRsearch benchmark can be configured to be compliant with [RFC2544] Throughput,
and most procedures reporting [RFC2544] Throughput can be adapted to satisfy also MLRsearch requirements
for specific search goal.

#### Applicability of Other Specifications

Methodology extensions from other BMWG documents that specify details for testing particular DUTs,
configurations, or protocols (e.g., by defining a particular Traffic Profile)
are considered orthogonal to MLRsearch and are applicable to a benchmark conducted using MLRsearch methodology.

#### Out of Scope

The following aspects are explicitly out of the normative scope of this document:

* This specification does not mandate or recommend any single,
  universal Search Goal configuration for all use cases.
  The selection of Search Goal parameters is left
  to the operator of the test procedure or may be defined by future specifications.

* The internal heuristics or algorithms used by the Controller to select Trial Input values
  (e.g., the load selection strategy) are considered implementation details.

* The potential for, and the effects of, interference between different Search Goal instances
  within a multiple-goal search are considered outside the normative scope of this specification.

## Architecture Overview

{::comment}

    TODO: Calls/invocations, interfaces.
    Low priority but useful for cleaning up the language.
    Maybe already fixed by MB49?

{:/comment}

While normative definitions and requirements only use already defined terms,
co-located discussion paragraphs are more useful on repeated reading
when they use terms defined later.
But for the first reading, such discussion paragraphs would be
unclead and confusing, so this informative section gives a brief
top-down overview of what a complete MLRsearch Architecture will look like.

MLRsearch Architecture describes a set of abstract system components,
acting as functions with specified inputs and outputs.

A Test Procedure is said to comply with MLRsearch Specification
if it can be conceptually divided into analogous components,
each satisfying requirements for the corresponding MLRsearch component.
Any such compliant Test Procedure is called a MLRsearch Implementation.

The Measurer component is tasked to perform Trials,
the Controller component is tasked to select Trial Durations and Loads,
the Manager component is tasked to pre-configure involved entities
and to produce the Test Report.
The Test Report explicitly states Search Goals (as Controller Input)
and corresponding Goal Results (Controller Output).

The Manager invokes

{::comment}

    MB49: Invoke?
            Maybe better to clarify what is actually meant by "calls".

    VP: Mention function calls in first sentence of this subsection.

    MK: done.
    MK: Edited.

{:/comment}

a Controller once,

{::comment}

    MB50: Is there only one? Always?
            Include a provision to have many

    VP: Add a sentence about one search.
          Complete test suite may perform multiple searches, using maybe different controllers

    MK: Not sure what you mean. It already says "stopping conditions",
          implying there are many.

{:/comment}

and the Controller then invokes the Measurer repeatedly
until every stopping condition is satisfied.

The part during which the Controller invokes the Measurer is termed the
Search. Any work the Manager performs either before invoking the
Controller or after Controller returns, falls outside the scope of the
Search.

MLRsearch Specification prescribes Regular Search Results and recommends
their stopping conditions.

{::comment}

    MB51: Does this also cover "abort" (before completion) to handle some error conditions?
            Or this is more a "stop execution"?

    VP: Add sentences about regular exits, irregular errors and user aborts?

    MK: Stop execution of the search.

{:/comment}

Irregular Search Results are also allowed,
they may have different requirements and stopping conditions.

Search Results are based on Load Classification. When measured enough,
a chosen Load can either achieve or fail each Search Goal
(separately), thus becoming a Lower Bound or an Upper Bound for that
Search Goal.

When the Relevant Lower Bound is close enough to Relevant Upper Bound
according to Goal Width, the Regular Goal Result is found.
Search stops when all Regular Goal Results are found,
or when some Search Goals are proven to have only Irregular Goal Results.

{::comment}

    Verify the language above is correct, minimal and enough as an overview
    when all definitions become stable.

{:/comment}

{::comment}

    Note:
    This comment was about load classifications being equivalent among implementations.
    We deleted tat sentence, keeping this block just for tracking purposes.

    MB52: Do we have taxonomoy/means to make that equivalence easy to put in place?

    VP: Add links to Goal Result or Load Classification.
          But maybe this sentence is not needed in this subsection?

    MK: It is covered in Sections 4.6.2 Load Classification and 6.1
          Load Classification Logic and 6.4.3 Load Classification
          Computations.

{:/comment}

{::comment}

    TODO: Repeating the same search is possible, this is about single search.

    Again, Test Suite subsection, and Test Report for scheduled tests.

{:/comment}

### Test Report

A primary responsibility of the Manager is to produce a Test Report,
which serves as the final and formal output of the test procedure.

This document does not provide a single, complete, normative definition
for the structure of the Test Report. Instead, normative requirements
on the content of the Test Report are specified throughout this document
in conjunction with the definitions of the quantities and procedures to which they apply.
Readers should note that any clause requiring a value to be "reported"
or "stated in the test report" constitutes a normative requirement
on the content of this final artifact.

### Behavior Correctness

MLRsearch Specification by itself does not guarantee that
the Search ends in finite time, as the freedom the Controller has
for Load selection also allows for clearly deficient choices.

{::comment}

    MB53: I suggest we be factual and avoid use of "believe" and so on.

    VP: Ok.

    MK: Ok.
    MK: Removed.

    VP: Verified, currently fixed everywhere.

{:/comment}

For deeper insights on these matters, refer to [FDio-CSIT-MLRsearch].

The primary MLRsearch Implementation, used as the prototype
for this specification, is [PyPI-MLRsearch].

## Quantities

MLRsearch Specification

{::comment}

    MB54: "S" is used in the previous section,
            Please pick one form and be consistent through the document.

    VP: S

    MK: MLRsearch Specification. Done all.
    MK: Edited.

{:/comment}

uses a number of specific quantities,
some of them can be expressed in several different units.

In general, MLRsearch Specification does not require particular units to be used,
but it is REQUIRED for the test report to state all the units.
For example, ratio quantities can be dimensionless numbers between zero and one,
but may be expressed as percentages instead.

For convenience, a group of quantities can be treated as a composite quantity.
One constituent

{::comment}

    MB55: Please check

    VP: Reformulate.

    MK: Fixed punctuation and broken sentence.
    MK: Edited.

{:/comment}

of a composite quantity is called an attribute.
A group of attribute values is called an instance of that composite quantity.

Some attributes may depend on others and can be calculated from other
attributes. Such quantities are called derived quantities.

### Current and Final Values

Some quantities are defined so that it is possible to compute their
values in the middle of a Search.  Other quantities are specified so
that their values can be computed only after a Search ends.  Some
quantities are important only after a Search ended, but their values
are computable also before a Search ends.

For a quantity that is computable before a Search ends,
the adjective **current** is used to mark a value of that quantity
available before the Search ends.
When such value is relevant for the search result, the adjective **final**
is used to denote the value of that quantity at the end of the Search.

If a time evolution of such a dynamic quantity is guided by
configuration quantities, those adjectives can be used to distinguish
quantities.  For example, if the current value of "duration"
(dynamic quantity) increases from "initial duration" to "final
duration"(configuration quantities), all the quoted names denote
separate but related quantities.  As the naming suggests, the final
value of "duration" is expected to be equal to "final duration" value.

{::comment}

    Terminology structure
    Second proposal:

    The normative part of the MLRsearch specification can be decomposed
    into a directed acyclic graph, where each node is a "term"
    with its definition and requirements. The links in the graph are
    dependencies, "later" term can only be fully defined
    when all its "earlier" terms are already defined.

    Some terms define composite quantities, subsections could be used
    to hold definitions of all the attributes.

    For readability, informative "discussion" text could be added,
    but frequently it is convenient to use a later term
    when discussing an earlier term.

    The currect structure of sections is a compromise between these motivations.

    VP: TODO: Describe this informal principle in official text?

    VP: TODO: Distinguish requirements from other discussions?

{:/comment}

## Existing Terms

{::comment}

    MB56: I would delete.

    VP: Not sure yet.

    MK: Edited, instead of deleting.
    MK: Edited.

{:/comment}

This specification relies on the following three documents that should
be consulted before attempting to make use of this document:

- "Benchmarking Terminology for Network Interconnect Devices" [RFC1242]
  contains basic term definitions.

- "Benchmarking Terminology for LAN Switching Devices" [RFC2285] adds
  more terms and discussions, describing some known network
  benchmarking situations in a more precise way.

- "Benchmarking Methodology for Network Interconnect Devices"
   [RFC2544] contains discussions about terms and additional
   methodology requirements.

Definitions of some central terms from above documents are copied and
discussed in the following subsections.

{::comment}

    MB57: Please move this to a terminology section suggested above

    VP: Ok for paragraph text...

    MK: See my note re your comment to the Requirements Language
          section. We ended up keeping the Existing Terms section just before
          the MLRsearch specific terms for clarity and easier reading, based
          on feedback from BMWG.

{:/comment}

### SUT

Defined in Section 3.1.2 of [RFC2285] as follows.

Definition:

&nbsp;
: The collective set of network devices to which stimulus is offered
as a single entity and response measured.

Discussion:

&nbsp;
: An SUT consisting of a single network device is allowed by this definition.

{::comment}

    MB58: Do we need to include this?
    I would only introduce deviation from base specs.

    VP: Ok on deviation, not sure on base definition.

    MK: We do need to include this, as the SUT and DUT terms are used
    repeatedly and are fundamental to understanding this
    specification.

    VP: Edited.

{:/comment}

&nbsp;
: In software-based networking SUT may comprise multitude of
networking applications and the entire host hardware and software
execution environment.

### DUT

Defined in Section 3.1.1 of [RFC2285] as follows.

Definition:

&nbsp;
: The network forwarding device

{::comment}

    MB59: This reasons about "device", should we say that we extends this to "function"?

    VP: Yes. Extend discussion. If device requires medium/cables,
          function can be working with something software-like
          (packet vectors, shared memory regions).

    MK: added text covering this.
    MK: Edited.

{:/comment}

to which stimulus is offered and response measured.

Discussion:

&nbsp;
: DUT, as a sub-component of SUT, is only indirectly mentioned in
MLRsearch Specification, but is of key relevance for its motivation.
The device can represent a software-based networking functions running
on commodity x86/ARM CPUs (vs purpose-built ASIC / NPU / FPGA).

{::comment}

    MB60: Idem as SUT

    VP: Yes.

    MK: See my note re SUT.

{:/comment}

### Trial

A trial is the part of the test described in Section 23 of [RFC2544].

Definition:

&nbsp;
: A particular test consists of multiple trials.  Each trial returns
one piece of information, for example the loss rate at a particular
input frame rate.  Each trial consists of a number of phases:

&nbsp;
: a) If the DUT is a router, send the routing update to the "input"
port and pause two seconds to be sure that the routing has settled.

&nbsp;
: b)  Send the "learning frames" to the "output" port and wait 2
seconds to be sure that the learning has settled.  Bridge learning
frames are frames with source addresses that are the same as the
destination addresses used by the test frames.  Learning frames for
other protocols are used to prime the address resolution tables in
the DUT.  The formats of the learning frame that should be used are
shown in the Test Frame Formats document.

&nbsp;
: c) Run the test trial.

&nbsp;
: d) Wait for two seconds for any residual frames to be received.

&nbsp;
: e) Wait for at least five seconds for the DUT to restabilize.

Discussion:

&nbsp;
: The traffic is sent only in phase c) and received in phases c) and d).

&nbsp;
: The definition describes some traits, and it is not clear whether all of them
are required, or some of them are only recommended.

&nbsp;
: Trials are the only stimuli the SUT is expected to experience during the Search.

{::comment}

    MB61: Is there any aspect new to MLRS?

    VP: No, make clear.

    MK: Yes, it is covered in detail in the following sections. The
          important part in this section, apart from quoting the original
          definition, is the discussion part, that sets the convention of how
          deviations from the original definition are captured in this
          document.

{:/comment}

&nbsp;
: For the purposes of the MLRsearch Specification,
it is allowed

{::comment}

    MB62: Not a normative language

    VP: Reformulate.

    MK: ok. changed from ALLOWED to allowed. is anything else needed?
    MK: Edited.

    VP: I feel this is important. Not only as a notable deviation from RFC 2544,
    but also as an example of normative language usage.
    Where RFC 2544 says you MUST do A or you CANNOT do B,
    MLRsearch may say there are specific conditions where you do not have to do A or can de B.
    Med had few comments like "since there is exception, the requirement is not universal",
    and I say "there are clear conditions, the requirement is universal if the conditions are satisfied".

    VP: TODO: Contruct appropriate "conditional requirement" sentence.

{:/comment}

&nbsp;
: for the test procedure to deviate from the [RFC2544] description,
but any such deviation MUST be described explicitly in the test report.

&nbsp;
: In some discussion paragraphs, it is useful to consider the traffic
as sent and received by a tester, as implicitly defined
in Section 6 of [RFC2544].

&nbsp;
: An example of deviation from [RFC2544] is using shorter wait times,
compared to those described in phases a), b), d) and e).

&nbsp;
: The [RFC2544] document itself seems to be treating phase b)
as any type of configuration that cannot be configured only once (by Manager,
before Search starts), as some crucial SUT state could time-out during the Search.
It is RECOMMENDED

{::comment}

    MB63: Not a normative term

    VP: Ok.

    MK: ok. MB and MK edits applied.
    MK: Edited.

{:/comment}

&nbsp;
: to interpret the "learning frames" to be
any such time-sensitive per-trial configuration method,
with bridge MAC learning being only one possibe example.
Appendix C.2.4.1 of [RFC2544] lists another example: ARP with wait time of 5 seconds.

{::comment}

    VP: TODO: Emphasize that this is a single trial.
    Any recurring tests count as separate trials,
    because they give different results.

{:/comment}

## Trial Terms

{::comment}

    TODO: Separate short description from further discussion.

{:/comment}

This section defines new and redefine existing terms for quantities
relevant as inputs or outputs of a Trial, as used by the Measurer component.
This includes also any derived quantities related to one trial result.

### Trial Duration

Definition:

&nbsp;
: Trial Duration is the intended duration of the phase c) of a Trial.
The value MUST be positive.

{::comment}

    MB64: Does this cover also recurrences?
            See, e.g., draft-ietf-netmod-schedule-yang-05 - A Common YANG Data Model for Scheduling
            or draft-ietf-opsawg-scheduling-oam-tests-00?

    VP: No, mention that probably already in trial definition.

    MK: No, it does not cover recurrences as specified in above two
          drafts, as it does involve scheduled events.

    VP: Created comment block at appropriate subsections.

{:/comment}

Discussion:

&nbsp;
: While any positive real value may be provided, some Measurer
implementations MAY limit possible values, e.g., by rounding down to
nearest integer in seconds.  In that case, it is RECOMMENDED to give
such inputs to the Controller so that the Controller only uses 

{::comment}

    MB65: To?

    VP: Reformulate.

    MK: Edited "proposes" => "uses".
    MK: Edited.

{:/comment}

&nbsp;
: the accepted values.

### Trial Load

Definition:

&nbsp;
: Trial Load is the per-interface Intended Load for a Trial.

Discussion:

&nbsp;
: For test report purposes, it is assumed that this is a constant load by default,
as specified in Section 3.4 of [RFC1242]).

{::comment}

    MB66: Please fix all similar ones in the doc

    VP: Ok.

    MK: ok. fixed only here for now.
    MK: TODO fix everywhere.
    MK: Edited.

{:/comment}

&nbsp;
: Trial Load MAY be an average load performed with steady state traffic or
with repeated bursts of frames

{::comment}

    MB67: Example of an example. :) Please reword.

    VP: Ok.

    MK: Edited.

{:/comment}

&nbsp;
: e.g., as suggested in Section 21 of [RFC2544].
In the case of a non-constant load, the test report
MUST explicitly mention how exactly non-constant the traffic is.

{::comment}

    MB68: Can we also cover load percentiles?
            The avg may not be representative to stress functions
            with anti-ddos guards, for example.

    VP: Not here. The average woks with aggregate counters used in loss definition.
          Maybe discuss anti-ddos in Traffic Profile subsection.

    MK: Definition of burst traffic profiles is out of scope.

    VP: TODO: Re-check the current text.

{:/comment}

&nbsp;
: Trial Load is equivalent to the quantities defined
as constant load (Section 3.4 of [RFC1242]),
data rate (Section 14 of [RFC2544]),
and Intended Load (Section 3.5.1 of [RFC2285]),
in the sense that all three definitions specify that this value
applies to one (input or output) interface.

&nbsp;
: Similarly to Trial Duration, some Measurers MAY limit the possible values
of trial load. Contrary to trial duration,

{::comment}

    MB69: Inappropriate use of normative language

    VP: Maybe disagree?
          Reformulate other parts to stress test report is subject to requirements.

    MK: Edited.

{:/comment}

&nbsp;
: documenting such behavior in the test report is OPTIONAL.
This is because the load differences are negligible (and frequently
undocumented) in practice.

&nbsp;
: It is allowed to combine Trial Load and Trial Duration values in a way
that would not be possible to achieve using any integer number of data frames.

{::comment}

    VP: TODO: Use normative MAY somewhere.

{:/comment}

&nbsp;
: If a particular Trial Load value is not tied to a single Trial,
e.g., if there are no Trials yet or if there are multiple Trials,
this document uses a shorthand **Load**.

&nbsp;
: The test report MAY present the aggregate load across multiple
interfaces, treating it as the same quantity expressed using different
units.  Each reported Trial Load value MUST state unambiguously whether
it refers to (i) a single interface, (ii) a specified subset of
interfaces (e.g., such as all logical interfaces mapped to one physical
port), or (iii) the total across every interface. For any aggregate
load value, the report MUST also give the fixed conversion factor that
links the per-interface and multi-interface load values.

{::comment}

    MB70: The causality effect may not be evident for the subset case, at least.

    VP: Reformulate.

    MK: Edited.

{:/comment}

&nbsp;
: The per-interface value remains the primary one, consistent
with prevailing practice in [RFC 1242], [RFC 2544], and [RFC 2285].

{::comment}

    MB71: Which ones?

    VP: List the common examples.

    MK: Edited.

{:/comment}

&nbsp;
: The last paragraph also applies to other terms related to Load.

### Trial Input

Definition:

&nbsp;
: Trial Input is a composite quantity, consisting of two attributes:
Trial Duration and Trial Load.

Discussion:

&nbsp;
: When talking about multiple Trials, it is common to say "Trial Inputs"
to denote all corresponding Trial Input instances.

&nbsp;
: A Trial Input instance acts as the input for one call of the Measurer component.

&nbsp;
: Contrary to other composite quantities, MLRsearch Implementations
MUST NOT add optional attributes here.
This improves interoperability between various implementations of
a Controller and a Measurer.

&nbsp;
: Note that both attributes are **intended** quantities,
as only those can be fully controlled by the Controller.
The actual offered quantities, as realized by the Measurer, can be different
(and must be different if not multiplying into integer number of frames),
but questions around those offered quantities are generally
outside of the scope of this document.

### Traffic Profile

Definition:

&nbsp;
: Traffic Profile is a composite quantity containing
all attributes other than Trial Load and Trial Duration,
that are needed for unique determination of the Trial to be performed.

Discussion:

&nbsp;
: All the attributes are assumed to be constant during the search,
and the composite is configured on the Measurer by the Manager
before the Search starts.
This is why the traffic profile is not part of the Trial Input.

&nbsp;
: Therefore, implementations of the Manager and the Measurer
must be aware of their common set of capabilities,

{::comment}

    MB72: Can we provide an example how to make that?

    VP: Nope. Say it is an integration effort.

    MK: Edited.

{:/comment}

&nbsp;
: so that Traffic Profile
instance uniquely defines the traffic during the Search making the Manager and the Measurer simple to integrate.
None of those capabilities
have to be known by the Controller implementations.

&nbsp;
: Specification of traffic properties included in the Traffic Profile is
out of scope of this document.

{::comment}

    MB73: This is too vague. Unless we reword top better reflect the requirement,
            I don't think we can use the normative language here

    VP: Reformulate.

    MK: Edited.

{:/comment}

&nbsp;
: Examples of traffic properties include:
- Data link frame size
  - Fixed sizes as listed in Section 3.5 of [RFC1242] and in Section
    9 of [RFC2544]
  - mixed sizes as defined in [RFC6985] "IMIX Genome: Specification of
    Variable Packet Size for Additional Testing"
- Frame formats and protocol addresses
  - Section 8, 12 and Appendix C of [RFC2544]
- Symmetric bidirectional traffic
  - Section 14 of [RFC2544].

{::comment}

    MB74: Inappropriate use of normative language

    VP: Reformulate.

    MK: Edited.

{:/comment}

{::comment}

    MB75: Idem as above. MUST is not appropriate here.

    VP: Reformulate.

    MK: Edited.

{:/comment}

&nbsp;
: Other traffic properties that need to be somehow specified in Traffic
Profile, if they apply to the test scenario, include:

&nbsp;
: - bidirectional traffic from Section 14 of [RFC2544],
- fully meshed traffic from Section 3.3.3 of [RFC2285],
- modifiers from Section 11 of [RFC2544].

{::comment}

    TODO: Multiple traffic profiles (at least frame sizes) in RFC2544,
    this is about single SUT+config+profile benchmark.

{:/comment}

### Trial Forwarding Ratio

Definition:

&nbsp;
: The Trial Forwarding Ratio is a dimensionless floating point value.
It MUST range between 0.0 and 1.0, both inclusive.
It is calculated by dividing the number of frames
successfully forwarded by the SUT
by the total number of frames expected to be forwarded during the trial.

Discussion:

&nbsp;
: For most Traffic Profiles, "expected to be forwarded" means
"intended to get received by SUT from tester".
Only if this is not the case, the test report SHOULD describe the Traffic Profile

{::comment}

    MB76: MUST is an absolute requirement (i.e., there is no exception):
            1. MUST This word, or the terms "REQUIRED" or "SHALL",
            mean that the definition is an absolute requirement of
            the specification.
            SHOULD This word, or the adjective "RECOMMENDED",
            mean that there may exist valid reasons in particular
            circumstances to ignore a particular item, but the full
            implications must be understood and carefully weighed
            before choosing a different course.

    VP: Reformulate.

    MK: Edited.

    VP: TODO: Apply stricter conditional requirements.

{:/comment}

&nbsp;
: in a way that implies how Trial Forwarding Ratio should be calculated.

&nbsp;
: Trial Forwarding Ratio MAY be expressed in other units
(e.g., as a percentage) in the test report.

&nbsp;
: Note that, contrary to Load terms, frame counts used to compute
Trial Forwarding Ratio are generally aggregates over all SUT output interfaces,
as most test procedures verify all outgoing frames.

{::comment}

    MB77: Should we call for more granularity to be provided/characterized?

    VP: No, include sentence on why.

    MK: What is the granularity that is needed here? The test
          procedure is about testing SUT as a single system, not parts of
          it.

    VP: TODO: Add the missing sentence.

{:/comment}

&nbsp;
: For example, in a test with symmetric bidirectional traffic,
if one direction is forwarded without losses, but the opposite direction
does not forward at all, the trial forwarding ratio would be 0.5 (50%).

### Trial Loss Ratio

Definition:

&nbsp;
: The Trial Loss Ratio is equal to one minus the Trial Forwarding Ratio.

{::comment}

    MB78: For all sections, please indent so that we separate the def/discussion vs. description

    VP: Ok.

    MK: Edited. Indented 2 spaces, will kramdown renderer take it?

    VP: Applied the way from https://stackoverflow.com/a/59612110 instead.

{:/comment}

Discussion:

&nbsp;
: 100% minus the Trial Forwarding Ratio, when expressed as a percentage.

&nbsp;
: This is almost identical to Frame Loss Rate of [RFC1242](Section 3.6).
The only minor differences are that Trial Loss Ratio does not need to
be expressed as a percentage, and Trial Loss Ratio is explicitly
based on aggregate frame counts.

### Trial Forwarding Rate

Definition:

&nbsp;
: The Trial Forwarding Rate is a derived quantity, calculated by
multiplying the Trial Load by the Trial Forwarding Ratio.

Discussion:

&nbsp;
: This quantity is not identical
to the Forwarding Rate as defined in Section 3.6.1 of [RFC2285].
Specifically, the latter is based on frame counts on one output interface only,
so each output interface can have different forwarding rate,
whereas the Trial Forwarding Rate is based on frame counts
aggregated over all SUT output interfaces, while still being a multiple of Load.

&nbsp;
: Consequently, for symmetric bidirectional Traffic Profiles (section 14
of [RFC2544],

{::comment}

    MB79: Do we have an authoritative reference where this is defined?
            If not, please add an definition entry early in the terminology section.

    VP: Add reference.

    MK: Edited. Added reference to RFC2544.

{:/comment}

&nbsp;
: the Trial Forwarding Rate value is equal to the arithmetic average
of [RFC2285] Forwarding Rate values across all SUT output interfaces.

{::comment}

    MB80: Why both?

    VP: Add explanations to Traffic Profile subsection.

    MK: Edited. But shouldn't it say "sum of" instead of "arithmetic
          average"? Unless specified, Trial Forwarding Rate is an aggregate
          rate, not per interface, as it is representating capability of
          DUT/SUT not a subset of it associated with particular interface :)

    VP: TODO: Re-check.

{:/comment}

&nbsp;
: Given that Trial Forwarding Rate is a quantity based on Load,
this quantity may be expressed using multi-interface values
in test report (e.g., as sum of per-interface forwarding rate values).

### Trial Effective Duration

Definition:

&nbsp;
: Trial Effective Duration is a time quantity related to the non-recurring trial,
by default equal to the Trial Duration.

{::comment}

    MB81: For the periodic/recurrences, does it cover only one recurrence
            or from start to last independent of in-between execution periods?

    VP: Make sure Trial implies no recurrence.

    MK: Edited. BUT - Why do we need to state that. There is nothing in the text of
          Section 23 of RFC2544 and in above sections implying recurrences.
          Why then do we need to explicity say "no recurrence"?

    VP: TODO: After Trial is stable, simplifi this sentence.

{:/comment}

Discussion:

&nbsp;
: This is an optional feature.
If the Measurer does not return any Trial Effective Duration value,
the Controller MUST use the Trial Duration value instead.

&nbsp;
: Trial Effective Duration may be any positive time quantity

{::comment}

    MB82: It is obvious, but should we say "positive"?

    VP: Yes.

    MK: Edited.

{:/comment}

&nbsp;
: chosen by the Measurer
to be used for time-based decisions in the Controller.

&nbsp;
: The test report MUST explain how the Measurer computes the returned
Trial Effective Duration values, if they are not always
equal to the Trial Duration.

&nbsp;
: This feature can be beneficial for users of testing equipment

{::comment}

    MB83: To be defined early in the terminology section

    VP: Ok.

    MK: Edited.

{:/comment}

&nbsp;
: who wish to manage the overall search duration,
rather than solely the traffic portion of it.
An approach is to measure the duration of the whole trial (including all wait times)
and use that as the Trial Effective Duration.

&nbsp;
: This is also a way for the Measurer to inform the Controller about
its surprising behavior, for example, when rounding the Trial Duration value.

### Trial Output

Definition:

&nbsp;
: Trial Output is a composite quantity consisting of several attributes. 

&nbsp;
: Required attributes are: Trial Loss Ratio, Trial Effective Duration and
Trial Forwarding Rate.

Discussion:

&nbsp;
: When referring to more than one trial, plural term "Trial Outputs" is
used to collectively describe multiple Trial Output instances.

&nbsp;
: Implementations may provide additional optional attributes.
The Controller implementations SHOULD

{::comment}

    MB84: As we have an exception

    VP: Reformulate.
          Conditional MUST has an authoritative prescribed condition,
          SHOULD gives implementers freedom to choose their own conditions.

    MK: Edited.

    VP: TODO: Apply stricter conditional requirements.

{:/comment}

&nbsp;
: ignore values of any optional attribute
they are not familiar with,
except when passing Trial Output instances to the Manager.

&nbsp;
: Example of an optional attribute:
The aggregate number of frames expected to be forwarded during the trial,
especially if it is not (a rounded-down value)
implied by Trial Load and Trial Duration.

&nbsp;
: While Section 3.5.2 of [RFC2285] requires the Offered Load value
to be reported for forwarding rate measurements,
it is not required in MLRsearch Specification,
as search results do not depend on it.

### Trial Result

Definition:

&nbsp;
: Trial Result is a composite quantity,
consisting of the Trial Input and the Trial Output.

Discussion:

&nbsp;
: When referring to more than one trial, plural term "Trial Results" is
used to collectively describe multiple Trial Result instances.

&nbsp;
: While implementations SHOULD NOT include additional attributes
with independent values,

{::comment}

    MB85: Can we include a short sentence to explain the risk if not followed?

    VP: Now I think even SHOULD NOT is too strong. Either way, reformulate.

    MK: For Vratko. Isn't this already covered in Trial Output? What
          other optional attributes are applicable here, give examples?
          Otherwise it's too abstract, open-ended, ambiguous and so on ... 
          Many other blue-sky and hand-wavy adjectives come to my mind :)

    VP: Re-check.

{:/comment}

&nbsp;
: they MAY include derived quantities.

## Goal Terms

This section defines new terms for quantities relevant (directly or indirectly)
for inputs and outputs of the Controller component.

Several goal attributes are defined before introducing
the main composite quantity: the Search Goal.

Contrary to other sections, definitions in subsections of this section
are necessarily vague, as their fundamental meaning is to act as
coefficients in formulas for Controller Output, which are not defined yet.

The discussions in this section relate the attributes to concepts mentioned in Section
[Overview of RFC 2544 Problems](#overview-of-rfc-2544-problems), but even these discussion
paragraphs are short, informal, and mostly referencing later sections,
where the impact on search results is discussed after introducing
the complete set of auxiliary terms.

### Goal Final Trial Duration

Definition:

&nbsp;
: Minimal value for Trial Duration that must be reached.
The value MUST be positive.

Discussion:

&nbsp;
: Certain trials must reach this minimum duration before a load can be
classified as a lower bound.

{::comment}

    MB86: I don't parse this.

    VP: Reformulate.

    MK: Edited.

{:/comment}

&nbsp;
: The Controller may choose shorter durations,
results of those may be enough for classification as an Upper Bound.

&nbsp;
: It is RECOMMENDED for all search goals to share the same
Goal Final Trial Duration value. Otherwise, Trial Duration values larger than
the Goal Final Trial Duration may occur, weakening the assumptions
the [Load Classification Logic](#load-classification-logic) is based on.

### Goal Duration Sum

Definition:

&nbsp;
: A threshold value for a particular sum of Trial Effective Duration values.
The value MUST be positive.

{::comment}

    MB87: I like this, but we should be consistent
    and mention it when appropriate for all other metrics

    VP: Ok. Check everywhere.

    MK: Checked all subsections under Goal Terms and Trial Terms.
          Applied as appropriate.

{:/comment}

Discussion:

&nbsp;
: Informally, this prescribes the sufficient number of trials performed
at a specific Trial Load and Goal Final Trial Duration during the search.

&nbsp;
: If the Goal Duration Sum is larger than the Goal Final Trial Duration,
multiple trials may be needed to be performed at the same load.

&nbsp;
: Refer to Section [MLRsearch Compliant with TST009](#mlrsearch-compliant-with-tst009)
for an example where the possibility of multiple trials
at the same load is intended.

&nbsp;
: A Goal Duration Sum value shorter than the Goal Final Trial Duration
(of the same goal) could save some search time, but is NOT RECOMMENDED,
as the time savings come at the cost of decreased repeatability.

&nbsp;
: In practice, the Search can spend less than Goal Duration Sum measuring
a Load value when the results are particularly one-sided,
but also, the Search can spend more than Goal Duration Sum measuring a Load
when the results are balanced and include
trials shorter than Goal Final Trial Duration.

### Goal Loss Ratio

Definition:

&nbsp;
: A threshold value for Trial Loss Ratio values.
The value MUST be non-negative and smaller than one.

Discussion:

&nbsp;
: A trial with Trial Loss Ratio larger than this value
signals the SUT may be unable to process this Trial Load well enough.

&nbsp;
: See [Throughput with Non-Zero Loss](#throughput-with-non-zero-loss)
for reasons why users may want to set this value above zero.

&nbsp;
: Since multiple trials may be needed for one Load value,
the Load Classification may be more complicated than mere comparison
of Trial Loss Ratio to Goal Loss Ratio.

### Goal Exceed Ratio

Definition:

&nbsp;
: A threshold value for a particular ratio of sums
of Trial Effective Duration values.
The value MUST be non-negative and smaller than one.

Discussion:

&nbsp;
: Informally, up to this proportion of Trial Results
with Trial Loss Ratio above Goal Loss Ratio is tolerated at a Lower Bound.
This is the full impact if every Trial was measured at Goal Final Trial Duration.
The actual full logic is more complicated, as shorter Trials are allowed.

&nbsp;
: For explainability reasons, the RECOMMENDED value for exceed ratio is 0.5 (50%),
as in practice that value leads to
the smallest variation in overall Search Duration.

&nbsp;
: Refer to Section [Exceed Ratio and Multiple Trials](#exceed-ratio-and-multiple-trials)
for more details.

### Goal Width

Definition:

&nbsp;
: A threshold value for deciding whether two Trial Load values are close enough.
This is an OPTIONAL attribute. If present, the value MUST be positive.

Discussion:

&nbsp;
: Informally, this acts as a stopping condition,
controlling the precision of the search result.
The search stops if every goal has reached its precision.

&nbsp;
: Implementations without this attribute
MUST provide the Controller with other means to control the search stopping conditions.

&nbsp;
: Absolute load difference and relative load difference are two popular choices,
but implementations may choose a different way to specify width.

&nbsp;
: The test report MUST make it clear what specific quantity is used as Goal Width.

&nbsp;
: It is RECOMMENDED to express Goal Width as a relative difference and
setting it to a value not lower than the Goal Loss Ratio.

&nbsp;
: Refer to Section 
[Generalized Throughput](#generalized-throughput) for more elaboration on the reasoning.

### Goal Initial Trial Duration

Definition:

&nbsp;
: Minimal value for Trial Duration suggested to use for this goal.
If present, this value MUST be positive.

Discussion:

&nbsp;
: This is an example of an optional Search Goal.

&nbsp;
: A typical default value is equal to the Goal Final Trial Duration value.

&nbsp;
: Informally, this is the shortest Trial Duration the Controller should select
when focusing on the goal.

&nbsp;
: Note that shorter Trial Duration values can still be used,
for example, selected while focusing on a different Search Goal.
Such results MUST be still accepted by the Load Classification logic.

&nbsp;
: Goal Initial Trial Duration is a mechanism for a user to discourage
trials with Trial Duration values deemed as too unreliable
for a particular SUT and a given Search Goal.

### Search Goal

Definition:

&nbsp;
The Search Goal is a composite quantity consisting of several attributes,
some of them are required.

&nbsp;
: Required attributes: Goal Final Trial Duration, Goal Duration Sum, Goal
Loss Ratio and Goal Exceed Ratio.

{::comment}

    MB88: Listing the attributes this way allows to easily classify mandatory/optional.
            However, this not followed in previous. Please pick your favorite approach
            and use it in a consistent manner in the document.

    VP: Use this longer way everywhere (also saying if no other attributes could be added).
          Tangent: Be more lenient on attributes internal to Controller?

    MK: Edited this one. Applied to subsections in Trial Terms and
          Goal Terms as appropriate. TODO check if more places need this.

{:/comment}

&nbsp;
: Optional attributes: Goal Initial Trial Duration and Goal Width.

Discussion:

&nbsp;
: Implementations MAY add their own attributes.
Those additional attributes may be required by an implementation
even if they are not required by MLRsearch Specification.
However, it is RECOMMENDED for those implementations
to support missing attributes by providing typical default values.

{::comment}

    MB89: I guess I understand what is meant here, but I think this should be reworded
            to avoid what can be seen as inconsistency: do not support vs. support a default.

    VP: Yes, probably worth a separate subsection,
          distinguishing automated implementations from manual processes.

    MK: No separate subsection. We should state that that the listed
          optional attributes should have documented default values. But i do
          not like the open-ended "Implementations MAY add their own
          attributes." Either examples are added or this sentence is
          removed.

    VP: TODO: Check if Specification does not mention "implementation".

{:/comment}

&nbsp;
: For example, implementations with Goal Initial Trial Durations
may also require users to specify "how quickly" should Trial Durations increase.

Refer to Section [Compliance](#compliance) for important Search Goal settings.

### Controller Input

Definition:

&nbsp;
: Controller Input is a composite quantity
required as an input for the Controller.
The only REQUIRED attribute is a list of Search Goal instances.

Discussion:

&nbsp;
: MLRsearch Implementations MAY use additional attributes.
Those additional attributes may be required by an implementation
even if they are not required by MLRsearch Specification.

&nbsp;
: Formally, the Manager does not apply any Controller configuration
apart from one Controller Input instance.

&nbsp;
: For example, Traffic Profile is configured on the Measurer by the Manager,
without explicit assistance of the Controller.

&nbsp;
: The order of Search Goal instances in a list SHOULD NOT
have a big impact on Controller Output,
but MLRsearch Implementations MAY base their behavior on the order
of Search Goal instances in a list.

#### Max Load

Definition:

&nbsp;
: Max Load is an optional attribute of Controller Input.
It is the maximal value the Controller is allowed to use for Trial Load values.

Discussion:

{::comment}

    VP: TODO: Use MUST NOT to make Controller behavior constrained, conditionally?

{:/comment}

&nbsp;
: Max Load is an example of an optional attribute (outside the list of Search Goals)
required by some implementations of MLRsearch.

&nbsp;
: In theory, each search goal could have its own Max Load value,
but as all Trial Results are possibly affecting all Search Goals,
it makes more sense for a single Max Load value to apply
to all Search Goal instances.

&nbsp;
: While Max Load is a frequently used configuration parameter, already governed
(as maximum frame rate) by [RFC2544] (Section 20)
and (as maximum offered load) by [RFC2285] (Section 3.5.3),
some implementations may detect or discover it
(instead of requiring a user-supplied value).

&nbsp;
: In MLRsearch Specification, one reason for listing
the [Relevant Upper Bound](#relevant-upper-bound) as a required attribute
is that it makes the search result independent of Max Load value.

&nbsp;
: Given that Max Load is a quantity based on Load,
it is allowed to express this quantity using multi-interface values
in test report, e.g., as sum of per-interface maximal loads.

{::comment}

    VP: TODO: Use MAY.

{:/comment}

#### Min Load

Definition:

&nbsp;
: Min Load is an optional attribute of Controller Input.
It is the minimal value the Controller is allowed to use for Trial Load values.

Discussion:

{::comment}

    VP: TODO: Use MUST NOT?

{:/comment}

&nbsp;
: Min Load is another example of an optional attribute
required by some implementations of MLRsearch.
Similarly to Max Load, it makes more sense to prescribe one common value,
as opposed to using a different value for each Search Goal.

&nbsp;
: Min Load is mainly useful for saving time by failing early,
arriving at an Irregular Goal Result when Min Load gets classified
as an Upper Bound.

&nbsp;
: For implementations, it is RECOMMENDED to require Min Load to be non-zero
and large enough to result in at least one frame being forwarded
even at shortest allowed Trial Duration,
so that Trial Loss Ratio is always well-defined,
and the implementation can apply relative Goal Width safely.

&nbsp;
: Given that Min Load is a quantity based on Load,
it is allowed to express this quantity using multi-interface values
in test report, e.g., as sum of per-interface minimal loads.

{::comment}

    VP: TODO: Use MAY.

{:/comment}

## Auxiliary Terms

While the terms defined in this section are not strictly needed
when formulating MLRsearch requirements, they simplify the language used
in discussion paragraphs and explanation sections.

### Trial Classification

When one Trial Result instance is compared to one Search Goal instance,
several relations can be named using short adjectives.

As trial results do not affect each other, this **Trial Classification**
does not change during a Search.

#### High-Loss Trial

A trial with Trial Loss Ratio larger than a Goal Loss Ratio value
is called a **high-loss trial**, with respect to given Search Goal
(or lossy trial, if Goal Loss Ratio is zero).

#### Low-Loss Trial

If a trial is not high-loss, it is called a **low-loss trial**
(or zero-loss trial, if Goal Loss Ratio is zero).

#### Short Trial

A trial with Trial Duration shorter than the Goal Final Trial Duration
is called a **short trial** (with respect to the given Search Goal).

#### Full-Length Trial

A trial that is not short is called a **full-length** trial.

Note that this includes Trial Durations larger than Goal Final Trial Duration.

#### Long Trial

A trial with Trial Duration longer than the Goal Final Trial Duration
is called a **long trial**.

### Load Classification

When a set of all Trial Result instances, performed so far
at one Trial Load, is compared to one Search Goal instance,
their relation can be named using the concept of a bound.

In general, such bounds are a current quantity,
even though cases of a Load changing its classification more than once
during the Search is rare in practice.

#### Upper Bound

Definition:

&nbsp;
: A Load value is called an Upper Bound if and only if it is classified
as such by [Appendix A](#appendix-a-load-classification)
algorithm for the given Search Goal at the current moment of the Search.

Discussion:

&nbsp;
: In more detail, the set of all Trial Result instances
performed so far at the Trial Load (and any Trial Duration)
is certain to fail to uphold all the requirements of the given Search Goal,
mainly the Goal Loss Ratio in combination with the Goal Exceed Ratio.
In this context, "certain to fail" relates to any possible results within the time
remaining till Goal Duration Sum.

&nbsp;
: One search goal can have multiple different Trial Load values
classified as its Upper Bounds.
While search progresses and more trials are measured,
any load value can become an Upper Bound in principle.

&nbsp;
: Moreover, a load can stop being an Upper Bound, but that
can only happen when more than Goal Duration Sum of trials are measured
(e.g., because another Search Goal needs more trials at this load).
In practice, the load becomes a Lower Bound (Section 4.6.2.2),
and we say the previous Upper Bound got Invalidated.

{::comment}

    VP: TODO: Reformulate to avoid the "we" construct.

    VP: TODO: Do we need Invalidation as a separate term? I guess no.

{:/comment}

#### Lower Bound

Definition:

&nbsp;
: A Load value is called a Lower Bound if and only if it is classified
as such by [Appendix A](#appendix-a-load-classification)
algorithm for the given Search Goal at the current moment of the search.

Discussion:

&nbsp;
: In more detail, the set of all Trial Result instances
performed so far at the Trial Load (and any Trial Duration)
is certain to uphold all the requirements of the given Search Goal,
mainly the Goal Loss Ratio in combination with the Goal Exceed Ratio.
Here "certain to uphold" relates to any possible results within the time
remaining till Goal Duration Sum.

&nbsp;
: One search goal can have multiple different Trial Load values
classified as its Lower Bounds.
As search progresses and more trials are measured,
any load value can become a Lower Bound in principle.

&nbsp;
: No load can be both an Upper Bound and a Lower Bound for the same Search goal
at the same time, but it is possible for a larger load to be a Lower Bound
while a smaller load is an Upper Bound.

&nbsp;
: Moreover, a load can stop being a Lower Bound, but that
can only happen when more than Goal Duration Sum of trials are measured
(e.g., because another Search Goal needs more trials at this load).
In that case, the load becomes an Upper Bound,
and we say the previous Lower Bound got Invalidated.

{::comment}

    Same as in upper bound:

    VP: TODO: Reformulate to avoid the "we" construct.

    VP: TODO: Do we need Invalidation as a separate term? I guess no.

{:/comment}

#### Undecided

Definition:

&nbsp;
: A Load value is called Undecided if it is currently
neither an Upper Bound nor a Lower Bound.

Discussion:

&nbsp;
: A Load value that has not been measured so far is Undecided.

&nbsp;
: It is possible for a Load to transition from an Upper Bound to Undecided
by adding Short Trials with Low-Loss results.
That is yet another reason for users to avoid using Search Goal instances
with different Goal Final Trial Duration values.

## Result Terms

Before defining the full structure of a Controller Output,
it is useful to define the composite quantity, called Goal Result.
The following subsections define its attribute first,
before describing the Goal Result quantity.

There is a correspondence between Search Goals and Goal Results.
Most of the following subsections refer to a given Search Goal,
when defining their terms.
Conversely, at the end of the search, each Search Goal instance
has its corresponding Goal Result instance.

### Relevant Upper Bound

Definition:

&nbsp;
: The Relevant Upper Bound is the smallest Trial Load value
classified as an Upper Bound for a given Search Goal at the end of the Search.

Discussion:

&nbsp;
: If no measured load had enough High-Loss Trials,
the Relevant Upper Bound MAY be non-existent.
For example, when Max Load is classified as a Lower Bound.

&nbsp;
: Conversely, when Relevant Upper Bound does exist,
it is not affected by Max Load value.

&nbsp;
: Given that Relevant Upper Bound is a quantity based on Load,
it is allowed to express this quantity using multi-interface values
in test report, e.g., as sum of per-interface loads.

{::comment}

    VP: TODO: Use MAY.

{:/comment}

### Relevant Lower Bound

Definition:

&nbsp;
: The Relevant Lower Bound is the largest Trial Load value
among those smaller than the Relevant Upper Bound, that got classified
as a Lower Bound for a given Search Goal at the end of the search.

Discussion:

&nbsp;
: If no load had enough Low-Loss Trials, the Relevant Lower Bound
MAY be non-existent.

&nbsp;
: Strictly speaking, if the Relevant Upper Bound does not exist,
the Relevant Lower Bound also does not exist.
In a typical case, Max Load is classified as a Lower Bound,
making it impossible to increase the Load to continue the search
for an Upper Bound.
Thus, it is not clear whether a larger value would be found
for a Relevant Lower Bound if larger Loads were possible.

&nbsp;
: Given that Relevant Lower Bound is a quantity based on Load,
it is allowed to express this quantity using multi-interface values
in test report, e.g., as sum of per-interface loads.

{::comment}

    VP: TODO: Use MAY.

{:/comment}

### Conditional Throughput

Definition:

&nbsp;
: Conditional Throughput is a value computed at the Relevant Lower Bound
according to algorithm defined in
[Appendix B](#appendix-b-conditional-throughput).

Discussion:

&nbsp;
: The Relevant Lower Bound is defined only at the end of the Search,
and so is the Conditional Throughput.
But the algorithm can be applied at any time on any Lower Bound load,
so the final Conditional Throughput value may appear sooner
than at the end of a Search.

&nbsp;
: Informally, the Conditional Throughput should be
a typical Trial Forwarding Rate, expected to be seen
at the Relevant Lower Bound of a given Search Goal.

&nbsp;
: But frequently it is only a conservative estimate thereof,
as MLRsearch Implementations tend to stop measuring more Trials
as soon as they confirm the value cannot get worse than this estimate
within the Goal Duration Sum.

&nbsp;
: This value is RECOMMENDED to be used when evaluating repeatability
and comparability of different MLRsearch Implementations.

&nbsp;
: Refer to Section [Generalized Throughput](#generalized-throughput) for more details.

&nbsp;
: Given that Conditional Throughput is a quantity based on Load,
it is allowed to express this quantity using multi-interface values
in test report, e.g., as sum of per-interface forwarding rates.

{::comment}

    VP: TODO: Use MAY.

{:/comment}

### Goal Results

MLRsearch Specification is based on a set of requirements
for a "regular" result. But in practice, it is not always possible
for such result instance to exist, so also "irregular" results
need to be supported.

#### Regular Goal Result

Definition:

&nbsp;
: Regular Goal Result is a composite quantity consisting of several attributes.
Relevant Upper Bound and Relevant Lower Bound are REQUIRED attributes.
Conditional Throughput is a RECOMMENDED attribute.
Stopping conditions for the corresponding Search Goal MUST
be satisfied to produce a Regular Goal Result.

{::comment}

    MB90: To do what? I'm afraid we need to explicit the meaning here.

    VP: Yes, reformulate.

    MK: Edited.

{:/comment}

Discussion:

{::comment}

    MB91: Isn't this redundant with listing the bounds as required in the previous definition?

    VP: Do we need separation between may-not-exist and must-exist quantities?
          Either way, reformulate.

    MK: Deleted. Agree with Med - Sentence was redundant as already
          covered by text in definition "Relevant Upper Bound and Relevant
          Lower Bound are REQUIRED attributes."

    VP: TODO: Re-check.

{:/comment}

&nbsp;
: If an implementation offers Goal Width as a Search Goal attribute,
the distance between the Relevant Lower Bound
and the Relevant Upper Bound MUST NOT be larger than the Goal Width,

&nbsp;
: Implementations MAY add their own attributes.

&nbsp;
: Test report MUST display Relevant Lower Bound.
Displaying Relevant Upper Bound is RECOMMENDED,
especially if the implementation does not use Goal Width.

&nbsp;
: For stopping conditions refer to Sections [Goal Width](#goal-width) and
[Stopping Conditions and Precision](#stopping-conditions-and-precision).

#### Irregular Goal Result

Definition:

&nbsp;
: Irregular Goal Result is a composite quantity. No attributes are required.

Discussion:

&nbsp;
: It is RECOMMENDED to report any useful quantity even if it does not
satisfy all the requirements. For example, if Max Load is classified
as a Lower Bound, it is fine to report it as an "effective" Relevant Lower Bound
(although not a real one, as that requires
Relevant Upper Bound which does not exist in this case),
and compute Conditional Throughput for it. In this case,
only the missing Relevant Upper Bound signals this result instance is irregular.

&nbsp;
: Similarly, if both relevant bounds exist, it is RECOMMENDED
to include them as Irregular Goal Result attributes,
and let the Manager decide if their distance is too far for users' purposes.

&nbsp;
: If test report displays some Irregular Goal Result attribute values,
they MUST be clearly marked as coming from irregular results.

&nbsp;
: The implementation MAY define additional attributes.

#### Goal Result

Definition:

&nbsp;
: Goal Result is a composite quantity.
Each instance is either a Regular Goal Result or an Irregular Goal Result.

Discussion:

&nbsp;
: The Manager MUST be able to distinguish whether the instance is regular or not.

### Search Result

Definition:

&nbsp;
: The Search Result is a single composite object
that maps each Search Goal instance to a corresponding Goal Result instance.

Discussion:

&nbsp;
: As an alternative to mapping, the Search Result may be represented
as an ordered list of Goal Result instances that appears in the exact
sequence of their corresponding Search Goal instances.

&nbsp;
: When the Search Result is expressed as a mapping, it MUST contain an
entry for every Search Goal instance supplied in the Controller Input.

{::comment}

    MB92: To what?

    VP: Subsections on quantities and interfaces should mention equivalent representations.
          Then reformulate this.

    MK: Edited. First two paragraphs in Discussion changed to make it
          clearer.

{:/comment}

&nbsp;
: Identical Goal Result instances MAY be listed for different Search Goals,
but their status as regular or irregular may be different.
For example, if two goals differ only in Goal Width value,
and the relevant bound values are close enough according to only one of them.

### Controller Output

Definition:

&nbsp;
: The Controller Output is a composite quantity returned from the Controller
to the Manager at the end of the search.
The Search Result instance is its only required attribute.

Discussion:

&nbsp;
: MLRsearch Implementation MAY return additional data in the Controller Output,
e.g., number of trials performed and the total Search Duration.

{::comment}

    VP: TODO: Regular end, irregular exit, user abort.
    Should not need new text, review related MD comments.
    Maybe differentiate abort conditions, or at least make them explicitly vague?

{:/comment}

{::comment}

    VP: TODO: Emphasize one controller call gives one benchmark.
    Any recurring tests count as independent benchmarks.

{:/comment}

## Architecture Terms

MLRsearch architecture consists of three main system components: 
the Manager, the Controller, and the Measurer, defined in the following
subsections.

{::comment}

    MB93: I guess these should be introduced before the attributes as these components
            are used in the description. Please reconsider the flow of the document.

    VP: Reformulate this to clarify overview introduced, this finalizes the definition.

    MK: Edited. And I disagree. Three components of the architecture
          are listed, with definitions following. I do not envisage any
          problem from the reader perspective.

    VP: TODO: Re-check.

{:/comment}

Note that the architecture also implies the presence of other components,
such as the SUT and the tester (as a sub-component of the Measurer).

Communication protocols and interfaces between components are left
unspecified. For example, when MLRsearch Specification mentions
"Controller calls Measurer",

{::comment}

    MB94: Aha, this answers a comment I made earlier :)
            Let's save cycles for other readers and move all this
            section early in the document.

    VP: Hmm, maybe a subsection of overview?
          Definitely something needs to be moved around.

    MK: Edited. And addressed the original concern. See my note at MB93.

    VP: TODO: Re-check.

{:/comment}

it is possible that the Controller notifies the Manager
to call the Measurer indirectly instead. In doing so, the Measurer Implementations
can be fully independent from the Controller implementations,
e.g., developed in different programming languages.

### Measurer

Definition:

&nbsp;
: The Measurer is a functional element that when called
with a [Trial Input](#trial-input) instance, performs one [Trial ](#trial)
and returns a [Trial Output](#trial-output) instance.

Discussion:

&nbsp;
: This definition assumes the Measurer is already initialized.
In practice, there may be additional steps before the Search,
e.g., when the Manager configures the traffic profile
(either on the Measurer or on its tester sub-component directly)
and performs a warm-up (if the tester or the test procedure requires one).

&nbsp;
: It is the responsibility of the Measurer implementation to uphold
any requirements and assumptions present in MLRsearch Specification,
e.g., Trial Forwarding Ratio not being larger than one.

&nbsp;
: Implementers have some freedom.
For example, Section 10 of [RFC2544]
gives some suggestions (but not requirements) related to
duplicated or reordered frames.
Implementations are RECOMMENDED to document their behavior
related to such freedoms in as detailed a way as possible.

&nbsp;
: It is RECOMMENDED to benchmark the test equipment first,
e.g., connect sender and receiver directly (without any SUT in the path),
find a load value that guarantees the Offered Load is not too far
from the Intended Load and use that value as the Max Load value.
When testing the real SUT, it is RECOMMENDED to turn any severe deviation
between the Intended Load and the Offered Load into increased Trial Loss Ratio.

&nbsp;
: Neither of the two recommendations are made into mandatory requirements,
because it is not easy to provide guidance about when the difference is severe enough,
in a way that would be disentangled from other Measurer freedoms.

&nbsp;
: For a sample situation where the Offered Load cannot keep up
with the Intended Load, and the consequences on MLRsearch result,
refer to Section [Hard Performance Limit](#hard-performance-limit).

### Controller

Definition:

&nbsp;
: The Controller is a functional element that, upon receiving a Controller
Input instance, repeatedly generates Trial Input instances for the
Measurer and collects the corresponding Trial Output instances. This
cycle continues until the stopping conditions are met, at which point
the Controller produces a final Controller Output instance and
terminates.

{::comment}

    MB95: Till a stop?

    VP: Yes.

    MK: Edited. It should be clear now.

{:/comment}

Discussion:

&nbsp;
: Informally, the Controller has big freedom in selection of Trial Inputs,
and the implementations want to achieve all the Search Goals
in the shortest average time.

&nbsp;
: The Controller's role in optimizing the overall Search Duration
distinguishes MLRsearch algorithms from simpler search procedures.

&nbsp;
: Informally, each implementation can have different stopping conditions.
Goal Width is only one example.
In practice, implementation details do not matter,
as long as Goal Result instances are regular.

### Manager

Definition:

&nbsp;
: The Manager is a functional element that is reponsible for
provisioning other components, calling a Controller component once,
and for creating the test report following the reporting format as
defined in Section 26 of [RFC2544].

Discussion:

&nbsp;
: The Manager initializes the SUT, the Measurer
(and the tester if independent from Measurer)
with their intended configurations before calling the Controller.

&nbsp;
: Note that Section 7 of [RFC2544] already puts requirements on SUT setups:

&nbsp;
: &nbsp;
  : It is expected that all of the tests will be run without changing the
  configuration or setup of the DUT in any way other than that required
  to do the specific test. For example, it is not acceptable to change
  the size of frame handling buffers between tests of frame handling
  rates or to disable all but one transport protocol when testing the
  throughput of that protocol.

{::comment}

    VP: TODO: Nested "definition list" does not work. Use quotes here?

{:/comment}

&nbsp;
: It is REQUIRED for the test report to encompass all the SUT configuration
details, including description of a "default" configuration common for most tests
and configuration changes if required by a specific test.

&nbsp;
: For example, Section 5.1.1 of [RFC5180] recommends testing jumbo frames
if SUT can forward them, even though they are outside the scope
of the 802.3 IEEE standard. In this case, it is acceptable
for the SUT default configuration to not support jumbo frames,
and only enable this support when testing jumbo traffic profiles,
as the handling of jumbo frames typically has different packet buffer
requirements and potentially higher processing overhead.
Non-jumbo frame sizes should also be tested on the jumbo-enabled setup.

&nbsp;
: The Manager does not need to be able to tweak any Search Goal attributes,
but it MUST report all applied attribute values even if not tweaked.

&nbsp;
: A "user" - human or automated - invokes the Manager once to launch a
single Search and receive its report. Every new invocation is treated
as a fresh, independent Search; how the system behaves across multiple
calls (for example, combining or comparing their results) is explicitly
out of scope for this document.

{::comment}

    MB96: This answers a comment I have earlier.
            Please move all these details to be provided early.

    VP: Yes (covered by earlier comments).

    MK: Yes - covered by earlier edits.

{:/comment}

{::comment}

    MB97: Should there be a mode where conditional calls are invoked?
            Or more generally to instruct some dependency?

    VP: Explain in earlier subsections, repeats are out of scope.

    MK: Edited. It should be clear now that repeats are out of scope.

{:/comment}

## Compliance

This section discusses compliance relations between MLRsearch
and other test procedures.

### Test Procedure Compliant with MLRsearch

Any networking measurement setup that could be understood as consisting of
functional elements satisfying requirements
for the Measurer, the Controller and the Manager,
is compliant with MLRsearch Specification.

These components can be seen as abstractions present in any testing procedure.
For example, there can be a single component acting both
as the Manager and the Controller, but if values of required attributes
of Search Goals and Goal Results are visible in the test report,
the Controller Input instance and Controller Output instance are implied.

For example, any setup for conditionally (or unconditionally)
compliant [RFC2544] throughput testing
can be understood as a MLRsearch architecture,
if there is enough data to reconstruct the Relevant Upper Bound.

Refer to section 
[MLRsearch Compliant with RFC 2544](#mlrsearch-compliant-with-rfc-2544)
for an equivalent Search Goal.

Any test procedure that can be understood as one call to the Manager of
MLRsearch architecture is said to be compliant with MLRsearch Specification.

### MLRsearch Compliant with RFC 2544

The following Search Goal instance makes the corresponding Search Result
unconditionally compliant with Section 24 of [RFC2544].

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 60 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 0%

{::comment}

    MB98: Not related but triggered by this,
            can we have at the end of the document a table with all
            the default values/recommended for the various
            attributes defined in the document?

    VP: Maybe? Revisit later to see if we have enough data to warrant table format.

    MK: TODO. This is not a bad idea. A section that in summary table
          lists common usage cases with recommended settings e.g. RFC2544,
          TST009, FD.io CSIT, examples of SUTs with certain behaviour e.g.
          suspected periodic SUT disruption. It will make it more concrete to
          the reader and verify their understanding of the spec.

{:/comment}

Goal Loss Ratio and Goal Exceed Ratio attributes,
are enough to make the Search Goal conditionally compliant.
Adding Goal Final Trial Duration
makes the Search Goal unconditionally compliant.

Goal Duration Sum prevents MLRsearch
from repeating zero-loss Full-Length Trials.

The presence of other Search Goals does not affect the compliance
of this Goal Result.
The Relevant Lower Bound and the Conditional Throughput are in this case
equal to each other, and the value is the [RFC2544] throughput.

Non-zero exceed ratio is not strictly disallowed, but it could
needlessly prolong the search when Low-Loss short trials are present.

### MLRsearch Compliant with TST009

One of the alternatives to [RFC2544] is Binary search with loss verification
as described in Section 12.3.3 of [TST009].

The rationale of such search is to repeat high-loss trials, hoping for zero loss on second try,
so the results are closer to the noiseless end of performance spectrum,
thus more repeatable and comparable.

Only the variant with "z = infinity" is achievable with MLRsearch.

For example, for "max(r) = 2" variant, the following Search Goal instance
should be used to get compatible Search Result:

- Goal Final Trial Duration = 60 seconds
- Goal Duration Sum = 120 seconds
- Goal Loss Ratio = 0%
- Goal Exceed Ratio = 50%

If the first 60 seconds trial has zero loss, it is enough for MLRsearch to stop
measuring at that load, as even a second high-loss trial
would still fit within the exceed ratio.

But if the first trial is high-loss, MLRsearch needs to perform also
the second trial to classify that load.
Goal Duration Sum is twice as long as Goal Final Trial Duration,
so third full-length trial is never needed.

# Methodology Rationale and Design Considerations

{::comment}

    MB99: Please consider that a more explicit title that reflects the content.

    VP: Yes, but not sure what would be a better title yet.

    MK: Edited. Also updated opening paragraph to motivate the reader.

{:/comment}

{::comment}

    Manual processes, automation, implementation as library,...

    TODO: Recheck specification minimizes user/iplementation discussions.

    TODO: Add those discussions here somewhere is useful.

{:/comment}

This section explains the Why behind MLRsearch. Building on the
normative specification in Section
[MLRsearch Specification] (#mlrsearch-specification),
it contrasts MLRsearch with the classic
[RFC2544] single-ratio binary-search procedure and walks through the
key design choices: binary-search mechanics, stopping-rule precision,
loss-inversion for multiple goals, exceed-ratio handling, short-trial
strategies, and the generalised throughput concept. Together, these
considerations show how the methodology reduces test time, supports
multiple loss ratios, and improves repeatability. 

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

MLRsearch Specification requires listing both Relevant Bounds for each
Search Goal, and the difference between the bounds implies
whether the result precision is achieved.
Therefore, it is not necessary to report the specific stopping condition used.

MLRsearch Implementations may use Goal Width
to allow direct control of result precision
and indirect control of the Search Duration.

Other MLRsearch Implementations may use different stopping conditions:
for example based on the Search Duration, trading off precision control
for duration control.

Due to various possible time optimizations, there is no strict
correspondence between the Search Duration and Goal Width values.
In practice, noisy SUT performance increases both average search time
and its variance.

## Loss Ratios and Loss Inversion

The biggest

{::comment}

    MB100: We don't need to say it if it is obvious ;)

    VP: Reformulate.

    MK: Edited.

{:/comment}

difference between MLRsearch and [RFC2544] binary search
is in the goals of the search.
[RFC2544] has a single goal, based on classifying a single full-length trial
as either zero-loss or non-zero-loss.
MLRsearch supports searching for multiple Search Goals at once,
usually differing in their Goal Loss Ratio values.

### Single Goal and Hard Bounds

Each bound in [RFC2544] simple binary search is "hard",
in the sense that all further Trial Load values
are smaller than any current upper bound and larger than any current lower bound.

This is also possible for MLRsearch Implementations,
when the search is started with only one Search Goal instance.

### Multiple Goals and Loss Inversion

MLRsearch Specification

{::comment}

    MB101: Specification?

    VP: Ok.

    MK: Edited.

{:/comment}

supports multiple Search Goals, making the search procedure
more complicated compared to binary search with single goal,
but most of the complications do not affect the final results much.
Except for one phenomenon: Loss Inversion.

Depending on Search Goal attributes, Load Classification results may be resistant
to small amounts of Section [Inconsistent Trial Results](#inconsistent-trial-results).
However, for larger amounts, a Load that is classified
as an Upper Bound for one Search Goal
may still be a Lower Bound for another Search Goal.
Due to this other goal, MLRsearch will probably perform subsequent Trials
at Trial Loads even larger than the original value.

This introduces questions any many-goals search algorithm has to address.
For example: What to do when all such larger load trials happen to have zero loss?
Does it mean the earlier upper bound was not real?
Does it mean the later Low-Loss trials are not considered a lower bound?

The situation where a smaller Load is classified as an Upper Bound,
while a larger Load is classified as a Lower Bound (for the same search goal),
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

The Relevant Upper Bound (for specific goal) is the smallest Load classified
as an Upper Bound. But the Relevant Lower Bound is not simply
the largest among Lower Bounds. It is the largest Load among Loads
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

This also applies when that Load is measured
before another Load gets enough measurements to become a current Relevant Bound.

This also implies that if the SUT tested (or the Traffic Generator used)
needs a warm-up, it should be warmed up before starting the Search,
otherwise the first few measurements could become unjustly limiting.

For MLRsearch Implementations, it means it is better to measure
at smaller Loads first, so bounds found earlier are less likely
to get invalidated later.

## Exceed Ratio and Multiple Trials

The idea of performing multiple Trials at the same Trial Load comes from
a model where some Trial Results (those with high Trial Loss Ratio) are affected
by infrequent effects, causing unsatisfactory repeatability

{::comment}

    MB102: Or other similar terms, but not poor thing.
    Please consider the same change in other parts of the document.

    VP: Ok, search&replace.

    MK: Edited. Searched and replaced all with unsatisfactory, unacceptable.

{:/comment}

of [RFC2544] Throughput results. Refer to Section [DUT in SUT](#dut-in-sut)
for a discussion about noiseful and noiseless ends
of the SUT performance spectrum.
Stable results are closer to the noiseless end of the SUT performance spectrum,
so MLRsearch may need to allow some frequency of high-loss trials
to ignore the rare but big effects near the noiseful end.

For MLRsearch to perform such Trial Result filtering, it needs
a configuration option to tell how frequent the "infrequent" big loss can be.
This option is called the [Goal Exceed Ratio](#goal-exceed-ratio).
It tells MLRsearch what ratio of trials (more specifically,
what ratio of Trial Effective Duration seconds)
can have a [Trial Loss Ratio](#trial-loss-ratio)
larger than the [Goal Loss Ratio](#goal-loss-ratio)
and still be classified as a [Lower Bound](#lower-bound).

Zero exceed ratio means all Trials must have a Trial Loss Ratio
equal to or lower than the Goal Loss Ratio.

When more than one Trial is intended to classify a Load,
MLRsearch also needs something that controls the number of trials needed.
Therefore, each goal also has an attribute called Goal Duration Sum.

The meaning of a [Goal Duration Sum](#goal-duration-sum) is that
when a Load has (Full-Length) Trials
whose Trial Effective Durations when summed up give a value at least as big
as the Goal Duration Sum value,
the Load is guaranteed to be classified either as an Upper Bound
or a Lower Bound for that Search Goal instance.

## Short Trials and Duration Selection

MLRsearch requires each Search Goal to specify its Goal Final Trial Duration.

Section 24 of [RFC2544] already anticipates possible time savings
when Short Trials are used.

An MLRsearch implementation MAY expose configuration parameters that
decide whether, when, and how short trial durations are used. The exact
heuristics and controls are left to the discretion of the implementer.

{::comment}

    MB103: We may say that how this is exposed to a user/manager is implmentation specific.

    VP: Earlier subsection should explain when discussing implementations.

    MK: Edited.

{:/comment}

While MLRsearch Implementations are free to use any logic to select
Trial Input values, comparability between MLRsearch Implementations
is only assured when the Load Classification logic
handles any possible set of Trial Results in the same way.

The presence of Short Trial Results complicates
the Load Classification logic, see more details in Section
[Load Classification Logic](#load-classification-logic).

While the Load Classification algorithm is designed to avoid any unneeded Trials,
for explainability reasons it is recommended for users to use
such Controller Input instances that lead to all Trial Duration values
selected by Controller to be the same,
e.g., by setting any Goal Initial Trial Duration to be a single value
also used in all Goal Final Trial Duration attributes.

## Generalized Throughput

Because testing equipment takes the Intended Load
as an input parameter for a Trial measurement,
any load search algorithm needs to deal with Intended Load values internally.

But in the presence of Search Goals with a non-zero
[Goal Loss Ratio](#goal-loss-ratio), the Load usually does not match
the user's intuition of what a throughput is.
The forwarding rate as defined in Section Section 3.6.1 of [RFC2285] is better,
but it is not obvious how to generalize it
for Loads with multiple Trials and a non-zero Goal Loss Ratio.

The clearest illustration - and the chief reason for adopting a
generalized throughput definition - is the presence of a hard
performance limit.

{::comment}

    MB104: Not sure to parse this.

    VP: Reformulate.

    MK: Edited.

{:/comment}

### Hard Performance Limit

Even if bandwidth of a medium allows higher traffic forwarding performance,
the SUT interfaces may have their additional own limitations,
e.g., a specific frames-per-second limit on the NIC (a common occurrence).

Those limitations should be known and provided as Max Load, Section
[Max Load](#max-load).

{::comment}

    MB105: We may say that some implementation may expose their capabilities
             using IPFIX/YANG, but such exposure is out of scope.

    VP: Add capability exposition to earlier implementation subsections.
          Reformulate this sentence to be specific to hard limits.

    MK: Edited. Capability exposition of SUT and DUT is out of scope
          of this document. Do we need to state it in the opening somewhere?
          COTS NICs do not support network configuration protocols,
          they are configured using vendor specific registers and associated
          kernel or userspace drivers.

{:/comment}

But if Max Load is set larger than what the interface can receive or transmit,
there will be a "hard limit" behavior observed in Trial Results.

Consider that the hard limit is at hundred million frames per second (100 Mfps),
Max Load is larger, and the Goal Loss Ratio is 0.5%.
If DUT has no additional losses, 0.5% Trial Loss Ratio will be achieved
at Relevant Lower Bound of 100.5025 Mfps.

Reporting a throughput that exceeds the SUT's verified hard limit is
counter-intuitive. Accordingly, the RFC 2544 throughput metric should
be generalized - rather than relying solely on the Relevant Lower
Bound - to reflect realistic, limit-aware performance.

{::comment}

    MK: Edited. Above paragraph was not reading well. Following from
          MB105 I have updated it further to motivate generalization of
          throughput.

{:/comment}

MLRsearch defines one such generalization,
the [Conditional Throughput](#conditional-throughput).
It is the Trial Forwarding Rate from one of the Full-Length Trials
performed at the Relevant Lower Bound.
The algorithm to determine which trial exactly is in
[Appendix B: Conditional Throughput](#appendix-b-conditional-throughput).

In the hard limit example, 100.5025 Mfps Load will still have
only 100.0 Mfps forwarding rate, nicely confirming the known limitation.

### Performance Variability

With non-zero Goal Loss Ratio, and without hard performance limits,
Low-Loss trials at the same Load may achieve different Trial Forwarding Rate
values just due to DUT performance variability.

By comparing the best case (all Relevant Lower Bound trials have zero loss)
and the worst case (all Trial Loss Ratios at Relevant Lower Bound
are equal to the Goal Loss Ratio), we find the possible Conditional Throughput
values may have up to the Goal Loss Ratio relative difference.

{::comment}

    VP: TODO: Reformulate to avoid "we" construct.

{:/comment}

Setting the Goal Width below the Goal Loss Ratio
may cause the Conditional Throughput for a larger Goal Loss Ratio to become smaller
than a Conditional Throughput for a goal with a lower Goal Loss Ratio,
which is counter-intuitive, considering they come from the same Search.
Therefore, it is RECOMMENDED to set the Goal Width to a value no lower
than the Goal Loss Ratio of the higher-loss Search Goal.

Although Conditional Throughput can fluctuate from one run to the next,
it still offers a more discriminating basis for comparison than the
Relevant Lower Bound - particularly when deterministic load selection
yields the same Lower Bound value across multiple runs.

# MLRsearch Logic and Example

This section uses informal language to describe two aspects of MLRsearch logic:
Load Classification and Conditional Throughput,
reflecting formal pseudocode representation provided in
[Appendix A: Load Classification](#appendix-a-load-classification)
and [Appendix B: Conditional Throughput](#appendix-b-conditional-throughput).
This is followed by example search.

The logic is equivalent but not identical to the pseudocode
on appendices. The pseudocode is designed to be short and frequently
combines multiple operations into one expression.
The logic as described in this section lists each operation separately
and uses more intuitive names for the intermediate values.

## Load Classification Logic

Note: For explanation clarity variables are taged as (I)nput,
(T)emporary, (O)utput.

{::comment}

    MB106: Move this to the terminology/convention section

    VP: I do not think these flags fit into terminology.
          For this long list, maybe divide into sublists?

    MK: I agree - this is does not belong to draft terminology
          section. And I agree, for readability we could split the long list
          into groups with meaningful headers. See my attempt to do so below.

{:/comment}

### Collect Trial Results

- Take all Trial Result instances (I) measured at a given load.

### Aggregate Trial Durations

- Full-length high-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length high-loss trials (I).
- Full-length low-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length low-loss trials (I).
- Short high-loss sum is the sum (T)  of Trial Effective Duration values
  of all short high-loss trials (I).
- Short low-loss sum is the sum (T) of Trial Effective Duration values
  of all short low-loss trials (I).

### Derive Goal-Based Ratios

- Subceed ratio (T) is One minus the Goal Exceed Ratio (I).
- Exceed coefficient (T) is the Goal Exceed Ratio divided by the subceed
  ratio.

### Balance Short-Trial Effects

- Balancing sum (T) is the short low-loss sum
  multiplied by the exceed coefficient.
- Excess sum (T) is the short high-loss sum minus the balancing sum.
- Positive excess sum (T) is the maximum of zero and excess sum.

### Compute Effective Duration Totals

- Effective high-loss sum (T) is the full-length high-loss sum
  plus the positive excess sum.
- Effective full sum (T) is the effective high-loss sum
  plus the full-length low-loss sum.
- Effective whole sum (T) is the larger of the effective full sum
  and the Goal Duration Sum.
- Missing sum (T) is the effective whole sum minus the effective full sum.

### Estimate Exceed Ratios

- Pessimistic high-loss sum (T) is the effective high-loss sum
  plus the missing sum.
- Optimistic exceed ratio (T) is the effective high-loss sum
  divided by the effective whole sum.
- Pessimistic exceed ratio (T) is the pessimistic high-loss sum
  divided by the effective whole sum.

### Classify the Load

- The load is classified as an Upper Bound (O) if the optimistic exceed
  ratio is larger than the Goal Exceed Ratio.
- The load is classified as a Lower Bound (O) if the pessimistic exceed
  ratio is not larger than the Goal Exceed Ratio.
- The load is classified as undecided (O) otherwise.

## Conditional Throughput Logic

### Collect Trial Results

- Take all Trial Result instances (I) measured at a given Load.

### Sum Full-Length Durations

- Full-length high-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length high-loss trials (I).
- Full-length low-loss sum (T) is the sum of Trial Effective Duration
  values of all full-length low-loss trials (I).
- Full-length sum (T) is the full-length high-loss sum (I) plus the
  full-length low-loss sum (I).

### Derive Initial Thresholds

- Subceed ratio (T) is One minus the Goal Exceed Ratio (I) is called.
- Remaining sum (T) initially is full-lengths sum multiplied by subceed
  ratio.
- Current loss ratio (T) initially is 100%.

### Iterate Through Ordered Trials

- For each full-length trial result, sorted in increasing order by Trial
  Loss Ratio:
  - If remaining sum is not larger than zero, exit the loop.
  - Set current loss ratio to this trial's Trial Loss Ratio (I).
  - Decrease the remaining sum by this trial's Trial Effective Duration (I).

### Compute Conditional Throughput

- Current forwarding ratio (T) is One minus the current loss ratio.
- Conditional Throughput (T) is the current forwarding ratio multiplied
  by the Load value.

### Conditional Throughput and Load Classification

Conditional Throughput and results of Load Classification overlap but
are not identical.

- When a load is marked as a Relevant Lower Bound, its Conditional
  Throughput is taken from a trial whose loss ratio never exceeds the
  Goal Loss Ratio.

- The reverse is not guaranteed: if the Goal Width is narrower than the
  Goal Loss Ratio, Conditional Throughput can still end up higher than
  the Relevant Upper Bound.

## SUT Behaviors

In Section [DUT in SUT](#dut-in-sut), the notion of noise has been introduced.
This section uses new terms
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
the expert can assess probability of each outcome.

### Exceed Probability

When the Controller selects new Trial Duration and Trial Load,
and just before the Measurer starts performing the Trial,
the SUT expert can envision possible Trial Results.

With respect to a particular Search Goal instance, the possibilities
can be summarized into a single number: Exceed Probability.
It is the probability (according to the expert) that the measured
Trial Loss Ratio will be higher than the Goal Loss Ratio.

### Trial Duration Dependence

When comparing Exceed Probability values for the same Trial Load value
but different Trial Duration values,
there are several patterns that commonly occur in practice.

#### Strong Increase

Exceed Probability is very low at short durations but very high at full-length.
This SUT behavior is undesirable, and may hint at faulty SUT,
e.g., SUT leaks resources and is unable to sustain the desired performance.

But this behavior is also seen when SUT uses large amount of buffers.
This is the main reasons users may want to set large Goal Final Trial Duration.

#### Mild Increase

Short trials are slightly less likely to exceed the loss-ratio limit,
but the improvement is modest. This mild benefit is typical when noise
is dominated by rare, large loss spikes: during a full-length trial,
the good-performing periods cannot fully offset the heavy frame loss
that occurs in the brief low-performing bursts.

#### Independence

Short trials have basically the same Exceed Probability as full-length trials.
This is possible only if loss spikes are small (so other parts can compensate)
and if Goal Loss Ratio is more than zero (otherwise, other parts
cannot compensate at all).

#### Decrease

Short trials have larger Exceed Probability than full-length trials.
This can be possible only for non-zero Goal Loss Ratio,
for example if SUT needs to "warm up" to best performance within each trial.
Not commonly seen in practice.

## Example Search

{::comment}

    MB107: We may move this section to an appendix

    VP: Ok.

    MK: TODO. Move to Appendix A, before the pseudocode Appendices.
          Keeping it here for now to finish editing with clean change
          tracking in gerrit.

{:/comment}

The following example Search is related to
one hypothetical run of a Search test procedure
that has been started with multiple Search Goals.
Several points in time are chosen, to show how the logic works,
with specific sets of Trial Result available.
The trial results themselves are not very realistic, as
the intention is to show several corner cases of the logic.

In all Trials, the Effective Trial Duration is equal to Trial Duration.

Only one Trial Load is in focus, its value is one million frames per second.
Trial Results at other Trial Loads are not mentioned,
as the parts of logic present here do not depend on those.
In practice, Trial Results at other Load values would be present,
e.g., MLRsearch will look for a Lower Bound smaller than any Upper Bound found.

At any given moment, exactly one Search Goal is designated as in focus.
This designation affects only the Trial Duration chosen for new trials;
it does not alter the rest of the decision logic.

An MLRsearch implementation is free to evaluate several goals
simultaneously - the "focus" mechanism is optional and appears here only
to show that a load can still be classified against goals that are not
currently in focus.

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

{::comment}

    MB108: Please add a table legend. Idem for all tables

    VP: Ok. Figure out how.

    MK: TODO. Kramdown magic.

{:/comment}

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

The one missing trial for "1s final" was Low-Loss,
half of trial results are Low-Loss which exactly matches 50% exceed ratio.
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
As Goal Loss Ratio is zero, it is not possible for 60-second trials
to compensate for losses seen in 1-second results.
But Load Classification logic does not have that knowledge hardcoded,
so optimistic exceed ratio is still only 50%.

But the 0.1% Trial Loss Ratio is lower than "20% exceed" Goal Loss Ratio,
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
This Load is now classified for all goals; the search may end.
Or, more realistically, it can focus on larger load only,
as the three goals will want an Upper Bound (unless this Load is Max Load).

### Conditional Throughput Computations

At the end of this hypothetical search, the "RFC2544" goal labels the
load as an Upper Bound, making it ineligible for Conditional-Throughput
calculations. By contrast, the other three goals treat the same load as
a Lower Bound; if it is also accepted as their Relevant Lower Bound, we
can compute Conditional-Throughput values for each of them.

(The load under discussion is 1 000 000 frames per second.)

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
- After 61 trials, duration of 60x1s + 1x60s has been subtracted from 120s, leaving 0s.
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
- No more trials (and remaining sum is not larger than zero), exiting loop.
- Current forwarding ratio was most recently set to 0.1%.

- Current forwarding ratio is one minus the current loss ratio, so 99.9%.
- Conditional Throughput is the current forwarding ratio multiplied by the Load value.
- Conditional Throughput is 999 thousand frames per second.

Due to stricter Goal Exceed Ratio, this Conditional Throughput
is smaller than Conditional Throughput of the other two goals.

# IANA Considerations

This document does not make any request to IANA.

# Security Considerations

Benchmarking activities as described in this memo are limited to
technology characterization of a DUT/SUT using controlled stimuli in a
laboratory environment, with dedicated address space and the constraints
specified in the sections above.

The benchmarking network topology will be an independent test setup and
MUST NOT be connected to devices that may forward the test traffic into
a production network or misroute traffic to the test management network.

Further, benchmarking is performed on an "opaque" basis, relying
solely on measurements observable external to the DUT/SUT.

The DUT/SUT SHOULD NOT include features that serve only to boost
benchmark scores - such as a dedicated "fast-track" test mode that is
never used in normal operation.

{::comment}

    MB109: Some more elaboration is needed

    VP: This needs BMWG discussion as this chapter is a "boilerplate"
          copied from earlier BMWG documents.

    MK: Edited

    VP: Ok, for draft11, but we can start discussing on bmwg for later versions.

{:/comment}

Any implications for network security arising from the DUT/SUT SHOULD be
identical in the lab and in production networks.

{::comment}

    MB110: Why? We can accept some relax rule in controlled environnement,
             but this not acceptable in deployement. I would adjust accordingly.

    VP: Explain and discuss in BMWG.

    MK: Keeping as is. It is a BMWG standard text that applies here.
          You can see it verbatim in RFC 6815 (section 7), RFC 6414 (section 4.1), RFC
          9004 (section 8), and several BMWG Internet-Drafts.  Its purpose is to
          remind implementers and testers that the device under test must not
          be re-configured into an unrealistic or less-secure state merely to
          obtain benchmark data - a principle that complements the adjacent
          sentence about avoiding "special benchmarking modes." Including
          the sentence therefore maintains consistency with BMWG precedent
          and reinforces a key security expectation.

{:/comment}

{::comment}

    MB111: I would some text to basically
             say that the benchmarking results should be adequately
             protected and guards top prevent leaks to unauthorized
             entities.
             Otherwise, the benchmark results can be used by
             attacker to better adjust their attacks and perform
             attacks that would lead to DDoS a node of the DUT in a
             live network, infer the limitation of a DUT that can be
             used for overflow attacks, etc.
             Also, we can say that the benchmark is agnostic to trafic
             and does not manipulate real traffic. As such, Privacy is
             not a concern.

    VP: To BMWG.

    MK: Keeping as is. See my comments above at MB110.

{:/comment}

# Acknowledgements

Special wholehearted gratitude and thanks to the late Al Morton for his
thorough reviews filled with very specific feedback and constructive
guidelines. Thank You Al for the close collaboration over the years, Your Mentorship,
Your continuous unwavering encouragement full of empathy and energizing
positive attitude. Al, You are dearly missed.

Thanks to Gabor Lencse, Giuseppe Fioccola and BMWG contributors for good
discussions and thorough reviews, guiding and helping us to improve the
clarity and formality of this document.

Many thanks to Alec Hothan of the OPNFV NFVbench project for a thorough
review and numerous useful comments and suggestions in the earlier
versions of this document.

--- back

# Appendix A: Load Classification

{::comment}

    MB112: Move after references

    VP: Ok.

    MK: Move after references.

    VP: Done by moving "--- back" above.

{:/comment}

This appendix specifies how to perform the Load Classification.

Any Trial Load value can be classified,
according to a given [Search Goal](#search-goal) instance.

The algorithm uses (some subsets of) the set of all available Trial Results
from Trials measured at a given Load at the end of the Search.

The block at the end of this appendix holds pseudocode
which computes two values, stored in variables named
`optimistic_is_lower` and `pessimistic_is_lower`.

Although presented as pseudocode, the listing is syntactically valid
Python and can be executed without modification.

{::comment}

    MB113: Where is that python code?

    VP: Reformulate.

    MK: Edited.

{:/comment}

If values of both variables are computed to be true, the Load in question
is classified as a Lower Bound according to the given Search Goal instance.
If values of both variables are false, the Load is classified as an Upper Bound.
Otherwise, the load is classified as Undecided.

Some variable names are shortened to fit expressions in one line.
Namely, variables holding sum quantities end in `_s` instead of `_sum`,
and variables holding effective quantities start in `effect_`
instead of `effective_`.

The pseudocode expects the following variables to hold the following values:

- `goal_duration_s`: The Goal Duration Sum value of the given Search Goal.

- `goal_exceed_ratio`: The Goal Exceed Ratio value of the given Search Goal.

- `full_length_low_loss_s`: Sum of Trial Effective Durations across Trials
  with Trial Duration at least equal to the Goal Final Trial Duration
  and with Trial Loss Ratio not higher than the Goal Loss Ratio
  (across Full-Length Low-Loss Trials).

- `full_length_high_loss_s`: Sum of Trial Effective Durations across Trials
  with Trial Duration at least equal to the Goal Final Trial Duration
  and with Trial Loss Ratio higher than the Goal Loss Ratio
  (across Full-Length High-Loss Trials).

- `short_low_loss_s`: Sum of Trial Effective Durations across Trials
  with Trial Duration shorter than the Goal Final Trial Duration
  and with Trial Loss Ratio not higher than the Goal Loss Ratio
  (across Short Low-Loss Trials).

- `short_high_loss_s`: Sum of Trial Effective Durations across Trials
  with Trial Duration shorter than the Goal Final Trial Duration
  and with Trial Loss Ratio higher than the Goal Loss Ratio
  (across Short High-Loss Trials).

The code works correctly also when there are no Trial Results at a given Load.

~~~ python
exceed_coefficient = goal_exceed_ratio / (1.0 - goal_exceed_ratio)

balancing_s = short_low_loss_s * exceed_coefficient

positive_excess_s = max(0.0, short_high_loss_s - balancing_s)

effect_high_loss_s = full_length_high_loss_s + positive_excess_s

effect_full_length_s = full_length_low_loss_s + effect_high_loss_s

effect_whole_s = max(effect_full_length_s, goal_duration_s)

quantile_duration_s = effect_whole_s * goal_exceed_ratio

pessimistic_high_loss_s = effect_whole_s - full_length_low_loss_s

pessimistic_is_lower = pessimistic_high_loss_s <= quantile_duration_s

optimistic_is_lower = effect_high_loss_s <= quantile_duration_s
~~~

{::comment}

    MB114: May display this a table for better readability

    VP: Ok.

    MK: TODO. Disagree. Can we have it in a proper code block instead?

{:/comment}

# Appendix B: Conditional Throughput

This section specifies an example of how to compute Conditional Throughput,
as referred to in Section [Conditional Throughput](#conditional-throughput).

Any Load value can be used as the basis for the following computation,
but only the Relevant Lower Bound (at the end of the Search)
leads to the value called the Conditional Throughput for a given Search Goal.

The algorithm uses (some subsets of) the set of all available Trial Results
from Trials measured at a given Load at the end of the Search.

The block at the end of this appendix holds pseudocode
which computes a value stored as variable `conditional_throughput`.

Although presented as pseudocode, the listing is syntactically valid
Python and can be executed without modification.

Some variable names are shortened in order to fit expressions in one line.
Namely, variables holding sum quantities end in `_s` instead of `_sum`,
and variables holding effective quantities start in `effect_`
instead of `effective_`.

The pseudocode expects the following variables to hold the following values:

- `goal_duration_s`: The Goal Duration Sum value of the given Search Goal.

- `goal_exceed_ratio`: The Goal Exceed Ratio value of the given Search Goal.

- `full_length_low_loss_s`: Sum of Trial Effective Durations across Trials
  with Trial Duration at least equal to the Goal Final Trial Duration
  and with Trial Loss Ratio not higher than the Goal Loss Ratio
  (across Full-Length Low-Loss Trials).

- `full_length_high_loss_s`: Sum of Trial Effective Durations across Trials
  with Trial Duration at least equal to the Goal Final Trial Duration
  and with Trial Loss Ratio higher than the Goal Loss Ratio
  (across Full-Length High-Loss Trials).

- `full_length_trials`: An iterable of all Trial Results from Trials
  with Trial Duration at least equal to the Goal Final Trial Duration
  (all Full-Length Trials), sorted by increasing Trial Loss Ratio.
  One item `trial` is a composite with the following two attributes available:

  - `trial.loss_ratio`: The Trial Loss Ratio as measured for this Trial.

  - `trial.effect_duration`: The Trial Effective Duration of this Trial.

The code works correctly only when there is at least one
Trial Result measured at a given Load.

~~~ python
full_length_s = full_length_low_loss_s + full_length_high_loss_s
whole_s = max(goal_duration_s, full_length_s)
remaining = whole_s * (1.0 - goal_exceed_ratio)
quantile_loss_ratio = None
for trial in full_length_trials:
    if quantile_loss_ratio is None or remaining > 0.0:
        quantile_loss_ratio = trial.loss_ratio
        remaining -= trial.effect_duration
    else:
        break
else:
    if remaining > 0.0:
        quantile_loss_ratio = 1.0
conditional_throughput = intended_load * (1.0 - quantile_loss_ratio)
~~~

{::comment}

    MB115: Please use <CODE BEGINS> and <CODE ENDS> markers.

    VP: Also table? Ok.

    MK: TODO. Not table, it's code. Can we have it in a proper code
          block instead?

{:/comment}

{::comment}

    TODO-P2: There are long lines.

{:/comment}

{::comment}

    VP: TODO: Fix warnings from kramdown.

{:/comment}

{::comment}

    [Final checklist.]

    <mark>VP Final Checks. Only mark as done when there are no active todos above.</mark>

    <mark>VP Rename chapter/sub-/section to better match their content.</mark>

    <mark>MKP3 VP TODO: Recheck the definition dependencies go bottom-up.</mark>

    <mark>VP TODO: Unify external reference style (brackets, spaces, section numbers and names).</mark>

    <mark>MKP2 VP TODO: Capitalization of New Terms: useful when editing and reviewing,
    but I still vote to remove capitalization before final submit,
    because all other RFCs I see only capitalize due to being section title.</mark>

    <mark>VP TODO: If time permits, keep improving formal style (e.g., using AI).</mark>

{:/comment}

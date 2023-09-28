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
  - Each trial result can affect any search goal in principle
    (trial reuse).
- Multiple preceding targets for each search goal, earlier ones need
  to spend less time on trials.
  - Earlier targets also aim at lesser precision.
  - Use Forwarding Rate (FR) at maximum offered load
    [RFC2285] (section 3.6.2) to initialize the initial targets.
- Take care when dealing with inconsistent trial results.
  - Loss ratios goals are handled in an order that minimizes the chance
    of interference from later trials to earlier goals.
- Apply several load selection heuristics to save even more time
  by trying hard to avoid unnecessarily narrow bounds.

MLRsearch configuration options are flexible enough to
support both conservative settings (unconditionally compliant with [RFC2544],
but longer search duration and worse repeatability) and aggressive
settings (shorter search duration and better repeatability but not
compliant with [RFC2544]).

No part of [RFC2544] is intended to be obsoleted by this document.

# Introduction

While the breadth of configuration options allow MLRsearch to be quite flexible,
it makes the precise description of MLRsearch quite complicated.

Frequently, any single term used in description of RFC 2544 throughput
can be understood as a collection of different notions,
which only happen to coincide in specific configurations.
For continuity, the familiar term can only be used in the specific configuration,
while the more general notions need new unfamiliar terms.

This section describes how RFC 2544 notions are split into
old specific ones and new general ones.

TODO: What is the best order of notions to split?
TODO: Move more RFC2544 comparisons out of terminology.

# Terminology

When a subsection is defining a term, the first paragraph
acts as a definition. Other paragraphs are treated as a description,
they provide additional details without being needed to define the term.

Definitions should form a directed acyclic graph of dependencies.
If a section contains subsections, the section definition
may depend on the subsection definitions.
Otherwise, any definition may depend on preceding definitions.
In other words, if the section definition were to come after subsections,
there would be no forward dependencies for people reading just definitions
from start to finish.

Descriptions provide motivations and explanations,
they frequently reference terms defined only later.
Motivations in section descriptions are the reason
why section text comes before subsection text.

## General notions

General notions are the terms defined in this section.

It is useful to define the following notions
before delving into MLRsearch architecture,
as the notions appear in multiple places
with no place being special enough to host the definition.

### General and specific quantities

General quantity is a quantity that may appear multiple times
in MLRsearch specification, perhaps each time in a different role.
The quantity when appearing in a single role is called
a specific quantity.

It is useful to define the general quantity,
so definitions of specific quantities may refer to it.
We say a specific quantity is based on a general quantity,
if the specific quantity definition refers to and
relies on the general quantity definition.

It is natural to name specific quantities by adding an adjective
(or a noun) to the name of the general quantity.
But existing RFCs typically explicitly define a term acting
in a specific role, so the RFC name directly refers to a specific
quantity, while the corresponding general quantity
is defined only implicitly.
Therefore this documents defines general quantities explicitly,
even if the same term already appears in an RFC.

In practice, it is required to know which unit of measurement
is used to accompany a numeric value of each quantity.
The choice of a particular unit of measurement is not important
for MLRsearch specification though, so specific units
mentioned in this document are just examples or recommendations,
not requirements.

When reporting, it is REQUIRED to state the units used.

### Composite

A composite is a set of named attributes.
Each attribute is either a specific quantity or another composite.

MLRsearch specification frequently groups multiple specific quantities
into a composite. Description of such a composite brings an insight
to motivations why this or other terms are defined as they are.
Such insight would be harder to communicate with the specific quantities alone.

Also, it simplifies naming of specific quantities, as they usually can
share a noun or adjective referring to their common composite.
Most of relations between composites and their specific quantities
can be described using plain English.

Perhaps the only exception involves referring to specific quantities
as attributes. For example if there is a composite called 'target',
and one of its specific quantities is 'target width' defined using
a general quantity 'width', we can say 'width is one of target attributes'.

### SUT

As defined in RFC 2285:
The collective set of network devices to which stimulus is offered
as a single entity and response measured.

While RFC 2544 mostly refers to DUT as a single
(network interconnecting) device, section 19 makes it clear
multiple DUTs can be treated as a single system,
so most of RFC 2544 also applies to testing SUT.

MLRsearch specification only refers to SUT (not DUT),
even if it consists of just a single device.

### Trial

A trial is the part of test described in RFC 2544 section 23.

When traffic has been sent and SUT response has been observed,
we say the trial has been performed, or the trial has been measured.
Before that happens, multiple possibilities for the upcoming trial
may be under consideration.

### Load

Intended, constant load for a trial, usually in frames per second.

Load is the general quantity implied by Constant Load of RFC 1242,
Data Rate of RFC 2544 and Intended Load of RFC 2285.
All three specify this value applies to one (input or output) interface,
so we can talk about unidirectional load also
when bidirectional or multi-port traffic is applied.

MLRsearch does not rely on this distinction, it works also if
the load values correspond to an aggregate rate
(sum over all SUT tested input or output interface unidirectional loads),
as long as all loads share the same semantics.

Several RFCs define useful quantities based on Offered Load
(instead of Intended Load), but MLRsearch specification
works only with (intended) load. Those useful quantities
still serve as motivations for few specific quantities used in MLRsearch
specification.

MLRsearch assumes most load values are positive.
For some (but not all) specific quantities based on load,
zero may also be a valid value.

### Duration

Intended duration of the traffic for a trial, usually in seconds.

This general quantity does not include any preparation nor waiting
described in section 23 of RFC 2544.
Section 24 of RFC 2544 places additional restrictions on duration,
but those restrictions apply only to some of the specific quantities based
on duration.

Duration is always positive in MLRsearch.

### Duration sum

For a specific set of trials, this is the sum of their durations.

Some of specific quantities based on duration sum are derived quantities,
without a specific set of trials to sum their durations.

Duration sum is never negative in MLRsearch.

As RFC 2544 assumes only one trial (at final trial duration) per load,
it does not distinguish between trial duration and trial duration sum.

### Width

General quantity defined for an ordered pair (lower and higher)
of load values, which describes a distance between the two values.

The motivation for the name comes from binary search.
The binary search tries to approximate an unknown value
by repeatedly bisecting an interval of possible values,
until the interval becomes narrow enough.
Width of the interval is a specific quantity
and the termination condition compares that
to another specific quantity acting as the threshold value.
The threshold value does not have a specific interval associated,
but corresponds to a 'size' of the compared interval.
As size is a word already used in definition of frame size,
so a more natural word describing interval is width.

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

RFC 2544 does not specify any stopping conditions,
so there is no analogue of width there.

### Loss ratio

The loss ratio is a general quantity, dimensionless floating point value
assumed to be between 0.0 and 1.0, both including.
It is computed as the number of frames forwarded by SUT, divided by
the number of frames that should have been forwarded during the trial.

If the number of frames that should have been forwarded is zero,
the loss ratio is considered to be zero
(but it is better to use high enough loads to prevent this).

Loss ratio is basically the same quantity as Frame Loss Rate of RFC 1242,
just not expressed in percents.

RFC1242 Frame Loss Rate:
Percentage of frames that should have been forwarded
by a network device under steady state (constant)
load that were not forwarded due to lack of
resources.

(RFC2544 restricts Frame Loss Rate to a type of benchmark,
for loads 100% of 'maximum rate', 90% and so on.)

RFC 2544 througput requires zero loss, corresponding to zero loss ratio here.

### Exceed ratio

This general quantity is a dimensionless floating point value,
defined using two duration sum quantities.
One duration sum is referred to as the good duration sum,
the other is referred to as the bad duration sum.
The exceed ratio value is computed as the bad duration sum value
divided by the sum of the two sums. If both sums are zero,
the exceed ratio is undefined.

As there are no negative duration sums in MLRsearch,
exceed ratio values are between 0.0 and 1.0 (both including).

RFC 2544 throughput can be understood as using zero exceed ratio
(although with only one treial per load any ratio below one works).

## Architecture

MLRsearch architecture consists of three main components:
the manager, the controller and the measurer.

The search algorithm is implemented in the controller,
and it is the main focus of this document.

Most implementation details of the manager and the measurer are
outside of scope of this document, except when describing
how do those components interface with the controller.

### Manager

The manager is the component that initializes SUT, traffic generator
(called tester in RFC 2544), the measurer and the controller
with intended configurations. It then handles the execution
to the controller and receives its result.

Managers can range from simple CLI utilities to complex
Continuous Integration systems. From the controller point of view
it is important that no additional configuration (nor warmup)
is needed for SUT and the measurer before performing trials.

The interface between the manager and the controller
is defined in the controller section.

One execution of the controller is called a search.
Some benchmarks may execute multiple searches on the same SUT
(for example when confirming the performance is stable over time),
but in this document only one invocation is concerned
(others may be understood as the part of SUT preparation).

Creation of reports of appropriate format can also be understood
as the responsibility of the manager. This document places requirements
on which information has to be included in such reports.

### Measurer

The measurer is the component which performs one trial
as described in RFC 2544 section 23, when requested by the controller.

From the controller point of view, it is a function that accepts
a trial input and returns a trial output.

This is the only way the controller can interact with SUT.
In practice, the measurer has to do subtle decisions
when converting the observed SUT behavior into a single
trial loss ratio value. For example how to deal with
out of order frames or duplicate frames.

On software implementation level, the measurer is a callable,
injected by the manager into the controller instance.

The act of performing one trial (act of turning trial input
into trial output) is called a measurement, or trial measurement.
This way we can talk about trials that were measured already
and trials that are merely planned (not measured yet).

#### Trial input

The load and duration to use in an upcoming trial.

This is a composite.

Other quantities needed by the measurer are assumed to be constant
and set up by the manager before search starts (see traffic profile),
so they do not count as trial input attributes.

##### Trial load

Trial load is the intended load for the trial.

This is a specific quantity based on load,
directly corresponding to RFC 2285 intended load.

##### Trial duration

Trial duration is the intended duration for the trial.

This is a specific quantity based on duration, so it specifies
only the traffic part of the trial, not the waiting parts.

#### Traffic profile

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

#### Trial ouput

A composite consisting of trial loss ratio and trial forwarding rate.

Those are the only two specific quantities (among other quantities
possibly measured in the trial, for example the offered load)
that are important for MLRsearch.

##### Trial loss ratio

Trial loss ratio is a specific quantity based on loss ratio.
The value is related to a particular measured trial,
as measured by the measurer.

##### Trial forwarding rate

Trial forwarding rate is a derived quantity.
It is computed as one minus trial loss ratio,
that multiplied by trial load.

Despite the name, the general quantity this specific quantity
corresponds to is load (not rate).
The name is inspired by RFC 2285, which defines Forwarding Rate
specific to one output interface.

As the definition of loss ratio is not neccessarily per-interface
(one of details left for the measurer), using the definition above
(instead of RFC 2285) makes sure trial forwarding rate
is always between zero and the trial load (both including).

#### Trial result

Trial result is a composite consisting of trial input attributes
and trial output attributes.

Those are all specific quantites related to a measured trial MLRsearch needs.

While distinction between trial input and output is important
when defining the interface between the controller and the measurer,
it is easier to talk about trial result
when describing how measured trials influence the controller behavior.

### Controller

The component of MLRsearch architecture that calls the measurer
and returns conditional throughputs to the manager.

This component implements the search algorithm,
the main content of this document.

Contrary to Throughput as defined in RFC 1242,
the definition of conditional throughput is quite sensitive
to the controller input (as provided by the manager),
and its full definition needs several terms
which would otherwise be hidden as internals of the controller
implementation.

The ability of conditional throughput to be less sensitive
to performance variance, and the ability of the controller
to find conditional throughputs for multiple search goals
within one search (and in short overall search time)
are strong enough motivations for the increased complexity.

### Controller input

A composite of max load, min load, and a list of search goals.

The search goals (as elements of the list of search goals)
are usually not named. They may be ordered,
but the impact of ordering is usually negligible.

It is fine if all search goals of the list have the same value
of a particular attribute. In that case, the common value
may be treated as a global attribute (similarly to max and min load).

The set of search goals MUST NOT be empty.
Two search goals within the set MUST differ in at least one attribute.
The manager MAY avoid both issues by presenting empty report
or de-duplicating the search goals, but it is RECOMMENDED
for the manager to raise an error to its caller,
as the two conditions suggest the test is improperly configured.

#### Max load

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

#### Min load

Min load is a specific quantity based on load.
No trial load is ever lower than this value.

The motivation of this quantity is to prevent trials
with too few frames sent to SUT.

Also, practically, if a SUT is able to reach only very small
forwarding rates (min load indirectly serves as a threshold for how small),
it may be considered faulty (or perhaps the test is misconfigured).

#### Search goal

A composite of 7 attributes (see subsections).

If not otherwise specified, 'goal' always refers to a search goal
in this document.

The controller input may contain multiple search goals.
The name Multiple Loss Ratio search was created back when
goal loss ratio was the only attribute allowed to vary between goals.

Each goal will get its conditional throughput discovered
and reported at the end of the search.
It is possible for multiple different goals to share
the same conditional throughput value.

The definitions of the 7 attributes are not very informative by themselves.
Their motivation (and naming) becomes more clear
from the impact they have on conditional throughput.

##### Goal loss ratio

A specific quantity based on loss ratio.
A threshold value for trial loss ratios.
MUST be lower than one.

Trial loss ratio values will be compared to this value,
a trial will be considered bad if its loss ratio is higher than this.

For example, RFC 2544 throughput has goal loss ratio of zero,
a trial is bad once a sigle frame is lost.

Loss ratio of one would classify each trial as good (regardless of loss),
which is not useful.

##### Goal initial trial duration

A specific quantity based on duration.
A threshold value for trial durations.
MUST be positive.

MLRsearch is allowed to use trials as short as this when focusing
on this goal.
The conditional throughput may be influenced by even shorter trials,
measured when focusing on other search goals.

##### Goal final trial duration

A specific quantity based on duration.
A threshold value for trial durations.
MUST be no smaller than goal initial trial duration.

MLRsearch is allowed to use trials as long as this when focusing
on this goal. If more data is needed, repeated trials
at the same load and duration are requested by the controller.

##### Goal min duration sum

A specific quantity based on duration sum.
A threshold value for a particular duration sum.

MLRsearch requires at least this amount of (effective) trials
for a particular load to become part of MLRsearch outputs.

It is possible (though not prectical) for goal min duration sum
to be smaller than goal final trial duration.

In practice, the sum of durations actually spent on trial measurement
can be smaller (when trial results are quite one-sided) or even larger
(in presence of shorter-than-final trial duration results at the same load).

If the sum of all (good and bad) long trials is at least this,
and there are no short trials, then the load is guaranteed
to be classified as either an upper or a lower bound.

When short trials are present, the logic is more complicated.

##### Goal exceed ratio

A specific quantity based on exceed ratio.
A threshold value for particular sets of trials.

An attribute used for classifying loads into upper and lower bounds.

If the duration sum of all (current duration) trials is at least
min duration sum, and more than this percentage of the duration sum
comes from bad trials, this load is an upper bound.

If there are shorter duration trials, the logic is more complicated.

##### Goal width

A specific quantity based on width.
A threshold value for a particular width.
MUST be positive.

This defines the exit condition for this search goal.

Relevant bounds (of the final target) need to be this close
before conditional throughput can be reported.

##### Preceding targets

A non-negative integer affecting the behavior of the controller.

How many additional non-final targets to add.
Each next preceding target has double width
and min duration sum geometrically closer to initial trial duration.

The usage of preceding targets is an important source
of MLRsearch time savings (compared to simpler search algorithms).

Having this value configurable lets the manager
tweak the overall search duration based on presumed knowledge
of SUT performance stability.

### Controller internals

Terms not directly corresponding to the controller's input nor output,
but needed indirectly as dependencies of the conditional throughput
definition.

Following these definitions specifies virtually all of the controller
(MLRsearch algorithm) logic.

#### Pre-initial trials

Up to three special trials executed at the start of the search.
The first trial load is max load,
subsequent trial load are computed from preceding trial forwarding rate.

The main loop of the controller logic needs at least one trial result,
and time is saved if the trial results are close to future conditional
throughput values.

The exact way to compute load for second and third trial
(and whether even measure second or third trial)
are not specified here, as the implementation details
have negligible effect on the reported conditional throughput.

{::comment}
    TODO: Still, recommend something like this:
    Loads need to fit several different initial targets at once.
    Duration is the largest among initial trial durations,
    loads are computed from forwarding rate an smallest loss ratio goal.
    Also, the initial target current width is set based on these.
{:/comment}

#### Search target

A composite of 5 specific quantites (see subsections).
Frequently called just target.

Similar to (but distinct from) the search goal.

Each search goal prescribes a final target,
usually with a chain of preceding targets.

More details in the Derived targets section.

##### Target loss ratio

Same as loss ratio of the corresponding goal.

##### Target exceed ratio

Same as exceed ratio of the corresponding goal.

##### Target width

Similar to goal width attribute.
Doubled from goal width for each level of preceding target.

##### Target min duration sum

Similar to goal min duration sum attribute.
Geometrically interpolated between
initial target duration and goal min duration sum.

##### Target trial duration

When MLRsearch focuses on this target, it measures trials
with this duration.
The value is equal to the minimum of goal final trial duration
and target min duration sum.

Also, this value is used to classify trial results
as short (if trial duration is shorter than this) or long.

#### Derived targets

After receiving the set of search goals,
MLRsearch internally derives a set of search targets.

The derived targets can be seen as forming a chain,
from initial target to final target.
The chain is linked by a reference from a target to its preceding
(towarsds initial) target.

The reference may be implemented as 6th attribute od target.

##### Final target

The final target is the target where the most of attribute values
are directly copied from the coresponding search goal.
Final target width is the same as goal width,
final target trial duration is the same as goal final trial duration,
and final target min duration sum is the same
as the goal min duration sum.

The conditional throughput is found when focusing on the final target.
All non-final targets do not directly affect the conditional throughput,
they are there just as an optimization.

##### Preceding target

Each target may have a preceding target.
Goal attribute Preceding targets governs how many targets are created
in addition to the final target corresponding to the search goal.

Any preceding target has double width, meaning one balanced bisection
is needed to reduce preceding target width to the next target width.

Preceding target min duration sum is exponentially smaller,
aiming for prescribed initial target min duration sum.

Preceding target trial duration is either its min duration sum,
or the corresponding goal's final trial duration, whichever is smaller.

As the preceding min duration sum is shorter than the next duration sum,
MLRsearch is able to achieve the preceding target width
sooner (than with the next target min duration sum).

This way an approximation of the conditional throughput is found,
with the next target needing not as much time to improve the approximation
(compared to not starting with comparably good approximation).

##### Initial target

Initial target is a target without any other target preceding it.
Initial target min duration sum is equal to the corresponding goal's
initial trial duration.

As a consequence, initial target trial duration is equal to its min duration sum.

Inputs of pre-initial trials are chosen so that the trials are considered long
by each initial target. this guarantees the main loop
starts (and keeps) making progress along each target chain.

#### Trial classification

Any trial result can be classified according to any target along two axes.

The two classifications are independent.

This classification is important for defining the conditional throughput.

##### Short trial

If the (measured) trial duration is shorter than
the target trial duration, the trial is called long.

##### Long trial

If the (measured) trial duration is not shorter than
the target trial duration, the trial is called long.

##### Bad trial

If the (measured) trial loss ratio is larger than the target loss ratio,
the trial is called bad.

For example, if the target loss ratio is zero,
a trial is bad as soon as one frame was lost.

##### Good trial

If the (measured) trial loss ratio is not larger than the target loss ratio,
the trial is called good.

For example, if the target loss ratio is zero,
a trial is good only when there were no frames lost.

#### Load stat

A composite of 8 quantities (see subsections)
The quantites depend on a target and a load,
and are computed from all trials measured at that load so far.

The MLRsearch output is the conditional througput,
which is a specific quantity based on load.
As MLRsearch may measure multiple trials at the same load,
and those trials may not have the same duration,
we need a way to classify a set of trial results at the same load.

As the logic is not as straightforward as in other parts
of MLRsearch algorithm, it is best defined using the following
derived quantities (see subsections).
Only the result of load classification (upper bound, lower bound, or undefined)
is important, implementations do not need to track all 8 attributes.

Load stat is the composite defined for one load and one target.
Set of load stats for one load an all targets is called load stats.

Additional trial results may flip the load classification
(between upper and lower bound). Changing from lower bound to undefined
is not possible. Changing from upper bound to undefined is possible,
but unlikely.

##### Long good duration sum

Sum of durations of all long good trials
(at this load, according to this target).

##### Long bad duration sum

Sum of durations of all long bad trials
(at this load, according to this target).

##### Short good duration sum

Sum of durations of all short good trials
(at this load, according to this target).

##### Short bad duration sum

Sum of durations of all short bad trials
(at this load, according to this target).

##### Effective bad duration sum

One divided by tagret exceed ratio, that plus one.
Short good duration sum divided by that.
Short bad duration sum minus that, or zero if that would be negative.
Long bad duration sum plus that is the effective bad duration sum.

Effective bad duration sum is the long bad duration sum
plus some fraction of short bad duration sum.
The fraction is between zero and one (both possibly including).

If there are no short good trials, effective bad duration sum
becomes the duration sum of all bad trials (long or short).

If an exceed ratio computed from short good duration sum
and short bad duration sum is equal or smaller than the target exceed ratio,
effective bad duration sum is equal to just long bad duration sum.

Basically, short good trials can only lessen the impact
of short bad trials, while short bad trials directly contribute
(unless lessened).

A typical example of why a goal needs higher final trial duration
than initial trial duration is when SUT is expected to have large buffers,
so a trial may be too short to see frame losses due to
a buffer becoming full. So a short good trial does not give strong information.
On the other hand, short bad trial is a strong hint SUT would also lose frames
at that load and longer duration.
But if there is a mix of short bad and short good trials,
MLRsearch should not cherry-pick only the short bad ones.

The presented way of computing the effective bad duration sum
aims to be a fair treatment of short good trials.

If the target exceed ratio is zero, the given definition contains
positive infinty as an intermediate value, but still simplifies
to a finite result (long bad duration sum plus short bad duration sum).

##### Missing duration sum

The target min duration sum minus effective bad duration sum
and minus long good duration sum, or zero if that would be negative.

MLRsearch may need up to this duration sum of additional long trials
before classifing the load.

##### Optimistic exceed ratio

The specific quantity based on exceed ratio, where bad duration sum is
the effective bad duration sum, and good duration sum is
the long good duration sum plus the missing duration sum.

This is the value MLRsearch would compare to target exceed ratio
assuming all of the missing duration sum ends up consisting of good long trials.

If there was a bad long trial, optimistic exceed ratio
becomes larger than zero.
Additionally, if the target exceed ratio is zero, optimistic exceed ratio
becomes larger than zero even on one short bad trial.

##### Pessimistic exceed ratio

The specific quantity based on exceed ratio, where bad duration sum is
the effective bad duration sum plus the missing duration sum,
and good duration sum is the long good duration sum.

This is the value MLRsearch would compare to target exceed ratio
assuming all of the missing duration sum ends up consisting of bad long trials.

Note that if the missing duration sum is zero,
optimistic exceed ratio becomes equal to pessimistic exceed ratio.

This is the role target min duration sum has,
it guarantees the two load exceed ratios eventually become the same.
Otherwise, pessimistic exceed ratio
is always bigger than the optimistic exceed ratio.

Depending on trial results, the missing duration sum may not be large enough
to change optimistic (or pessimistic) exceed ratio
to move to the other side compared to target exceed ratio.
In that case, MLRsearch does not need to measure more trials
at this load when focusing on this target.

#### Target bounds

With respect to a target, some loads may be classified as upper or lower bound,
and some of the bounds are treated as relevant.

The subsequent parts of MLRsearch rely only on relevant bounds,
without the need to classify other loads.

##### Upper bound

A load is classified as an upper bound for a target,
if and only if both optimistic exceed ratio
and pessimstic load exceed ratio are larger than the target exceed ratio.

During the search, it is possible there is no upper bound,
for example because every measured load still has too high
missing duration sum.

If the target exceed ratio is zero, and the load has at least one bad trial
(short or long), the load becomes an upper bound.

##### Lower bound

A load is classified as a lower bound for a target,
if and only if both optimistic exceed ratio
and pessimstic load exceed ratio are no larger than the target exceed ratio.

During the search, it is possible there is no lower bound,
for example because every measured load still has too high
missing duration sum.

If the target exceed ratio is zero, all trials at the load of
a lower bound must be good trials (short or long).

Note that so far it is possible for a lower bound to be higher
than an upper bound.

##### Relevant upper bound

For a target, a load is the relevant upper bound,
if and only if it is an upper bound, and all other upper bounds
are larger (as loads) than this load.

In some cases, the max load when classified as a lower bound
is also effectively treated as the relevant upper bound.
(In that case both relevant bounds are equal.)

If that happens for a final target at the end of the search,
the controller output may contain max load as the relevant upper bound
(even if the goal exceed ratio was not exceeded),
signalling SUT performs well even at max load.

If the target exceed ratio is zero, the relevant upper bound
is the smallest load where a bad trial (short or long) has been measured.

##### Relevant lower bound

For a target, a load is the relevant lower bound if it is a lower bound,
it is smaller than the relevant upper bound,
and all other lower bounds smaller than the relevant upper bounds
are also smaller than this load.

Effectively, any load larger than the relevant upper bound is ignored,
thus hiding possible lower bounds larger than the relevant upper bound.

While it is possible for a lower bound to be be larger than an upper bound,
the relevant lower bound is always smaller than the relevant upper bound
(if both exist).

This is a second place where MLRsearch is not symmetric
(the first place was effective bad duration sum).

In some cases, the min load when classified as an upper bound
is also effectively treated as the relevant lower bound.
(In that case both relevant bounds are equal.)

If that happens for a final target at the end of the search,
the controller output may contain min load as the relevant lower bound
even if the exceed ratio was 'overstepped',
signalizing the SUT does not even reach the minimal required performance.

The manager has to make sure this is distingushed in report
from cases where min rate is a legitimate conditional throughput
(e.g. the exceed ratio was not overstepped at the min load).

##### Relevant bounds

The pair of the relevant lower bound and the relevant upper bound.

Useful for determining the width of the relevant bounds.
Any of the bounds may be the effective one (max load or min load).

During the search, one or both bounds may be missing.

A goal is achieved (at the end of the search) when the final target's
relevant bounds have width no larger than the goal width.

Additional trial results may affect current relevant bounds
so a target achieved at one moment may stop being achieved later.

#### Candidate selector

A stateful object focusing on a single goal (whole target chain),
used to determine next trial input.

Internally, a single selector may be using different strategies,
switching between them according to information available.

Public state (shared with all selectors) is the database of all trial results
measured so far and a global width (to avoid interleaving external searches).

Private state (not shared with other selectors) consists of current target,
current strategy (including its private state), current width
(shared by all strategies belonging to the same selector),
and at least two load values (to guarantee progress between targets,
one value may be missing) called initial bounds.

##### Candidate

The trial input (if any) this selector nominates.

Each selector can nominate one candidate (or no candidate)
for the next trial measurement inputs. One candidate is chosen by the controller
(becoming a winner), the selector which nominated the winner may
get prioritized in next nomination round.

The trial duration attribute is always the current target trial duration.
The trial load attribute depends on the current selector strategy.

##### Winner

If the candidate previously nominated by a selector was the one
that got measured, the candidate is called a winner.

Candidates have defined ordering, to simplify finding the winner.
If load differs, the candidate with lower load is preferred.
If load is the same but duration differs, the candidate
with larger duration is preferred.
In case of tie, the selector nominating the previous winner
may ask for preferrence. Otherwise, the goal earlier in the list is preferred.

In most cases, the last two conditions have zero impact on results,
but they make it easier to follow the internal logic.

##### Current target

This is the target this selector tries to achieve currently.

Each selector starts focusing on its initial target.
When a target is reached, its subsequent target becomes the new current,
up until the final target is achieved.

Strategies are designed in such a way each selector always nominates a candidate,
unless the final target (and hence its goal) is achieved.

In principle, it is possible for a goal to stop being achieved
(when subsequent trials change the classification of a relevant bound),
in which case the selector starts nominating a candidate again.
Only when no selector nominates a load, the MLRsearch main loop is done.

A selector never needs to revert its focus to a preceding target,
as it retains enough private state to always make progress.

##### Initial bounds

Two load values used to guarantee progress. One of them may be missing.

At the time the selector is created for the first time,
the two values are computed from forwarding rates of pre-initial trials
(only one is guaranteed to be a relevant bound for the initial target).

When the current target (that the selector is focusing on)
changes from preceding to next, the relevant bounds of the preceding target
become the new initial bounds.

##### Selector strategy

Strategy is a piece of logic for nominating a candidate.
When focusing on current target, selector tries to apply strategies
in a fixed order, nominating the first candidate load a strategy nominates.

Each strategy has its specific conditions on when to nominate a load,
hat global width to set if the candidate becomes a winner,
and when to request a precedence upon winning.

If no strategy wants to nominate, it means the current target is reached.
If it is not the final target, its next target becomes the new current
and the list of strategies is queried again (after resetting any internal state
conditioned on the old target, such as initial bounds).

There is some logic common to all strategies.
If a load is nominated, it must be higher than the relevant lower bound
(if it exists) of the current target, and lower than the relevant upper bound
(if it exists) of the current target.
If, after measuring a trial based on winner candidate, the load does not become
either the new lower relevant bound or the new upper relevant bound
(of the current target), the selector requests to get a precedence.

FIXME: Is precedence needed? Perhaps only for external search expansion?

###### Halve Strategy

Candidate is in the middle of the initial bounds,
if their width is more than one but no more than two target widths.

As the preceding target had double width, just one halving load
needs to be measured.

###### Refine Strategy

Nominate any initial bound that is not an upper bound or a lower bound yet.

The intent is to add more trial result to increase duration sum,
so the load (which was probably a relevant bound of the treceding target)
becomes a relevant bound of the current target.

###### Extend Strategy

Nominate new candidate according to external search.
This strategy activates when one relevant bound is missing.

If the load moves the original relevant bound (not creating the missing bound),
both pre-strategy and global widths are expanded according to goal expansion
coefficient.

An analogous strategy is also queried when both relevant bounds exist,
and its candidate is nominated if it is closer to initial bound
than the candidate of bisect strategy.

###### Bisecting

If both relevant bounds exist for the current target, but they are more than
current target width apart, nominate a middle load.

Contrary to halving, the candidate load does not need to be at the exact middle.
For example if the width of the current relevant bounds
is three times as large as the target width,
it is advantageous to split the interval in 1:2 ratio
(choosing the lower candidate load), as it can save one bisect.

### Controller output

The output object the controller returns to the manager
is a mapping assigning each search goal its conditional output (if it exists).

The controller MAY include more information (if manager accepts it),
for example load stat at relevant bounds.

There MAY be several ways how to communicate the fact a conditional output
does not exist (e.g. min load is classified as an upper bound).
The manager MUST NOT present min load as a conditional output in that case.

If max load is a lower bound, it leads to a valid conditional throughput value.

#### Conditional throughput

The conditional throughput is the average of trial forwarding rates
across long good trials measured at the (offered load classified as)
relevant lower bound (for the goal, at the end of the search).
The average is the weighted arithmetic mean, weighted by trial duration.

If the goal exceed ratio is zero, the definition of the relevant bounds
simplifies significantly.
If additionally the goal loss ratio is zero,
and the goal min duration sum is equal to goal final trial duration,
conditional throughput becomes conditionally compliant with RFC 2544 throughput.
If the goal final trial duration is at least 60 seconds,
the conditional througput becomes unconditionally compliant
with RFC 2544 throughput.

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

# How the problems are addressed

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

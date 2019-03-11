---
title: Probabilistic Loss Ratio Search for Packet Throughput (PLRsearch)
# abbrev: PLRsearch
docname: draft-vpolak-bmwg-plrsearch-01
date: 2019-03-11

ipr: trust200902
area: ops
wg: Benchmarking Working Group
kw: Internet-Draft
cat: info

coding: us-ascii
pi:    # can use array (if all yes) or hash here
#  - toc
#  - sortrefs
#  - symrefs
  toc: yes
  sortrefs:   # defaults to yes
  symrefs: yes

author:
      -
        ins: M. Konstantynowicz
        name: Maciek Konstantynowicz
        org: Cisco Systems
        role: editor
        email: mkonstan@cisco.com
      -
        ins: V. Polak
        name: Vratko Polak
        org: Cisco Systems
        role: editor
        email: vrpolak@cisco.com

normative:
  RFC2544:
  RFC8174:

informative:
  draft-vpolak-mkonstan-bmwg-mlrsearch:
    target: https://tools.ietf.org/html/draft-vpolak-mkonstan-bmwg-mlrsearch-00
    title: "Multiple Loss Ratio Search for Packet Throughput (MLRsearch)"
    date: 2018-11

--- abstract

This document addresses challenges while applying methodologies
described in [RFC2544] to benchmarking software based NFV (Network
Function Virtualization) data planes over an extended period of time,
sometimes referred to as "soak testing". Packet throughput search
approach proposed by this document assumes that system under test is
probabilistic in nature, and not deterministic.

--- middle

# Motivation

Network providers are interested in throughput a system can sustain.

[RFC2544] assumes loss ratio is given by a deterministic function of
offered load. But NFV software systems are not deterministic enough.
This makes deterministic algorithms (such as Binary Search per [RFC2544]
and [draft-vpolak-mkonstan-bmwg-mlrsearch] with single trial) to return
results, which when repeated show relatively high standard deviation,
thus making it harder to tell what "the throughput" actually is.

We need another algorithm, which takes this indeterminism into account.

# Relation To RFC2544

The aim of this document is to become an extension of [RFC2544] suitable
for benchmarking networking setups such as software based NFV systems.

# Terms And Assumptions

## Device Under Test

In software networking, "device" denotes a specific piece of software
tasked with packet processing. Such device is surrounded with other
software components (such as operating system kernel). It is not
possible to run devices without also running the other components, and
hardware resources are shared between both.

For purposes of testing, the whole set of hardware and software
components is called "system under test" (SUT). As SUT is the part of
the whole test setup performance of which can be measured by [RFC2544]
methods, this document uses SUT instead of [RFC2544] DUT.

Device under test (DUT) can be re-introduced when analysing test results
using whitebox techniques, but this document sticks to blackbox testing.

## System Under Test

System under test (SUT) is a part of the whole test setup whose
performance is to be benchmarked. The complete methodology contains
other parts, whose performance is either already established, or not
affecting the benchmarking result.

## SUT Configuration

Usually, system under test allows different configurations, affecting
its performance. The rest of this document assumes a single
configuration has been chosen.

## SUT Setup

Similarly to [RFC2544], it is assumed that the system under test has
been updated with all the packet forwarding information it needs, before
the trial measurements (see below) start.

## Network Traffic

Network traffic is a type of interaction between system under test and
the rest of the system (traffic generator), used to gather information
about the system under test performance. PLRsearch is applicable only to
areas where network traffic consists of packets.

## Packet

Unit of interaction between traffic generator and the system under test.
Term "packet" is used also as an abstractions of Ethernet frames.

### Packet Offered

Packet can be offered, which means it is sent from traffic generator
to the system under test.

Each offered packet is assumed to become received or lost in a short
time.

### Packet Received

Packet can be received, which means the traffic generator verifies it
has been processed. Typically, when it is succesfully sent from the
system under test to traffic generator.

It is assumed that each received packet has been caused by an offered
packet, so the number of packets received cannot be larger than the
number of packets offered.

### Packet Lost

Packet can be lost, which means sent but not received in a timely
manner.

It is assumed that each lost packet has been caused by an offered
packet, so the number of packets lost cannot be larger than the number
of packets offered.

Usually, the number of packets lost is computed as the number of packets
offered, minus the number of packets received.

###  Other Packets

PLRsearch is not considering other packet behaviors known from
networking (duplicated, reordered, greatly delayed), assuming the test
specification reclassifies those behaviors to fit into the first three
categories.

### Tasks As Packets

Ethernet frames are the prime example of packets, but other units are
possible.

For example, a task processing system can fit the description. Packet
offered can stand for task submitted, packet received for task processed
successfully, and packet lost for task aborted (or not processed
successfully for some other reason).

In networking context, such a task can be a route update.

## Traffic Profile

Usually, the performance of the system under test depends on a "type" of
a particular packet (for example size), and "composition" if the network
traffic consists of a mixture of different packet types.

Also, some systems under test contain multiple "ports" packets can be
offered to and received from.

All such qualities together (but not including properties of trial
measurements) are called traffic profile.

Similarly to system under test configuration, this document assumes only
one traffic profile has been chosen for a particular test.

##  Traffic Generator

Traffic generator is the part of the whole test setup, distinct from the
system under test, responsible both for offering packets in a highly
predictable manner (so the number of packets offered is known), and for
counting received packets in a precise enough way (to distinguish lost
packets from tolerably delayed packets).

Traffic generator must offer only packets compatible with the traffic
profile, and only count similarly compatible packets as received.

## Offered Load

Offered load is an aggregate rate (measured in packets per second) of
network traffic offered to the system under test, the rate is kept
constant for the duration of trial measurement.

## Trial Measurement

Trial measurement is a process of stressing (previously setup) system
under test by offering traffic of a particular offered load, for a
particular duration.

After that, the system has a short time to become idle, while the
traffic generator decides how many packets were lost.

After that, another trial measurement (possibly with different offered
load and duration) can be immediately performed. Traffic generator
should ignore received packets caused by packets offered in previous
trial measurements.

## Trial Duration

Duration for which the traffic generator was offering packets at
constant offered load.

In theory, care has to be taken to ensure the offered load and trial
duration predict integer number of packets to offer, and that the
traffic generator really sends appropriate number of packets within
precisely enough timed duration. In practice, such consideration do not
change PLRsearch result in any significant way.

## Packet Loss

Packet loss is any quantity describing a result of trial measurement.

It can be loss count, loss rate or loss ratio. Packet loss is zero (or
non-zero) if either of the three quantities are zero (or non-zero,
respecively).

### Loss Count

Number of packets lost (or delayed too much) at a trial measurement by
the system under test as determined by packet generator. Measured in
packets.

### Loss Rate

Loss rate is computed as loss count divided by trial duration. Measured
in packets per second.

### Loss Ratio

Loss ratio is computed as loss count divided by number of packets
offered. Measured as a real (in practice rational) number between zero
or one (including).

## Trial Order Independent System

Trial order independent system is a system under test, proven (or just
assumed) to produce trial measurement results that display trial order
independence.

That means when a pair of consequent trial measurements are performed,
the probability to observe a pair of specific results is the same, as
the probability to observe the reversed pair of results whe performing
the reversed pair of consequent measurements.

PLRsearch assumes the system under test is trial order independent.

In practice, most system under test are not entirely trial order
independent, but it is not easy to devise an algorithm taking that into
account.

## Trial Measurement Result Distribution

When a trial order independent system is subjected to repeated trial
measurements of constant offered load and duration, Law of Large Numbers
implies the observed loss count frequencies will converge to a specific
probability distribution over possible loss counts.

This probability distribution is called trial measurement result
distribution, and it depends on all properties fixed when defining it.
That includes the system under test, its chosen configuration, the
chosen traffic profile, the offered load and the trial duration.

As the system is trial order independent, trial measurement result
distribution does not depend on results of few initial trial
measurements, of any offered load or (finite) duration.

## Average Loss Ratio

Probability distribution over some (finite) set of states enables
computation of probability-weighted average of any quantity evaluated on
the states (called the expected value of the quantity).

Average loss ratio is simply the expected value of loss ratio for a
given trial measurement result distribution.

## Duration Independent System

Duration independent system is a trial order independent system, whose
trial measurement result distribution is proven (or just assumed) to
display practical independence from trial duration. See definition of
trial duration for discussion on practical versus theoretical.

The only requirement is for average loss ratio to be independent of
trial duration.

In theory, that would necessitate each trial measurement result
distribution to be a binomial distribution. In practice, more
distributions are allowed.

PLRsearch assumes the system under test is duration independent, at
least for trial durations typically chosen for trial measurements
initiated by PLRsearch.

## Load Regions

For a duration independent system, trial measurement result distribution
depends only on offered load.

It is convenient to name some areas of offered load space by possible
trial results.

### Zero Loss Region

A particular offered load value is said to belong to zero loss region,
if the probability of seeing non-zero loss trial measurement result is
exactly zero, or at least practically indistinguishable from zero.

### Guaranteed Loss Region

A particular offered load value is said to belong to guaranteed loss
region, if the probability of seeing zero loss trial measurement result
(for non-negligible count of packets offered) is exactly zero, or at
least practically indistinguishable from zero.

### Non-Deterministic Region

A particular offered load value is said to belong to non-deterministic
region, if the probability of seeing zero loss trial measurement result
(for non-negligible count of packets offered) practically
distinguishable from both zero and one.

### Normal Region Ordering

Although theoretically the three regions can be arbitrary sets, this
document assumes they are intervals, where zero loss region contains
values smaller than non-deterministic region, which in turn contains
values smaller than guaranteed loss region.

## Deterministic System

A hypothetical duration independent system with normal region ordering,
whose non-deterministic region is extremely narrow; only present due to
"practical distinguishibility" and cases when the expected number of
packets offered is not and integer.

A duration independent system which is not deterministic is called non-
deterministic system.

## Througphput

Throughput is the highest offered load provably causing zero packet loss
for trial measurements of duration at least 60 seconds.

For duration independent systems with normal region ordering, the
throughput is the highest value within the zero loss region.

## Deterministic Search

Any algorithm that assumes each measurement is a proof of the offered
load belonging to zero loss region (or not) is called deterministic
search.

This definition includes algorithms based on "composite measurements"
which perform multiple trial measurements, somehow re-classifying
results pointing at non-deterministic region.

Binary Search is an example of deterministic search.

Single run of a deterministic search launched against a deterministic
system is guaranteed to find the throughput with any prescribed
precision (not better than non-deterministic region width).

Multiple runs of a deterministic search launched against a non-
deterministic system can return varied results within non-deterministic
region. The exact distribution of deterministic search results depends
on the algorithm used.

## Probabilistic Search

Any algorithm which performs probabilistic computations based on
observed results of trial measurements, and which does not assume that
non-deterministic region is practically absent is called probabilistic
search.

A probabilistic search algorithm, which would assume that non-
deterministic region is practically absent, does not really need to
perform probabilistic computations, so it would become a deterministic
search.

While probabilistic search for estimating throughput is possible, it
would need a careful model for boundary between zero loss region and
non-deterministic region, and it would need a lot of measurements of
almost surely zero loss to reach good precision.

## Loss Ratio Function

For any duration independent system, the average loss ratio depends only
on offered load (for a particular test setup).

Loss ratio function is the name used for the function mapping offered
load to average loss ratio.

This function is initially unknown.

## Target Loss Ratio

Input parameter of PLRsearch. The average loss ratio the output of
PLRsearch aims to achieve.

## Critical Load

Aggregate rate of network traffic, which would lead to average loss
ratio exactly matching target loss ratio (when used as the offered load
for infinite many trial measurement).

## Critical Load Estimate

Any quantitative description of the possible critical load PLRsearch is
able to give after observing finite amount of trial measurements.

## Fitting Function

Any function PLRsearch uses internally instead of the unknown loss ratio
function. Typically chosen from small set of formulas (shapes) with few
parameters to tweak.

## Shape of Fitting Function

Any formula with few undetermined parameters.

## Parameter Space

A subset of Real Coordinate Space. A point of parameter space is a
vector of real numbers. Fitting function is defined by shape (a formula
with parameters) and point of parameter space (specifying values for the
parameters).

# Abstract Algorithm

## High level description

PLRsearch accepts some input arguments, then iteratively performs trial
measurements at varying offered loads (and durations), and returns some
estimates of critical load.

PLRsearch input arguments form three groups.

First group has a single argument: measurer. This is a callback
(function) accepting offered load and duration, and returning the
measured loss count.

Second group consists of load related arguments required for measurer to
work correctly, typically minimal and maximal load to offer. Also,
target loss ratio (if not hardcoded) is a required argument.

Third group consists of time related arguments. Typically the duration
for the first trial measurement, duration increment per subsequent trial
measurement and total time for search. Some PLRsearch implementation may
use estimation accuracy parameters as an exit condition instead of total
search time.

The returned quantities should describe the final (or best) estimate of
critical load. Implementers can chose any description that suits their
users, typically it is average and standard deviation, or lower and
upper boundary.

## Main Ideas

The search tries to perform measurements at offered load close to the
critical load, because measurement results at offered loads far from the
critical load give less information on precise location of the critical
load. As virtually every trial measurement result alters the estimate of
the critical load, offered loads vary as they approach the critical
load.

PLRsearch uses Bayesian Inference, computed using numerical integration,
which takes long time to get reliable enough results. Therefore it takes
some time before the most recent measurement result starts affecting
subsequent offered loads and critical rate estimates.

During the search, PLRsearch spawns few processes that perform numerical
computations, the main process is calling the measurer to perform trial
measurements, without any significant delays between them. The durations
of the trial measurements are increasing linearly, as higher number of
trial measurement results take longer to process.

## Probabilistic Notions

Before internals of PLRsearch are described, we need to define notions
valid for situations when loss ratio is not entirely determined by
offered load.

Some of the notions already incorporate assumptions the PLRsearch
algorithm applies.

### Loss Count Only

It is assumed that the traffic generator detects duplicate packets on
receive, and reports this as an error.

No latency (or other information) is taken into account.

### Independent Trials

PLRsearch still assumes the system under test can be subjected to trial
measurements. The loss count is no longer determined precisely, but it
is assumed that for every system under test, its configuration, traffic
type and trial duration, there is a probability distribution over
possible loss counts.

This implies trial measurements are probabilistic, but the distribution
is independent of possible previous trial measurements.

Independence from previous measurements is not guaranteed in the real
world. The previous measurements may improve performance (via long-term
warmup effects), or decrease performance (due to long-term resource
leaks).

### Trial Durations

[RFC2544] motivates the usage of at least 60 second duration by the idea
of the system under test slowly running out of resources (such as memory
buffers).

Practical results when measuring NFV software systems show that relative
change of trial duration has negligible effects on average loss ratio,
compared to relative change in offered load.

While the standard deviation of loss ratio usually shows some effects of
trial duration, they are hard to model; so further assumtions in
PLRsearch will make it insensitive to trial duration.

### Target Loss Ratio

Loss ratio function could be used to generalize throughput as the
biggest offered load which still leads to zero average loss ratio.
Unfortunately, most realistic loss ratio functions always predict non-
zero (even if negligible) average loss ratio.

On the other hand, users do not really require the average loss ratio to
be an exact zero. Most users are satisfied when the average loss ratio
is small enough.

One of PLRsearch inputs is called target loss ratio. It is the loss
ratio users would accept as negligible.

(TODO: Link to why we think 1e-7 is acceptable loss ratio.)

### Critical Load

Critical load (sometimes called critical rate) is the offered load which
leads to average loss ratio to become exactly equal to the target loss
ratio.

In principle, there could be such loss ratio functions which allow more
than one offered load to achieve target loss ratio. To avoid that,
PLRsearch assumes only increasing loss ratio functions are possible.

Similarly, some loss ratio functions may never return the target loss
ratio. PLRsearch assumes loss ratio function is continuous, that the
average loss ratio approaches zero as offered load approaches zero, and
that the average loss ratio approaches one as offered load approaches
infinity.

Under these assumptions, each loss ratio function has unique critical
load. PLRsearch attempts to locate the critical load.

### Load Regions

Critical region is the interval of offered load close to critical load,
where single measurement is not likely to distinguish whether the
critical load is higher or lower than the current offered load.

In typical case of small target loss ratio, rates below critical region
form "zero loss region", and rates above form "high loss region".

### Finite Models

Of course, finite amount of trial measurements, each of finite duration
does not give enough information to pinpoint the critical load exactly.
Therefore the output of PLRsearch is just an estimate with some
precision.

Aside of the usual substitution of infinitely precise real numbers by
finitely precise floating point numbers, there are two other instances
within PLRsearch where an objects of high information are replaced by
objects of low information.

One is the probability distribution of loss count, which is replaced by
average loss ratio. The other is the loss ratio function, which is
replaced by a few parameters, to be described later.

## PLRsearch Building Blocks

Here we define notions used by PLRsearch which are not applicable to
other search methods, nor probabilistic systems under test, in general.

### Bayesian Inference

Having reduced the model space significantly, the task of estimating the
critical load becomes simple enough so that Bayesian inference can be
used (instead of neural networks, or other Artifical Intelligence
methods).

In this case, the few parameters describing the loss ration function
become the model space. Given a prior over the model space, and trial
duration results, a posterior distribution can be computed, together
with quantities describing the critical load estimate.

### Iterative Search

The idea PLRsearch is to iterate trial measurements, using Bayesian
inference to compute both the current estimate of the critical load and
the next offered load to measure at.

The required numerical computations are done in parallel with the trial
measurements.

This means the result of measurement "n" comes as an (additional) input
to the computation running in parallel with measurement "n+1", and the
outputs of the computation are used for determining the offered load for
measurement "n+2".

Other schemes are possible, aimed to increase the number of measurements
(by decreasing their duration), which would have even higher number of
measurements run before a result of a measurement affects offered load.

### Poisson Distribution

For given offered load, number of packets lost during trial measurement
is assumed to come from Poisson distribution, and the (unknown) Poisson
parameter is expressed as average loss ratio.

Side note: Binomial Distribution is a better fit compared to Poisson
distribution (acknowledging that the number of packets lost cannot be
higher than the number of packets offered), but the difference tends to
be relevant only in high loss region. Using Poisson distribution lowers
the impact of measurements in high loss region, thus helping the
algorithm to focus on critical region better.

### Fitting Functions

There are great many increasing functions (as candidates for the loss
ratio function).

To make the space of possible functions more tractable, some other
simplifying assumptions are needed. As the algorithm will be examining
(also) loads very close to the critical load, linear approximation to
the loss rate function around the critical load is important. But as the
search algorithm needs to evaluate the function also far away from the
critical region, the approximate function has to be reasonably behaved
for every positive offered load, specifically it cannot predict non-
positive packet loss ratio.

Within this document, "fitting function" is the name for such a
reasonably behaved function, which approximates the loss ratio function
well in the critical region.

### Measurement Impact

Results from trials far from the critical region are likely to affect
the critical rate estimate negatively, as the fitting function does not
need to be a good approximation there. This is true mainly for high loss
region, as in zero loss region even badly behaved fitting function
predicts loss count to be "almost zero", so seeing a measurement
confirming the loss has been zero indeed has small impact.

Discarding some results, or "suppressing" their impact with ad-hoc
methods (other than using Poisson distribution instead of binomial) is
not used, as such methods tend to make the overall search unstable. We
rely on most of measurements being done (eventually) within the critical
region, and overweighting far-off measurements (eventually) for well-
behaved fitting functions.

Speaking about new trials, each next trial will be done at offered load
equal to the current average of the critical load. Alternative methods
for selecting offered load might be used, in an attempt to speed up
convergence. For example by employing the aforementioned unstable ad-hoc
methods.

### Fitting Function Coefficients Distribution

To accomodate systems with different behaviours, the fitting function is
expected to have few numeric parameters affecting its shape (mainly
affecting the linear approximation in the critical region).

The general search algorithm can use whatever increasing fitting
function, some specific functions can described later.

It is up to implementer to chose a fitting function and prior
distribution of its parameters. The rest of this document assumes each
parameter is independently and uniformly distributed over a common
interval. Implementers are to add non-linear transformations into their
fitting functions if their prior is different.

Exit condition for the search is either the standard deviation of the
critical load estimate becoming small enough (or similar), or overal
search time becoming long enough.

The algorithm should report both average and standard deviation for its
critical load posterior. If the reported averages follow a trend
(without reaching equilibrium), average and standard deviation should
refer to the equilibrium estimates based on the trend, not to immediate
posterior values.

### Integration

The posterior distributions for fitting function parameters will not be
integrable in general.

The search algorithm utilises the fact that trial measurement takes some
time, so this time can be used for numeric integration (using suitable
method, such as Monte Carlo) to achieve sufficient precision.

### Optimizations

After enough trials, the posterior distribution will be concentrated in
a narrow area of the parameter space. The integration method should take
advantage of that.

Even in the concentrated area, the likelihood can be quite small, so the
integration algorithm should avoid underflow errors by some means,
for example by tracking the logarithm of the likelihood.

# Sample Implementation Specifics: FD.io CSIT

The search receives min_rate and max_rate values, to avoid measurements
at offered loads not supporeted by the traffic generator.

The implemented tests cases use bidirectional traffic. The algorithm
stores each rate as bidirectional rate (internally, the algorithm is
agnostic to flows and directions, it only cares about overall counts of
packets sent and packets lost), but debug output from traffic generator
lists unidirectional values.

## Measurement Delay

In a sample implemenation in FD.io CSIT project, there is roughly 0.5
second delay between trials due to restrictons imposed by packet traffic
generator in use (T-Rex).

As measurements results come in, posterior distribution computation
takes more time (per sample), although there is a considerable constant
part (mostly for inverting the fitting functions).

Also, the integrator needs a fair amount of samples to reach the region
the posterior distribution is concentrated at.

And of course, speed of the integrator depends on computing power of the
CPU the algorithm is able to use.

All those timing related effects are addressed by arithmetically
increasing trial durations with configurable coefficients (currently 5.1
seconds for the first trial, each subsequent trial being 0.1 second
longer).

## Rounding Errors and Underflows

In order to avoid them, the current implementation tracks natural
logarithm (instead of the original quantity) for any quantity which is
never negative. Logarithm of zero is minus infinity (not supported by
Python), so special value "None" is used instead. Specific functions for
frequent operations (such as "logarithm of sum of exponentials") are
defined to handle None correctly.

## Fitting Functions

Current implementation uses two fitting functions. In general, their
estimates for critical rate differ, which adds a simple source of
systematic error, on top of randomness error reported by integrator.
Otherwise the reported stdev of critical rate estimate is
unrealistically low.

Both functions are not only increasing, but also convex (meaning the
rate of increase is also increasing).

As Primitive Function to any positive function is an increasing
function, and Primitive Function to any increasing function is convex
function; both fitting functions were constructed as double Primitive
Function to a positive function (even though the intermediate increasing
function is easier to describe).

As not any function is integrable, some more realistic functions
(especially with respect to behavior at very small offered loads) are
not easily available.

Both fitting functions have a "central point" and a "spread", varied by
simply shifting and scaling (in x-axis, the offered load direction) the
function to be doubly integrated. Scaling in y-axis (the loss rate
direction) is fixed by the requirement of transfer rate staying nearly
constant in very high offered loads.

In both fitting functions (as they are a double Primitive Function to a
symmetric function), the "central point" turns out to be equal to the
aforementioned limiting transfer rate, so the fitting function parameter
is named "mrr", the same quantity our Maximum Receive Rate tests are
designed to measure.

Both fitting functions return logarithm of loss rate, to avoid rounding
errors and underflows. Parameters and offered load are not given as
logarithms, as they are not expected to be extreme, and the formulas are
simpler that way.

Both fitting functions have several mathematically equivalent formulas,
each can lead to an overflow or underflow in different places. Overflows
can be eliminated by using different exact formulas for different
argument ranges. Underflows can be avoided by using approximate formulas
in affected argument ranges, such ranges have their own formulas to
compute. At the end, both fitting function implementations contain
multiple "if" branches, discontinuities are a possibility at range
boundaries.

Offered load for next trial measurement is the average of critical rate
estimate. During each measurement, two estimates are computed, even
though only one (in alternating order) is used for next offered load.

### Stretch Function

The original function (before applying logarithm) is Primitive Function
to Logistic Function. The name "stretch" is used for related a function
in context of neural networks with sigmoid activation function.

Formula for stretch function: loss rate (r) computed from offered load
(b), mrr parameter (m) and spread parameter (a):

r = a (Log(E^(b/a) + E^(m/a)) - Log(1 + E^(m/a)))

### Erf Function

The original function is double Primitive Function to Gaussian Function.
The name "erf" comes from error function, the first primitive to
Gaussian.

Formula for erf function: loss rate (r) computed from offered load (b),
mrr parameter (m) and spread parameter (a):

r = (b + (a (E^(-((b - m)^2/a^2)) - E^(-(m^2/a^2))))/Sqrt(Pi) + (b - m) Erf((b - m)/a) - m Erf(m/a))/2

## Prior Distributions

The numeric integrator expects all the parameters to be distributed
(independently and) uniformly on an interval (-1, 1).

As both "mrr" and "spread" parameters are positive and not not
dimensionless, a transformation is needed. Dimentionality is inherited
from max_rate value.

The "mrr" parameter follows a Lomax Distribution with alpha equal to
one, but shifted so that mrr is always greater than 1 packet per second.

The "stretch" parameter is generated simply as the "mrr" value raised to
a random power between zero and one; thus it follows a Reciprocal
Distribution.

## Integrator

After few measurements, the posterior distribution of fitting function
arguments gets quite concentrated into a small area. The integrator is
using Monte Carlo with Importance Sampling where the biased distribution
is Bivariate Gaussian distribution, with deliberately larger variance.
If the generated sample falls outside (-1, 1) interval, another sample
is generated.

The the center and the covariance matrix for the biased distribution is
based on the first and second moments of samples seen so far (within the
computation), with the following additional features designed to avoid
hyper-focused distributions.

Each computation starts with the biased distribution inherited from the
previous computation (zero point and unit covariance matrix is used in
the first computation), but the overal weight of the data is set to the
weight of the first sample of the computation. Also, the center is set
to the first sample point. When additional samples come, their weight
(including the importance correction) is compared to the weight of data
seen so far (within the computation). If the new sample is more than one
e-fold more impactful, both weight values (for data so far and for the
new sample) are set to (geometric) average if the two weights. Finally,
the actual sample generator uses covariance matrix scaled up by a
configurable factor (8.0 by default).

This combination showed the best behavior, as the integrator usually
follows two phases. First phase (where inherited biased distribution or
single big sasmples are dominating) is mainly important for locating the
new area the posterior distribution is concentrated at. The second phase
(dominated by whole sample population) is actually relevant for the
critical rate estimation.

# IANA Considerations

..

# Security Considerations

..

# Acknowledgements

..

--- back
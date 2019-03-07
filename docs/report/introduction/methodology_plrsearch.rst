.. _`PLRsearch algorithm`:

PLRsearch
^^^^^^^^^

Applicability
~~~~~~~~~~~~~

The PLRsearch algorithm has been developed with intended use
of determining usability of network traffic forwarding devices.

But not every aspect of network traffic forwarding affects PLRsearch operation,
allowing application of PLRsearch on a broader set of problems.

Still, most of terminology in this document os borrowed from the area
of network benchmarking, with only minimal comments on other possible
applications for PLRsearch.

Terms and assumptions
~~~~~~~~~~~~~~~~~~~~~

Device under test
`````````````````

Device under test is a sub-system whose performance is to be benchmarked.
The complete methodology contains other sub-systems, whose performance
is either already established, or not affecting the benchmarking result.

Usually, device under test allows different configurations,
affecting its performance. The rest of this document assumes
a single configuration has been chosen.

Network traffic
```````````````

Network traffic is a type of interaction between device under test
and the rest of the system (traffic generator), used to gather information
about the device performance. PLRsearch is applicable only to areas
where network traffic consists of packets.

Packet
``````

Unit of interaction between traffic generator and device under test.

Packet offered
--------------

Packet can be offered, which means it is sent from traffic generator
to device under test.

Each offered packet is assumed to become received or lost in a short time.

Packet received
---------------

Packet can be received, which means it is succesfully sent
from device under test to traffic generator.

It is assumed that each received packet has been caused by an offered packet,
so the number of packets received cannot be larger than the number
of packets offered.

Packet lost
-----------

Packet can be lost, which means sent but not received in a timely manner.

It is assumed that each lost packet has been caused by an offered packet,
so the number of packets lost cannot be larger than the number
of packets offered.

Usually, the number of packets lost is computed
as the number of packets offered, minus the number of packets received.

Other packets
-------------

PLRsearch is not considering other packet behaviors known from networking
(duplicated, reordered, greatly delayed), assuming the test specification
reclassifies those behaviors to fit into the first three categories.

Tasks as packets
----------------

Ethernet frames are the prime example of packets, but other units are possible.

For example, a task processing system can fit the description.
Packet offered can stand for task submitted, packet received
for task processed successfully, and packet lost for task aborted
(or not processed successfully for some other reason).

Traffic profile
```````````````

Usually, the performance of the device under test depends on a "type"
of a particular packet (for example size), and "composition"
if the network traffic consists of a mixture of different packet types.

Also, some devices contain multiple "ports" packets can be offered to,
and received from.

All such qualities together (but not including properties of trial measurements)
are called traffic profile.

Similarly to device configuration, this document assumes
only one traffic profile has been chosen for a particular test.

Traffic generator
`````````````````

Traffic generator is the part of overall system, distinct from
the device under test, responsible both for offering packets in a highly
predictable manner (so the number of packets offered is known),
and for counting received packets in a precise enough way
(to distinguish lost packets from tolerably delayed packets).

Some devices under test use network traffic in initial configuration phase.
In this document, such traffic is considered to come from a sub-system
different from traffic generator.

Traffic generator must offer only packets compatible with the traffic profile,
and only count similarly compatible packets as received.

Offered load
````````````

Offered load is an aggregate rate (measured in packets per second)
of network traffic offered to device under test,
the rate is kept constant for the duration of trial measurement.

Trial measurement
`````````````````

Trial measurement is a process of stressing (previously idle) device under test
by offering traffic of a particular offered load, for a particular duration.

After that, the system has a short time to become idle again,
while the traffic generator decides how many packets were lost.

After that, another trial measurement (possibly with different offered load
and duration) can be performed.

Trial duration
``````````````

Duration for which the traffic generator was offering packets
at constant offered load.

In theory, care has to be taken to ensure the offered load and trial duration
predict integer number of packets to offer, and that the traffic generator
really sends appropriate number of packets within precisely enough
timed duration. In practice, such consideration do not change PLRsearch
result in any significant way.

Packet loss
```````````

Packet loss is any quantity describing a result of trial measurement.

It can be loss count, loss rate or loss ratio.
Packet loss is zero (or non-zero) if either of the three quantities are zero
(or non-zero, respecively).

Loss count
----------

Number of packets lost (or delayed too much) at a trial measurement
by the device under test as determined by packet generator. Measured in packets.

Loss rate
---------

Loss rate is computed as loss count divided by trial duration.
Measured in packets per second.

Loss ratio
----------

Loss ratio is computed as loss count divided by number of packets offered.
Measured as a real (in practice rational) number between zero or one (including).

Trial order independent device
``````````````````````````````

Trial order independent device is a device under test,
proven (or just assumed) to produce trial measurement
results that display some degree of trial order independence.

PLRsearch assumes the device under test is trial order independent.

In practice, most device under test are not entirely trial order independent,
but it is not easy to devise an algorithm taking that into account.

Trial measurement result distribution
`````````````````````````````````````

When a trial order independent device is subjected to repeated
trial measurements of constant offered load and duration,
'law of large numbers'_ implies the observed loss count frequencies
will converge to a specific probability distribution over possible loss counts.

This probability distribution is called trial measurement result distribution,
and it depends on all properties fixed when defining it.
That includes the device under test, its chosen configuration,
the chosen traffic profile, the offered load and the trial duration.

Average loss ratio
``````````````````

Probability distribution over some (finite) set of states
enables computation of weighted average of any quantity evaluated on the states.

Average loss ratio is simply the weighted average of loss ratio
for a given trial measurement result distribution.

Duration independent device
```````````````````````````

Duration independent device is a trial order independent device,
whose trial measurement result distribution is proven (or just assumed)
to display some degree of independence from trial duration.

The only requirement is for average loss ratio to be independent
of trial duration.

In principle, that would necessitate each trial measurement result distribution
to be a `binomial distribution`_, but see below for more PLRsearch assumptions.

PLRsearch assumes the device under test is duration independent,
at least for trial durations typically chosen for trial measurements
initiated by PLRsearch.

Load regions
````````````

For a duration independent device, trial measurement result distribution
depends only on offered load (within one PLRsearch run).

It is convenient to name some areas of offered load space
by possible trial results.

Zero loss region
----------------

A particular offered load value is said to belong to zero loss region,
if the probability of seeing non-zero loss trial measurement result
is exactly zero, or at least practically indistinguishable from zero.

Guaranteed loss region
----------------------

A particular offered load value is said to belong to big loss region,
if the probability of seeing zero loss trial measurement result
(for non-negligible count of packets offered)
is exactly zero, or at least practically indistinguishable from zero.

Non-deterministic region
------------------------

A particular offered load value is said to belong to non-deterministic region,
if the probability of seeing zero loss trial measurement result
(for non-negligible count of packets offered)
practically distinguishable from both zero and one.

Normal region ordering
----------------------

Although theoretically the three regions can be arbitrary sets,
this document assumes they are intervals, where zero loss region
contains values smaller than non-deterministic region,
which in turn contains values smaller than guaranteed loss region.

Deterministic device
````````````````````

A hypothetical duration independent device with normal region ordering,
whose non-deterministic region is extremely narrow;
only present due to "practical distinguishibility" and cases
when the expected number of packets offered is not and integer.

A duration independent device which is not deterministic
is called non-deterministic device.

Througphput
```````````

Throughput is the highest offered load proven to cause zero packet loss
(presumably reliably) for trial measurements of duration at least 60 seconds.

For duration independent devices with normal region ordering,
the throughput is the highest value within the zero loss region.

Deterministic search
````````````````````

Any algorithm that assumes each measurement is a proof of the offered load
belonging to zero loss region (or not) is called deterministic search.

This definition includes algorithms based on "composite measurements"
which perform multiple trial measurements, somehow re-classifying
results pointing at non-deterministic region.

`Binary search`_ is an example of deterministic search.

Single run of a deterministic search launched against a deterministic device
is guaranteed to find the throughput with any prescribed precision
(not better than non-deterministic region width).

Multiple runs of a deterministic search launched against
a non-deterministic device can return varied results
within non-deterministic region.







Target loss ratio: Input parameter of PLRsearch.
The average loss ratio the output of PLRsearch aims to achieve.

Critical load: Aggregate rate of network traffic, which would lead to
average loss ratio exactly matching target loss ratio
(when used as the offered load for infinite many trial measurement).

Critical load estimate: Any quantitative description of the possible
critical load PLRsearch is able to give
after observing finite amount of trial measurements.

Loss ratio function: Mapping from offered load to average loss ratio.
This is an unknown characteristic of the device under test.

Fitting function: Any function PLRsearch uses internally instead of
the unknown loss ratio function. Typically chosen from small set
of formulas (shapes) with few parameters to tweak.

Shape of fitting function: Any formula with few undetermined parameters.

Parameter space: A subset of `real coordinate space`_. A point of parameter
space is a vector of real numbers. Fitting function is defined by shape
(a formula with parameters) and point of parameter space (specifying values
for the parameters).

Abstract algorithm
~~~~~~~~~~~~~~~~~~

.. TODO: Refer to packet forwarding terminology, such as "offered load" and
   "loss ratio".

Eventually, a better description of the abstract search algorithm
will appear at this IETF standard: `plrsearch draft`_.

Deterministic throughput
````````````````````````

`RFC 2544`_ is the reference for measuring throughput of network devices.
The trhoughput definition is centered around the idea of trial measurement.
After the system under test is started, initialized (say ARP),
and (if needed) warmed-up, the traffic generator is set
to start sending packets (of defined size and content) at a constant rate
(called offered load). After some time (called trial duration),
traffic generator stops sending packets, and there is some time
for counting late packets and (if needed) system cool-down.
After this cool down, the system under test is assumed to be as ready
for next trial measurement, as it was after the first initialization
(or warm-up).

Packets not registered by the traffic generator during the traffic phase
nor the cool-down phase are considered lost.
Thus, any trial measurement at given system configuration, traffic type,
trial duration and offered load leads to some loss count.
The number of packets sent by the traffic generator
is determined by offered load and trial duration.
Loss ratio is a real (not integer) number, computed as loss count
divided by the number of packets sent.

Throughput (for a given system, configuration and traffic type)
is defined as largest offered load which still leads to zero loss ratio
(for trial duration at least 60 seconds).

Implicit in this definition is the assumption of loss ratio
being a deterministic function of offered load (other things being equal).

Motivation for PLRsearch
````````````````````````

Network providers are interested in throughput a device can sustain.

`RFC 2544`_ assumes loss ratio is given by a deterministic function of
offered load. But NFV software devices are not deterministic enough.
This makes deterministic algorithms (such as binary search per RFC 2544
and MLRsearch with single trial) to return results,
which when repeated show relatively high standard deviation,
thus making it harder to tell what "the throughput" actually is.

We need another algorithm, which takes this indeterminism into account.

High level description
``````````````````````

Black box view
--------------

See later text for explanations for notions such as
"target loss ratio" and "critical load".

PLRsearch accepts some input arguments, then iteratively performs
trial measurements at varying offered loads (and durations),
and returns some estimates of critical load.

PLRsearch input arguments form three groups.
First group has a single argument: measurer. This is a callback (function)
accepting offered load and duration, and returning the measured loss count.

Second group consists load related arguments required for measurer to work
correctly, typically minimal and maximal load to offer.
Also, target loss ratio (if not hardcoded) is a required argument.

Third group consists of time related arguments.
Typically the duration for the first trial measurement, duration increment
per subsequent trial measurement and total time for search.
Some PLRsearch implementation may use estimation accuracy parameters
as an exit condition instead of total search time.

The returned quantities should describe the final (or best) estimate
of critical load. Implementers can chose any description that suits their users,
typically it is average and standard deviation, or lower and upper boundary.

Main ideas
----------

The search tries to perform measurements at offered load
close to the critical load, because measurement results at offered loads
far from the critical load give less information on precise location
of the critical load. As virtually every trial measurement result
alters the estimate of the critical load, offered loads vary
as they approach the critical load.

PLRsearch uses `Bayesian inference`_, computed using numerical integration,
which takes long time to get reliable enough results.
Therefore it takes some time before the most recent measurement result
starts affecting subsequent offered loads and critical rate estimates.

During the search, PLRsearch spawns few processes that perform numerical
computations, the main process is calling measurer to perform
trial measurements, without any significant delays between them.
The durations of the trial measurements are increasing linearly,
as higher number of trial measurement results take longer to process.

Probabilistic notions
`````````````````````

Before internals of PLRsearch are described, we need to define notions
valid for situations when loss ratio is not entirely determined
by offered load.

Some of the notions already incorporate assumptions
the PLRsearch algorithm applies.

Loss count only
---------------

It is assumed that the traffic generator detects duplicate packets
on receive, and reports this as an error.

No latency (or other information) is taken into account.

Independent trials
------------------

PLRsearch still assumes the system under test can be subjected
to trial measurements. The loss count is no longer determined precisely,
but it is assumed that for every system under test, its configuration,
traffic type and trial duration, there is a probability distribution
over possible loss counts.

This implies trial measurements are probabilistic, but the distribution
is independent of possible previous trial measurements.

Independence from previous measurements is not guaranteed
in the real world. The previous measurements may improve performance
(via long-term warmup effects), or decrease performance (due to
long-term resource leaks).

Trial durations
---------------

`RFC 2544`_ motivates the usage of at least 60 second duration
by the idea of the system under test slowly running out of resources
(such as memory buffers).

Practical results when measuring NFV software devices show
that relative change of trial duration has negligible effects on
average loss ratio, compared to relative change in offered load.

While the standard deviation of loss ratio usually shows some effects
of trial duration, they are hard to model; so further assumtions in PLRsearch
will make it insensitive to trial duration.

Loss ratio function
-------------------

From the previous assumtions, it follow that for a given system under test,
configuration and traffic type, the average loss ratio depends deterministically
of offered load (and does not depend on trial duration).
The mapping from offered load to average loss ratio is called
loss ratio function.

Target loss ratio
-----------------

Loss ratio function could be used to generalize throughput
as the biggest offered load which still leads to zero average loss ratio.
Unfortunately, most realistic loss ratio functions always predict
non-zero (even if negligible) average loss ratio.

On the other hand, users do not really require
the average loss ratio to be an exact zero.
Most users are satisfied when the average loss ratio is small enough.

One of PLRsearch inputs is called target loss ratio.
It is the loss ratio users would accept as negligible.

Critical load
-------------

Critical load (sometimes called critical rate) is the offered load
which leads to average loss ratio to become exactly equal
to the target loss ratio.

In principle, there could be such loss ratio functions
which allow more than one offered load to achieve target loss ratio.
To avoid that, PLRsearch assumes only increasing loss ratio functions
are possible.

Similarly, some loss ratio functions may never return the target loss ratio.
PLRsearch assumes loss ratio function is continuous, that
the average loss ratio approaches zero as offered load approaches zero, and
that the average loss ratio approaches one as offered load approaches infinity.

Under these assumptions, each loss ratio function has unique critical load.
PLRsearch attempts to locate the critical load.

Load regions
------------

Critical region is the interval of offered load close to critical load,
where single measurement is not likely to distinguish whether
the critical load is higher or lower than the current offered load.

In typical case of small target loss ratio, rates below critical region
form "zero loss region", and rates above form "high loss region".

Finite models
-------------

Of course, finite amount of trial measurements, each of finite duration
does not give enough information to pinpoint the critical load exactly.
Therefore the output of PLRsearch is just an estimate with some precision.

Aside of the usual substitution of infinitely precise real numbers
by finitely precise floating point numbers, there are two other instances
within PLRsearch where an objects of high information are replaced by
objects of low information.

One is the probability distribution of loss count, which is replaced
by average loss ratio. The other is the loss ratio function,
which is replaced by a few parameters, to be described later.

PLRsearch building blocks
`````````````````````````

Here we define notions used by PLRsearch which are not applicable
to other search methods, nor probabilistic systems under test, in general.

Bayesian inference
------------------

Having reduced the model space significantly, the task of estimating
the critical load becomes simple enough so that `Bayesian inference`_
can be used (instead of neural networks,
or other Artifical Intelligence methods).

In this case, the few parameters describing the loss ration function
become the model space. Given a prior over the model space,
and trial duration results, a posterior distribution can be computed,
together with quantities describing the critical load estimate.

Iterative search
----------------

The idea PLRsearch is to iterate trial measurements,
using `Bayesian inference`_ to compute both the current estimate
of the critical load and the next offered load to measure at.

The required numerical computations are done
in parallel with the trial measurements.

This means the result of measurement "n" comes as an (additional) input
to the computation running in parallel with measurement "n+1",
and the outputs of the computation are used for determining the offered load
for measurement "n+2".

Other schemes are possible, aimed to increase the number of measurements
(by decreasing their duration), which would have even higher number
of measurements run before a result of a measurement affects offered load.

Poisson distribution
--------------------

For given offered load, number of packets lost during trial measurement
is assumed to come from `Poisson distribution`_,
and the (unknown) Poisson parameter is expressed as average loss ratio.

Side note: `Binomial distribution`_ is a better fit compared to Poisson
distribution (acknowledging that the number of packets lost cannot be
higher than the number of packets offered), but the difference tends to
be relevant only in high loss region. Using Poisson
distribution lowers the impact of measurements in high loss region,
thus helping the algorithm to focus on critical region better.

Fitting functions
-----------------

There are great many increasing functions (as candidates
for the loss ratio function).

To make the space of possible functions more tractable, some other
simplifying assumptions are needed. As the algorithm will be examining
(also) loads very close to the critical load, linear approximation to the
loss rate function around the critical load is important.
But as the search algorithm needs to evaluate the function also far
away from the critical region, the approximate function has to be
reasonably behaved for every positive offered load,
specifically it cannot predict non-positive packet loss ratio.

Within this document, "fitting function" is the name for such a reasonably
behaved function, which approximates the loss ratio function
well in the critical region.

Measurement impact
------------------

Results from trials far from the critical region are likely to affect
the critical rate estimate negatively, as the fitting function does not
need to be a good approximation there. This is true mainly for high loss region,
as in zero loss region even badly behaved fitting function predicts
loss count to be "almost zero", so seeing a measurement confirming
the loss has been zero indeed has small impact.

Discarding some results, or "suppressing" their impact with ad-hoc methods
(other than using Poisson distribution instead of binomial) is not used,
as such methods tend to make the overall search unstable. We rely on most of
measurements being done (eventually) within the critical region, and
overweighting far-off measurements (eventually) for well-behaved fitting
functions.

Speaking about new trials, each next trial will be done at offered load
equal to the current average of the critical load.
Alternative methods for selecting offered load might be used,
in an attempt to speed up convergence. For example by employing
the aforementioned unstable ad-hoc methods.

Fitting function coefficients distribution
------------------------------------------

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

Exit condition for the search is either the standard deviation
of the critical load estimate becoming small enough (or similar),
or overal search time becoming long enough.

The algorithm should report both average and standard deviation
for its critical load posterior. If the reported averages follow a trend
(without reaching equilibrium), average and standard deviation
should refer to the equilibrium estimates based on the trend,
not to immediate posterior values.

Integration
-----------

The posterior distributions for fitting function parameters will not be
integrable in general.

The search algorithm utilises the fact that trial measurement takes some
time, so this time can be used for numeric integration (using suitable
method, such as Monte Carlo) to achieve sufficient precision.

Optimizations
-------------

After enough trials, the posterior distribution will be concentrated in
a narrow area of the parameter space. The integration method should take
advantage of that.

Even in the concentrated area, the likelihood can be quite small, so the
integration algorithm should avoid underflow errors by some means,
for example by tracking the logarithm of the likelihood.

FD.io CSIT Implementation Specifics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The search receives min_rate and max_rate values, to avoid measurements
at offered loads not supporeted by the traffic generator.

The implemented tests cases use bidirectional traffic.
The algorithm stores each rate as bidirectional rate (internally,
the algorithm is agnostic to flows and directions,
it only cares about overall counts of packets sent and packets lost),
but debug output from traffic generator lists unidirectional values.

Measurement delay
`````````````````

In a sample implemenation in FD.io CSIT project, there is roughly 0.5
second delay between trials due to restrictons imposed by packet traffic
generator in use (T-Rex).

As measurements results come in, posterior distribution computation takes
more time (per sample), although there is a considerable constant part
(mostly for inverting the fitting functions).

Also, the integrator needs a fair amount of samples to reach the region
the posterior distribution is concentrated at.

And of course, speed of the integrator depends on computing power
of the CPU the algorithm is able to use.

All those timing related effects are addressed by arithmetically increasing
trial durations with configurable coefficients
(currently 5.1 seconds for the first trial,
each subsequent trial being 0.1 second longer).

Rounding errors and underflows
``````````````````````````````

In order to avoid them, the current implementation tracks natural logarithm
(instead of the original quantity) for any quantity which is never negative.
Logarithm of zero is minus infinity (not supported by Python),
so special value "None" is used instead.
Specific functions for frequent operations
(such as "logarithm of sum of exponentials")
are defined to handle None correctly.

Fitting functions
`````````````````

Current implementation uses two fitting functions.
In general, their estimates for critical rate differ,
which adds a simple source of systematic error,
on top of randomness error reported by integrator.
Otherwise the reported stdev of critical rate estimate
is unrealistically low.

Both functions are not only increasing, but also convex
(meaning the rate of increase is also increasing).

As `primitive function`_ to any positive function is an increasing function,
and primitive function to any increasing function is convex function;
both fitting functions were constructed as double primitive function
to a positive function (even though the intermediate increasing function
is easier to describe).

As not any function is integrable, some more realistic functions
(especially with respect to behavior at very small offered loads)
are not easily available.

Both fitting functions have a "central point" and a "spread",
varied by simply shifting and scaling (in x-axis, the offered load direction)
the function to be doubly integrated.
Scaling in y-axis (the loss rate direction) is fixed by the requirement of
transfer rate staying nearly constant in very high offered loads.

In both fitting functions (as they are a double primitive function
to a symmetric function), the "central point" turns out
to be equal to the aforementioned limiting transfer rate,
so the fitting function parameter is named "mrr",
the same quantity our Maximum Receive Rate tests are designed to measure.

Both fitting functions return logarithm of loss rate,
to avoid rounding errors and underflows.
Parameters and offered load are not given as logarithms,
as they are not expected to be extreme,
and the formulas are simpler that way.

Both fitting functions have several mathematically equivalent formulas,
each can lead to an overflow or underflow in different places.
Overflows can be eliminated by using different exact formulas
for different argument ranges.
Underflows can be avoided by using approximate formulas
in affected argument ranges, such ranges have their own formulas to compute.
At the end, both fitting function implementations
contain multiple "if" branches, discontinuities are a possibility
at range boundaries.

Offered load for next trial measurement is the average
of critical rate estimate. During each measurement, two estimates are computed,
even though only one (in alternating order) is used for next offered load.

Stretch function
----------------

The original function (before applying logarithm) is primitive function
to `logistic function`_.
The name "stretch" is used for related a function
in context of neural networks with sigmoid activation function.

Erf function
------------

The original function is double primitive function to `Gaussian function`_.
The name "erf" comes from error function, the first primitive to Gaussian.

Prior distributions
```````````````````

The numeric integrator expects all the parameters to be distributed
(independently and) uniformly on an interval (-1, 1).

As both "mrr" and "spread" parameters are positive and not not dimensionless,
a transformation is needed. Dimentionality is inherited from max_rate value.

The "mrr" parameter follows a `Lomax distribution`_
with alpha equal to one, but shifted so that mrr is always greater than 1
packet per second.

The "stretch" parameter is generated simply as the "mrr" value
raised to a random power between zero and one;
thus it follows a `reciprocal distribution`_.

Integrator
``````````

After few measurements, the posterior distribution of fitting function
arguments gets quite concentrated into a small area.
The integrator is using `Monte Carlo`_ with `importance sampling`_
where the biased distribution is `bivariate Gaussian`_ distribution,
with deliberately larger variance.
If the generated sample falls outside (-1, 1) interval,
another sample is generated.

The the center and the covariance matrix for the biased distribution
is based on the first and second moments of samples seen so far
(within the computation), with the following additional features
designed to avoid hyper-focused distributions.

Each computation starts with the biased distribution inherited
from the previous computation (zero point and unit covariance matrix
is used in the first computation), but the overal weight of the data
is set to the weight of the first sample of the computation.
Also, the center is set to the first sample point.
When additional samples come, their weight (including the importance correction)
is compared to the weight of data seen so far (within the computation).
If the new sample is more than one e-fold more impactful, both weight values
(for data so far and for the new sample) are set to (geometric) average
if the two weights. Finally, the actual sample generator uses covariance matrix
scaled up by a configurable factor (8.0 by default).

This combination showed the best behavior, as the integrator usually follows
two phases. First phase (where inherited biased distribution
or single big sasmples are dominating) is mainly important
for locating the new area the posterior distribution is concentrated at.
The second phase (dominated by whole sample population)
is actually relevant for the critical rate estimation.

Caveats
```````

As high loss count measurements add many bits of information,
they need a large amount of small loss count measurements to balance them,
making the algorithm converge quite slowly. Typically, this happens
when few initial measurements suggest spread way bigger then later measurements.

Some systems evidently do not follow the assumption of repeated measurements
having the same average loss rate (when offered load is the same).
The idea of estimating the trend is not implemented at all,
as the observed trends have varied characteristics.

Probably, using a more realistic fitting functions
will give better estimates than trend analysis.

Graphical examples
``````````````````

FIXME: Those are 1901 graphs, not reflecting later improvements.

The following pictures show the upper and lower bound (one sigma)
on estimated critical rate, as computed by PLRsearch, after each trial measurement
within the 30 minute duration of a test run.

Both graphs are focusing on later estimates. Estimates computed from
few initial measurements are wildly off the y-axis range shown.

L2 patch
--------

This test case shows quite narrow critical region. Both fitting functions
give similar estimates, the graph shows the randomness of measurements,
and a trend. Both fitting functions seem to be somewhat overestimating
the critical rate. The final estimated interval is too narrow,
a longer run would report estimates somewhat bellow the current lower bound.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{PLR_patch}
                \label{fig:PLR_patch}
        \end{figure}

.. only:: html

    .. figure:: PLR_patch.svg
        :alt: PLR_patch
        :align: center

Vhost
-----

This test case shows quite broad critical region. Fitting functions give
fairly differing estimates. One overestimates, the other underestimates.
The graph mostly shows later measurements slowly bringing the estimates
towards each other. The final estimated interval is too broad,
a longer run would return a smaller interval within the current one.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{PLR_vhost}
                \label{fig:PLR_vhost}
        \end{figure}

.. only:: html

    .. figure:: PLR_vhost.svg
        :alt: PLR_vhost
        :align: center

.. _plrsearch draft: https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch-00
.. _RFC 2544: https://tools.ietf.org/html/rfc2544
.. _Bayesian inference: https://en.wikipedia.org/wiki/Bayesian_statistics
.. _Poisson distribution: https://en.wikipedia.org/wiki/Poisson_distribution
.. _binomial distribution: https://en.wikipedia.org/wiki/Binomial_distribution
.. _primitive function: https://en.wikipedia.org/wiki/Antiderivative
.. _logistic function: https://en.wikipedia.org/wiki/Logistic_function
.. _Gaussian function: https://en.wikipedia.org/wiki/Gaussian_function
.. _Lomax distribution: https://en.wikipedia.org/wiki/Lomax_distribution
.. _reciprocal distribution: https://en.wikipedia.org/wiki/Reciprocal_distribution
.. _Monte Carlo: https://en.wikipedia.org/wiki/Monte_Carlo_integration
.. _importance sampling: https://en.wikipedia.org/wiki/Importance_sampling
.. _bivariate Gaussian: https://en.wikipedia.org/wiki/Multivariate_normal_distribution
.. _real coordinate space: https://en.wikipedia.org/wiki/Real_coordinate_space
.. _law of large numbers: https://en.wikipedia.org/wiki/Law_of_large_numbers#Borel's_law_of_large_numbers
.. _Binary search: https://en.wikipedia.org/wiki/Binary_search_algorithm

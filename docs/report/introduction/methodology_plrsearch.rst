.. _plrsearch_algorithm:

PLRsearch
^^^^^^^^^

Abstract algorithm
~~~~~~~~~~~~~~~~~~

.. TODO: Refer to packet forwarding terminology, such as "offered load" and
   "loss ratio".

Eventually, a better description of the abstract search algorithm
will appear at this IETF standard: `plrsearch draft`_.

Motivation
----------

Network providers are interested in throughput a device can sustain.

`RFC 2544`_ assumes loss ratio is given by a deterministic function of
offered load. But NFV software devices are not deterministic (enough).
This leads for deterministic algorithms (such as MLRsearch with single
trial) to return results, which when repeated show relatively high
standard deviation, thus making it harder to tell what "the throughput"
actually is.

We need another algorithm, which takes this indeterminism into account.

Model
-----

Each algorithm searches for an answer to a precisely formulated
question. When the question involves indeterministic systems, it has to
specify probabilities (or prior distributions) which are tied to a
specific probabilistic model. Different models will have different
number (and meaning) of parameters. Complicated (but more realistic)
models have many parameters, and the math involved can be very
convoluted. It is better to start with simpler probabilistic model, and
only change it when the output of the simpler algorithm is not stable or
useful enough.

This document is focused on algorithms related to packet loss count
only. No latency (or other information) is taken into account. For
simplicity, only one type of measurement is considered: dynamically
computed offered load, constant within trial measurement of
predetermined trial duration.

The main idea of the search apgorithm is to iterate trial measurements,
using `Bayesian inference`_ to compute both the current estimate
of "the throughput" and the next offered load to measure at.
The computations are done in parallel with the trial measurements.

The following algorithm makes an assumption that packet traffic
generator detects duplicate packets on receive detection, and reports
this as an error.

Poisson distribution
--------------------

For given offered load, number of packets lost during trial measurement
is assumed to come from `Poisson distribution`_,
each trial is assumed to be independent, and the (unknown) Poisson parameter
(average number of packets lost per second) is assumed to be
constant across trials.

When comparing different offered loads, the average loss per second is
assumed to increase, but the (deterministic) function from offered load
into average loss rate is otherwise unknown. This is called "loss function".

Given a target loss ratio (configurable), there is an unknown offered load
when the average is exactly that. We call that the "critical load".
If critical load seems higher than maximum offerable load, we should use
the maximum offerable load to make search output more conservative.

Side note: `Binomial distribution`_ is a better fit compared to Poisson
distribution (acknowledging that the number of packets lost cannot be
higher than the number of packets offered), but the difference tends to
be relevant in loads far above the critical region, so using Poisson
distribution helps the algorithm focus on critical region better.

Of course, there are great many increasing functions (as candidates
for loss function). The offered load has to be chosen for each trial,
and the computed posterior distribution of critical load
changes with each trial result.

To make the space of possible functions more tractable, some other
simplifying assumptions are needed. As the algorithm will be examining
(also) loads close to the critical load, linear approximation to the
loss function in the critical region is important.
But as the search algorithm needs to evaluate the function also far
away from the critical region, the approximate function has to be
well-behaved for every positive offered load, specifically it cannot predict
non-positive packet loss rate.

Within this document, "fitting function" is the name for such a well-behaved
function, which approximates the unknown loss function in the critical region.

Results from trials far from the critical region are likely to affect
the critical rate estimate negatively, as the fitting function does not
need to be a good approximation there. Discarding some results,
or "suppressing" their impact with ad-hoc methods (other than
using Poisson distribution instead of binomial) is not used, as such
methods tend to make the overall search unstable. We rely on most of
measurements being done (eventually) within the critical region, and
overweighting far-off measurements (eventually) for well-behaved fitting
functions.

Speaking about new trials, each next trial will be done at offered load
equal to the current average of the critical load.
Alternative methods for selecting offered load might be used,
in an attempt to speed up convergence, but such methods tend to be
scpecific for a particular system under tests.

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

Exit condition for the search is either critical load stdev
becoming small enough, or overal search time becoming long enough.

The algorithm should report both avg and stdev for critical load. If the
reported averages follow a trend (without reaching equilibrium), avg and
stdev should refer to the equilibrium estimates based on the trend, not
to immediate posterior values.

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
a narrow area of parameter space. The integration method should take
advantage of that.

Even in the concentrated area, the likelihood can be quite small, so the
integration algorithm should track the logarithm of the likelihood, and
also avoid underflow errors by other means.

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
-----------------

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
(currently 10.2 seconds for the first trial,
each subsequent trial being 0.2 second longer).

Rounding errors and underflows
------------------------------

In order to avoid them, the current implementation tracks natural logarithm
(instead of the original quantity) for any quantity which is never negative.
Logarithm of zero is minus infinity (not supported by Python),
so special value "None" is used instead.
Specific functions for frequent operations
(such as "logarithm of sum of exponentials")
are defined to handle None correctly.

Fitting functions
-----------------

Current implementation uses two fitting functions.
In general, their estimates for critical rate differ,
which adds a simple source of systematic error,
on top of randomness error reported by integrator.
Otherwise the reported stdev of critical rate estimate
is unrealistically low.

Both functions are not only increasing, but convex
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

Offered load for next trial measurement is the average of critical rate estimate.
During each measurement, two estimates are computed,
even though only one (in alternating order) is used for next offered load.

Stretch function
________________

The original function (before applying logarithm) is primitive function
to `logistic function`_.
The name "stretch" is used for related function
in context of neural networks with sigmoid activation function.

Erf function
____________

The original function is double primitive function to `Gaussian function`_.
The name "erf" comes from error function, the first primitive to Gaussian.

Prior distributions
-------------------

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
----------

After few measurements, the posterior distribution of fitting function
arguments gets quite concentrated into a small area.
The integrator is using `Monte Carlo`_ with `importance sampling`_
where the biased distribution is `bivariate Gaussian`_ distribution,
with deliberately larger variance.
If the generated sample falls outside (-1, 1) interval,
another sample is generated.

The center and the variance for the biased distribution has three sources.
First is a prior information. After enough samples are generated,
the biased distribution is constructed from a mixture of two sources.
Top 12 most weight samples, and all samples (the mix ratio is computed
from the relative weights of the two populations).
When integration (run along a particular measurement) is finished,
the mixture bias distribution is used as the prior information
for the next integration.

This combination showed the best behavior, as the integrator usually follows
two phases. First phase (where the top 12 samples are dominating)
is mainly important for locating the new area the posterior distribution
is concentrated at. The second phase (dominated by whole sample population)
is actually relevant for the critical rate estimation.

Caveats
-------

Current implementation does not constrict the critical rate
(as computed for every sample) to the min_rate, max_rate interval.

Earlier implementations were targeting loss rate (as opposed to loss ratio).
The chosen fitting functions do not even allow arbitrarily low loss ratios,
especially if the "spread" value is high enough (relative to "mrr" value).
Internal loss rate target is computed from given loss ratio
using the current trial offered load, which increases search instability
if measurements with surprisingly high loss count appear.

As high loss count measurements add many bits of information,
they need a large amount of small loss count measurements to balance them,
making the algorithm converge quite slowly.

Some systems evidently do not follow the assumption of repeated measurements
having the same average loss rate (when offered load is the same).
The idea of estimating the trend is not implemented at all,
as the observed trends have varied characteristics.

Probably, using a more realistic fitting functions
will give better estimates than trend analysis.

.. TODO: Add a 1901 result section when results are available.

.. TODO: Add a graph of time evolution when 1901 run is available.

.. _plrsearch draft: https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch-00
.. _RFC 2544: https://tools.ietf.org/html/rfc2544
.. _Bayesian inference: https://en.wikipedia.org/wiki/Bayesian_statistics
.. _Poisson distribution: https://en.wikipedia.org/wiki/Poisson_distribution
.. _Binomial distribution: https://en.wikipedia.org/wiki/Binomial_distribution
.. _primitive function: https://en.wikipedia.org/wiki/Antiderivative
.. _logistic function: https://en.wikipedia.org/wiki/Logistic_function
.. _Gaussian function: https://en.wikipedia.org/wiki/Gaussian_function
.. _Lomax distribution: https://en.wikipedia.org/wiki/Lomax_distribution
.. _reciprocal distribution: https://en.wikipedia.org/wiki/Reciprocal_distribution
.. _Monte Carlo: https://en.wikipedia.org/wiki/Monte_Carlo_integration
.. _importance sampling: https://en.wikipedia.org/wiki/Importance_sampling
.. _bivariate Gaussian: https://en.wikipedia.org/wiki/Multivariate_normal_distribution

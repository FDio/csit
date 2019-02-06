PLRsearch
^^^^^^^^^

TODO: Make this not an orphan document.

This is a draft of design document for new type of test.

Abstract algorithm
~~~~~~~~~~~~~~~~~~

Motivation
----------

Network providers are interested in throughput a device can sustain.

RFC 2544 assumes loss ratio is given by a deterministic function of
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
complicated. It is better to start with simpler probabilistic model, and
only change it when the output of the simpler algorithm is not stable or
useful enough.

TODO: Refer to packet forwarding terminology, such as "offered load" and
"loss ratio".

Note-1: The algorithm makes an assumption that packet traffic
generator detects duplicate packets on receive detection, and reports
this as an error.

This document is focused on algorithms related to packet loss count
only. No latency (or other information) is taken into account. For
simplicity, only one type of measurement is considered: dynamically
computed offered load, constant within trial measurement of
predetermined trial duration.

In current CSIT code, there is around 0.5 second delay between trials,
avoiding that is out of scope of this document.

Also, running longer trials (in some situations) could be more efficient,
but in order to perform trial at multiple offered loads withing critical region,
trial durations should be kept as short as possible.

Poisson distribution
--------------------

Wikipedia link: https://en.wikipedia.org/wiki/Poisson_distribution

For given offered load, number of packets lost during trial
is assumed to come from Poisson distribution,
each trial is assumed to be independent, and the (unknown) Poisson parameter
(average number of packets lost per second) is constant across trials.

When comparing different offered loads, the average loss per second is
assumed to increase, but the (deterministic) function from offered load
into average loss rate is otherwise unknown.

Given a target loss ratio (configurable), there is an unknown offered load
when the average is exactly that. We call that the "critical load".
If critical load seems higher than maximum offerable load, we should use
the maximum offerable load to make search output more conservative.

Note-2: Binomial distribution is a better fit compared to Poisson
distribution (acknowledging that the number of packets lost cannot be
higher than the number of packets offered), but the difference tends to
be relevant in loads far above the critical region, so using Poisson
distribution helps the algorithm focus on critical region better.

Of course, there are great many increasing functions. The offered load
has to be chosen for each trial, and the computed posterior distribution
of critical load changes with each trial result.

To make the space of possible functions more tractable, some other
simplifying assumptions are needed. As the algorithm will be examining
(also) loads close to the critical load, linear approximation to the
function (TODO: name this function) in the critical region is important.
But as the search algorithm needs to evaluate the function also far
away from the critical region, the approximate function has to be well-
behaved for every positive offered load, specifically it cannot predict
non-positive packet loss rate.

Within this document, "fitting function" is the name for such well-behaved
function which approximates the unknown function in the critical region.

Results from trials far from the critical region are likely to affect
the critical rate estimate negatively, as the fitting function does not
need to be a good approximation there. Discarding some results,
or "suppressing" their impact with ad-hoc methods (other than
using Poisson distribution instead of binomial) is not used, as such
methods tend to make the overall search unstable. We rely on most of
measurements being done (eventually) within the critical region, and
overweighting far-off measurements (eventually) for well-behaved fitting
functions.

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

TODO: Move the following sentence into more appropriate place.

Speaking about new trials, each next trial will be done at offered load
equal to the current average of the critical load.

Exit condition is either critical load stdev becoming small enough, or
overal search time becoming long enough.

The algorithm should report both avg and stdev for critical load. If the
reported averages follow a trend (without reaching equilibrium), avg and
stdev should refer to the equilibrium estimates based on the trend, not
to immediate posterior values.

TODO: Explicitly mention the iterative character of the search.

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

Rounding errors and underflows
------------------------------

In order to avoid them, the current implementation tracks natural logarithm
(instead of original quantity) for any quantity which is never negative.
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

Both functions are not only increasing, but convex
(meaning the rate of increase is also increasing).

As primitive function to any positive function is an increasing function,
and primitive function to any increasing function is convex function,
both fitting functionc were constructed as double primitive function
to a positive function.

As not any function is integrable, some more realistic functions
(especially with respect to behavior at very small offered loads)
are not easily available.

Both fitting function have a "central point" and a "spread",
varied by simply shifting and scaling (in x-axis direction)
the function to be doubly integrated.
Scaling in y-axis direction is fixed by the requirement of
transfer rate staying nearly constant in very high offered loads.

In both fitting functions, the "central point" turns out
to be equal to the aforementioned limiting transfer rate,
so the fitting function parameter is named "mrr",
the same quantity our Maximum Receive Rate tests are measuring.

Both fitting function return logarithm of loss rate,
to avoid rounding errors and underflows.
Parameters and offered load are not logarithm,
as they are not expected to be extreme,
and the formulas are simpler that way.

Stretch function
________________

The original function (before applying logarithm) is primitive function
to logistic function https://en.wikipedia.org/wiki/Logistic_function
(The name "stretch" is used for this function
in context of neural networks with sigmoud activation function.)


TODO: Describe sigmoid-based and erf-based functions.



In a sample implemenation in FD.io CSIT project, there is around 0.5
second delay between trials due to restrictons imposed by packet traffic
generator in use (T-Rex), avoiding that delay is out of scope of this
document.

TODO: Describe how the current integration algorithm finds the
concentrated area.

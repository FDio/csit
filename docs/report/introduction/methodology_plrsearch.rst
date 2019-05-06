.. _`PLRsearch algorithm`:

PLRsearch
^^^^^^^^^

Motivation for PLRsearch
~~~~~~~~~~~~~~~~~~~~~~~~

Network providers are interested in throughput a system can sustain.

`RFC 2544`_ assumes loss ratio is given by a deterministic function of
offered load. But NFV software systems are not deterministic enough.
This makes deterministic algorithms (such as binary search per RFC 2544
and MLRsearch with single trial) to return results,
which when repeated show relatively high standard deviation,
thus making it harder to tell what "the throughput" actually is.

We need another algorithm, which takes this indeterminism into account.

Terms
~~~~~

Average loss ratio
``````````````````

Average loss ratio is simply the expected value of loss ratio
for a given trial measurement result distribution.

Duration independent system
```````````````````````````

Duration independent system is a trial order independent system,
whose trial measurement result distribution is proven (or just assumed)
to display practical independence from trial duration.

The only requirement is for average loss ratio to be independent
of trial duration.

PLRsearch assumes the system under test is duration independent,
at least for trial durations typically chosen for trial measurements
initiated by PLRsearch.

Load regions
````````````

For a duration independent system, trial measurement result distribution
depends only on offered load.

It is convenient to name some areas of offered load space
by possible trial results.

Zero loss region
----------------

A particular offered load value is said to belong to zero loss region,
if the probability of seeing non-zero loss trial measurement result
is exactly zero, or at least practically indistinguishable from zero.

Guaranteed loss region
----------------------

A particular offered load value is said to belong to guaranteed loss region,
if the probability of seeing zero loss trial measurement result
(for non-negligible count of packets offered)
is exactly zero, or at least practically indistinguishable from zero.

Non-deterministic region
------------------------

A particular offered load value is said to belong to non-deterministic region,
if the probability of seeing zero loss trial measurement result
(for non-negligible count of packets offered)
practically distinguishable from both zero and one.

Througphput
```````````

Throughput is the highest offered load provably causing zero packet loss
for trial measurements of duration at least 60 seconds.

For duration independent systems with normal region ordering,
the throughput is the highest value within the zero loss region.

Probabilistic search
````````````````````

Any algorithm which performs probabilistic computations based on
observed results of trial measurements, and which does not assume
that non-deterministic region is practically absent
is called probabilistic search.

While probabilistic search for estimating throughput is possible,
it would need a careful model for boundary between zero loss region
and non-deterministic region, and it would need a lot of measurements
of almost surely zero loss to reach good precision.

Loss ratio function
```````````````````

For any duration independent system, the average loss ratio depends
only on offered load (for a particular test setup).

Loss ratio function is the name used for the function mapping
offered load to average loss ratio.

This function is initially unknown.

Target loss ratio
`````````````````

Input parameter of PLRsearch.
The average loss ratio the output of PLRsearch aims to achieve.

Critical load
`````````````

A particular value for offered load, which would lead to
average loss ratio exactly matching target loss ratio.

Critical load estimate
``````````````````````

Any quantitative description of the possible
critical load PLRsearch is able to give
after observing finite amount of trial measurements.

Fitting function
````````````````

Any function PLRsearch uses internally instead of
the unknown loss ratio function. Typically chosen from small set
of formulas (shapes) with few parameters to tweak.

Shape of fitting function
`````````````````````````

Any formula with few undetermined parameters.

Parameter space
```````````````

A subset of `real coordinate space`_. A point of parameter
space is a vector of real numbers. Fitting function is defined by shape
(a formula with parameters) and point of its
parameter space (specifying values for the parameters).

Abstract algorithm
~~~~~~~~~~~~~~~~~~

High level description
``````````````````````

Programming interface view
--------------------------

PLRsearch accepts some input arguments, then iteratively performs
trial measurements at varying offered loads (and durations),
and returns some estimates of critical load.

PLRsearch input arguments form three groups.
First group has a single argument: measurer. This is a callback function,
accepting offered load and duration, and returning the measured loss count.

Second group consists of load related arguments required for measurer to work
correctly, typically minimal and maximal load to offer.
Also, target loss ratio (if not hardcoded) is a required argument of this group.

Third group consists of time related arguments.
Typically the duration for the first trial measurement, duration increment
per subsequent trial measurement and total time for search.
Some PLRsearch implementation may use estimation accuracy parameters
as an exit condition instead of total search time.

The returned quantities should describe the final (or best) estimate
of critical load. Implementers can chose any description that suits their users,
typically it is average and standard deviation, or lower and upper boundary.

Main ideas
``````````

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
computations, the main process is calling the measurer to perform
trial measurements, without any significant delays between them.
The durations of the trial measurements are increasing linearly,
as higher number of trial measurement results take longer to process.

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

Speaking about new trials, each next trial will be done in general
at offered load equal to the current average of the critical load.
But see below for current workarounds.

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

Stretch function
----------------

The original function (before applying logarithm) is primitive function
to `logistic function`_.
The name "stretch" is used for related a function
in context of neural networks with sigmoid activation function.

Formula for stretch function: loss rate (r) computed from offered load (b),
mrr parameter (m) and spread parameter (a):

r = a (Log(E^(b/a) + E^(m/a)) - Log(1 + E^(m/a)))

Erf function
------------

The original function is double primitive function to `Gaussian function`_.
The name "erf" comes from error function, the first primitive to Gaussian.

Formula for erf function: loss rate (r) computed from offered load (b),
mrr parameter (m) and spread parameter (a):

r = (b + (a (E^(-((b - m)^2/a^2)) - E^(-(m^2/a^2))))/Sqrt[Pi] + (b - m) Erf[(b - m)/a] - m Erf[m/a])/2

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
of the two weights. Finally, the actual sample generator uses covariance matrix
scaled up by a configurable factor (8.0 by default).

This combination showed the best behavior, as the integrator usually follows
two phases. First phase (where inherited biased distribution
or single big samples are dominating) is mainly important
for locating the new area the posterior distribution is concentrated at.
The second phase (dominated by whole sample population)
is actually relevant for the critical rate estimation.

Offered load selection
``````````````````````

First two measurements are hardcoded to happen at the middle of rate interval
and at max_rate. Next two measurements follow MRR-like logic,
offered load is decreased so that it would reach target loss ratio
if offered load decrease lead to equal decrease of loss rate.

The rest of measurements alternate between erf and stretch estimate average.
There is one workaround implemented, aimed at reducing the number of consequent
zero loss measurements (per fitting function). The workaround first stores
every measurement result which loss ratio was the targed loss ratio or higher.
Sorted list (called lossy loads) of such results is maintained.

When a sequence of one or more zero loss measurement results is encountered,
a smallest of lossy loads is drained from the list.
If the estimate average is smaller than the drained value,
a weighted average of this estimate and the drained value is used
as the next offered load. The weight of the estimate decreases exponentially
with the length of consecutive zero loss results.

This behavior helps the algorithm with convergence speed,
as it does not need so many zero loss result to get near critical region.
Using the smallest (not srained yet) of lossy loads makes it sure
the new offered load is unlikely to result in big loss region.
Draining even if the estimate is large enough helps to discard
early measurements when loss hapened at too low offered load.
Current implementation adds 4 copies of lossy loads and drains 3 of them,
which leads to fairly stable behavior even for somewhat inconsistent SUTs.

Caveats
```````

As high loss count measurements add many bits of information,
they need a large amount of small loss count measurements to balance them,
making the algorithm converge quite slowly. Typically, this happens
when few initial measurements suggest spread way bigger then later measurements.
The workaround in offered load selection helps,
but more intelligent workarounds could get faster convergence still.

Some systems evidently do not follow the assumption of repeated measurements
having the same average loss rate (when offered load is the same).
The idea of estimating the trend is not implemented at all,
as the observed trends have varied characteristics.

Probably, using a more realistic fitting functions
will give better estimates than trend analysis.

Graphical examples
``````````````````

FIXME: Those are 1901 graphs, not reflecting later improvements.
TODO: Use real results from 1904 testing.

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

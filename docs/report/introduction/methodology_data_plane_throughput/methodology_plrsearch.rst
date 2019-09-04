.. _plrsearch:

PLRsearch
^^^^^^^^^

Motivation for PLRsearch
~~~~~~~~~~~~~~~~~~~~~~~~

Network providers are interested in throughput a system can sustain.

`RFC 2544`_ assumes loss ratio is given by a deterministic function of
offered load. But NFV software systems are not deterministic enough.
This makes deterministic algorithms (such as `binary search`_ per RFC 2544
and MLRsearch with single trial) to return results,
which when repeated show relatively high standard deviation,
thus making it harder to tell what "the throughput" actually is.

We need another algorithm, which takes this indeterminism into account.

Generic Algorithm
~~~~~~~~~~~~~~~~~

Detailed description of the PLRsearch algorithm is included in the IETF
draft `draft-vpolak-bmwg-plrsearch-02`_ that is in the process
of being standardized in the IETF Benchmarking Methodology Working Group (BMWG).

Terms
-----

The rest of this page assumes the reader is familiar with the following terms
defined in the IETF draft:

+ Trial Order Independent System
+ Duration Independent System
+ Target Loss Ratio
+ Critical Load
+ Offered Load regions

  + Zero Loss Region
  + Non-Deterministic Region
  + Guaranteed Loss Region

+ Fitting Function

  + Stretch Function
  + Erf Function

+ Bayesian Inference

  + Prior distribution
  + Posterior Distribution

+ Numeric Integration

  + Monte Carlo
  + Importance Sampling

FD.io CSIT Implementation Specifics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The search receives min_rate and max_rate values, to avoid measurements
at offered loads not supporeted by the traffic generator.

The implemented tests cases use bidirectional traffic.
The algorithm stores each rate as bidirectional rate (internally,
the algorithm is agnostic to flows and directions,
it only cares about aggregate counts of packets sent and packets lost),
but debug output from traffic generator lists unidirectional values.

Measurement Delay
`````````````````

In a sample implemenation in FD.io CSIT project, there is roughly 0.5
second delay between trials due to restrictons imposed by packet traffic
generator in use (T-Rex).

As measurements results come in, posterior distribution computation takes
more time (per sample), although there is a considerable constant part
(mostly for inverting the fitting functions).

Also, the integrator needs a fair amount of samples to reach the region
the posterior distribution is concentrated at.

And of course, the speed of the integrator depends on computing power
of the CPU the algorithm is able to use.

All those timing related effects are addressed by arithmetically increasing
trial durations with configurable coefficients
(currently 5.1 seconds for the first trial,
each subsequent trial being 0.1 second longer).

Rounding Errors and Underflows
``````````````````````````````

In order to avoid them, the current implementation tracks natural logarithm
(instead of the original quantity) for any quantity which is never negative.
Logarithm of zero is minus infinity (not supported by Python),
so special value "None" is used instead.
Specific functions for frequent operations (such as "logarithm
of sum of exponentials") are defined to handle None correctly.

Fitting Functions
`````````````````

Current implementation uses two fitting functions.
In general, their estimates for critical rate differ,
which adds a simple source of systematic error,
on top of randomness error reported by integrator.
Otherwise the reported stdev of critical rate estimate
is unrealistically low.

Both functions are not only increasing, but also convex
(meaning the rate of increase is also increasing).

Both fitting functions have several mathematically equivalent formulas,
each can lead to an overflow or underflow in different sub-terms.
Overflows can be eliminated by using different exact formulas
for different argument ranges.
Underflows can be avoided by using approximate formulas
in affected argument ranges, such ranges have their own formulas to compute.
At the end, both fitting function implementations
contain multiple "if" branches, discontinuities are a possibility
at range boundaries.

Prior Distributions
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

The center and the covariance matrix for the biased distribution
is based on the first and second moments of samples seen so far
(within the computation). The center is used directly,
covariance matrix is scaled up by a heurictic constant (8.0 by default).
The following additional features are applied
designed to avoid hyper-focused distributions.

Each computation starts with the biased distribution inherited
from the previous computation (zero point and unit covariance matrix
is used in the first computation), but the overal weight of the data
is set to the weight of the first sample of the computation.
Also, the center is set to the first sample point.
When additional samples come, their weight (including the importance correction)
is compared to sum of the weights of data seen so far (within the iteration).
If the new sample is more than one e-fold more impactful, both weight values
(for data so far and for the new sample) are set to (geometric) average
of the two weights.

This combination showed the best behavior, as the integrator usually follows
two phases. First phase (where inherited biased distribution
or single big sample are dominating) is mainly important
for locating the new area the posterior distribution is concentrated at.
The second phase (dominated by whole sample population)
is actually relevant for the critical rate estimation.

Offered Load Selection
``````````````````````

First two measurements are hardcoded to happen at the middle of rate interval
and at max_rate. Next two measurements follow MRR-like logic,
offered load is decreased so that it would reach target loss ratio
if offered load decrease lead to equal decrease of loss rate.

The rest of measurements start directly in between
erf and stretch estimate average.
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
Using the smallest (not drained yet) of lossy loads makes it sure
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
having the same average loss rate (when the offered load is the same).
The idea of estimating the trend is not implemented at all,
as the observed trends have varied characteristics.

Probably, using a more realistic fitting functions
will give better estimates than trend analysis.

Bottom Line
~~~~~~~~~~~

The notion of Throughput is easy to grasp, but it is harder to measure
with any accuracy for non-deterministic systems.

Even though the notion of critical rate is harder to grasp than the notion
of throughput, it is easier to measure using probabilistic methods.

In testing, the difference between througput measurements and critical
rate measurements is usually small, see :ref:`soak vs ndr comparison`.

In pactice, rules of thumb such as "send at max 95% of purported throughput"
are common. The correct benchmarking analysis should ask "Which notion is
95% of throughput an approximation to?" before attempting to answer
"Is 95% of critical rate safe enough?".

Algorithmic Analysis
~~~~~~~~~~~~~~~~~~~~

Motivation
``````````

While the estimation computation is based on hard probability science;
the offered load selection part of PLRsearch logic is pure heuristics,
motivated by what would a human do based on measurement and computation results.

The quality of any heuristic is not affected by soundness of its motivation,
just by its ability to achieve the intended goals.
In case of offered load selection, the goal is to help the search to converge
to the long duration estimates sooner.

But even those long duration estimates could still be of poor quality.
Even though the estimate computation is Bayesian (so it is the best it could be
within the applied assumptions), it can still of poor quality when compared
to what a human would estimate.

One possible source of poor quality is the randomnes inherently present
in Monte Carlo numeric integration, but that can be supressed
by tweaking the time related input parameters.

The most likely source of poor quality then are the assumptions.
Most importantly, the number and the shape of fitting functions;
but also others, such as trial order independence and duration independence.

The result can have poor quality in basically two ways.
One way is related to location. Both upper and lower bounds
can be overestimates or underestimates, meaning the entire estimated interval
between lower bound and upper bound lays above or below (respectively)
of human-estimated interval.
The other way is related to the estimation interval width.
The interval can be too wide or too narrow, compared to human estimation.

An estimate from a particular fitting function can be classified
as an overestimate (or underestimate) just by looking at time evolution
(without human examining measurement results). Overestimates
decrease by time, underestimates increase by time (assuming
the system performance stays constant).

Quality of the width of the estimation interval needs human evaluation,
and is unrelated to both rate of narrowing (both good and bad estimate intervals
get narrower at approximately the same relative rate) and relatative width
(depends heavily on the system being tested).

Graphical Examples
``````````````````

The following pictures show the upper (red) and lower (blue) bound,
as well as average of Stretch (pink) and Erf (light green) estimate,
and offered load chosen (grey), as computed by PLRsearch,
after each trial measurement within the 30 minute duration of a test run.

Both graphs are focusing on later estimates. Estimates computed from
few initial measurements are wildly off the y-axis range shown.

The following analysis will rely on frequency of zero loss measurements
and magnitude of loss ratio if nonzero.

The offered load selection strategy used implies zero loss measurements
can be gleamed from the graph by looking at offered load points.
When the points move up farther from lower estimate, it means
the previous measurement had zero loss. After non-zero loss,
the offered load starts again right between (the previous values of)
the estimate curves.

The very big loss ratio results are visible as noticeable jumps
of both estimates downwards. Medium and small loss ratios are much harder
to distinguish just by looking at the estimate curves,
the analysis is based on raw loss ratio measurement results.

The following descriptions should explain why the graphs seem to signal
low quality estimate at first sight, but a more detailed look
reveals the quality is good (considering the measurement results).

L2 patch
--------

Both fitting functions give similar estimates, the graph shows
"stochasticity" of measurements (estimates increase and decrease
within small time regions), and an overall trend of decreasing estimates.

On the first look, the final interval looks fairly narrow,
especially compared to the region the estimates have travelled
during the search. But the look at the frequency of zero loss results shows
this is not a case of overestimation. Measurements at around the same
offered load have higher probability of zero loss earlier
(when performed farther from upper bound), but smaller probability later
(when performed closer to upper bound). That means it is the performance
of the system under test that decreases (slightly) over time.

With that in mind, the apparent narrowness of the interval
is not a sign of low quality, just a consequence of PLRsearch assuming
the performance stays constant.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/methodology_data_plane_throughput/}}
                \includegraphics[width=0.90\textwidth]{PLR_patch}
                \label{fig:PLR_patch}
        \end{figure}

.. only:: html

    .. figure:: PLR_patch.svg
        :alt: PLR_patch
        :align: center

Vhost
-----

This test case shows what looks like a quite broad estimation interval,
compared to other test cases with similarly looking zero loss frequencies.
Notable features are infrequent high-loss measurement results
causing big drops of estimates, and lack of long-term convergence.

Any convergence in medium-sized intervals (during zero loss results)
is reverted by the big loss results, as they happen quite far
from the critical load estimates, and the two fitting functions
extrapolate differently.

In other words, human only seeing estimates from one fitting function
would expect narrower end interval, but human seeing the measured loss ratios
agrees that the interval should be wider than that.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/methodology_data_plane_throughput/}}
                \includegraphics[width=0.90\textwidth]{PLR_vhost}
                \label{fig:PLR_vhost}
        \end{figure}

.. only:: html

    .. figure:: PLR_vhost.svg
        :alt: PLR_vhost
        :align: center

Summary
-------

The two graphs show the behavior of PLRsearch algorithm applied to soaking test
when some of PLRsearch assumptions do not hold:

+ L2 patch measurement results violate the assumption
  of performance not changing over time.
+ Vhost measurement results violate the assumption
  of Poisson distribution matching the loss counts.

The reported upper and lower bounds can have distance larger or smaller
than a first look by a human would expect, but a more closer look reveals
the quality is good, considering the circumstances.

The usefullness of the critical load estimate is of questionable value
when the assumptions are violated.

Some improvements can be made via more specific workarounds,
for example long term limit of L2 patch performance could be estmated
by some heuristic.

Other improvements can be achieved only by asking users
whether loss patterns matter. Is it better to have single digit losses
distributed fairly evenly over time (as Poisson distribution would suggest),
or is it better to have short periods of medium losses
mixed with long periods of zero losses (as happens in Vhost test)
with the same overall loss ratio?

.. _draft-vpolak-bmwg-plrsearch-02: https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch-02
.. _plrsearch draft: https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch-00
.. _RFC 2544: https://tools.ietf.org/html/rfc2544
.. _Lomax distribution: https://en.wikipedia.org/wiki/Lomax_distribution
.. _reciprocal distribution: https://en.wikipedia.org/wiki/Reciprocal_distribution
.. _Monte Carlo: https://en.wikipedia.org/wiki/Monte_Carlo_integration
.. _importance sampling: https://en.wikipedia.org/wiki/Importance_sampling
.. _bivariate Gaussian: https://en.wikipedia.org/wiki/Multivariate_normal_distribution
.. _binary search: https://en.wikipedia.org/wiki/Binary_search_algorithm

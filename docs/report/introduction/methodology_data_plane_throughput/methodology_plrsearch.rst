.. _PLRsearch:

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

Generic algorithm
~~~~~~~~~~~~~~~~~

Detailed description of the PLRsearch algorithm is included in the IETF
draft `draft-vpolak-bmwg-plrsearch-01`_ that is in the process
of being standardized in the IETF Benchmarking Methodology Working Group (BMWG).

Terms
-----

The rest of this page assumes the reader is familiar with the following terms
defined in the IETF draft:

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
Specific functions for frequent operations (such as "logarithm
of sum of exponentials") are defined to handle None correctly.

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

Both fitting functions have several mathematically equivalent formulas,
each can lead to an overflow or underflow in different places.
Overflows can be eliminated by using different exact formulas
for different argument ranges.
Underflows can be avoided by using approximate formulas
in affected argument ranges, such ranges have their own formulas to compute.
At the end, both fitting function implementations
contain multiple "if" branches, discontinuities are a possibility
at range boundaries.

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

The center and the covariance matrix for the biased distribution
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

The following pictures show the upper (red) and lower (blue) bound,
as well as average of stretch (pink) and erf (light green) estimate,
and offered load chosen (grey), as computed by PLRsearch,
after each trial measurement within the 2 hour duration of a test run.

Both graphs are focusing on later estimates. Estimates computed from
few initial measurements are wildly off the y-axis range shown.

L2 patch
--------

This test case shows quite narrow critical region, compared to the area
the estimates have travelled during the search. Sometimes
it is an example of high probability of the real critical load being outside
the reported estimates, but not in this case.

Both fitting functions give similar estimates,
the graph shows the randomness of measurements, and a trend.
Both fitting functions seem to be fairly precise in estimating
the current critical rate, but the performance of the system
decreases slightly over time.

In this case, the "real critical load" changes over time,
as evidenced by zero loss measurements (visible as grey box
appearing above the estimation lines).

The final estimated interval is fairly narrow, but corresponds
to the overall results measured so far.

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

This test case shows quite broad critical region. Fitting functions give
fairly differing estimates. Usually that signifies poor eastimation quality,
which is also true for this case.

Erf function overestimates (based on the estimates going steadily down),
stretch function is fairly precise (based on its estimate
not moving much with time).

The graph mostly shows later measurements slowly bringing the estimates
towards each other. The final estimated interval is too broad,
compared to precisions achieved in other test cases.
A longer run would return a smaller interval within the current one.

The broadness is caused by result composition, which consists of
mostly zero loss measurements, partialy of medium loss measurements,
and lack of small loss measurements the loss ratio target would imply.

With this result composition, it is expected that the convergence
of the two bounds is slow.

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

The two graphs show the behavior of PLRsearch algorithm when some of assumptions
used to derive the PLRsearch logic do not hold.

L2 patch violates assumption of performance not changing over time,
and Vhost violates assumption of Poisson distribution matching the loss counts.

The reported upper and lower bounds can have distance larger or smaller
than human intuition would suggest, but it can be argued
the quality of the estimate is still better than other methods would give.

.. _draft-vpolak-bmwg-plrsearch-01: https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch-01
.. _plrsearch draft: https://tools.ietf.org/html/draft-vpolak-bmwg-plrsearch-00
.. _RFC 2544: https://tools.ietf.org/html/rfc2544
.. _Lomax distribution: https://en.wikipedia.org/wiki/Lomax_distribution
.. _reciprocal distribution: https://en.wikipedia.org/wiki/Reciprocal_distribution
.. _Monte Carlo: https://en.wikipedia.org/wiki/Monte_Carlo_integration
.. _importance sampling: https://en.wikipedia.org/wiki/Importance_sampling
.. _bivariate Gaussian: https://en.wikipedia.org/wiki/Multivariate_normal_distribution
.. _binary search: https://en.wikipedia.org/wiki/Binary_search_algorithm

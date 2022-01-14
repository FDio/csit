Trend Analysis
^^^^^^^^^^^^^^

All measured performance trend data is treated as time-series data
that is modelled as a concatenation of groups,
within each group the samples come (independently) from
the same normal distribution (with some center and standard deviation).

Center of the normal distribution for the group (equal to population average)
is called a trend for the group.
All the analysis is based on finding the right partition into groups
and comparing their trends.

Trend Compliance
~~~~~~~~~~~~~~~~

.. _Trend_Compliance:

Trend compliance metrics are targeted to provide an indication of trend
changes, and hint at their reliability.

There is a difference between compliance metric names used in this document,
and column names used in :ref:`Dashboard` tables and Alerting emails.
In cases of low user confusion risk, column names are shortened,
e.g. Trend instead of Last Trend.
In cases of high user confusion risk, column names are prolonged,
e.g. Long-Term Change instead of Trend Change.
(This document refers to a generic "trend",
so the compliance metric name is prolonged to Last Trend to avoid confusion.)

The definition of Reference for Trend Change is perhaps surprising.
It was chosen to allow both positive difference on progression
(if within last week), but also negative difference on progression
(if performance was even better somewhere between 3 months and 1 week ago).

In the table below, "trend at time <t>", shorthand "trend[t]"
means "the group average of the group the sample at time <t> belongs to".
Here, time is usually given as "last" or last with an offset,
e.g. "last - 1week".
Also, "runs[t]" is a shorthand for "number of samples in the group
the sample at time <t> belongs to".

The definitions of compliance metrics:

+-------------------+-------------------+---------------------------------+-------------+-----------------------------------------------+
| Compliance Metric | Legend Short Name | Formula                         | Value       | Reference                                     |
+===================+===================+=================================+=============+===============================================+
| Last Trend        | Trend             | trend[last]                     |             |                                               |
+-------------------+-------------------+---------------------------------+-------------+-----------------------------------------------+
| Number of runs    | Runs              | runs[last]                      |             |                                               |
+-------------------+-------------------+---------------------------------+-------------+-----------------------------------------------+
| Trend Change      | Long-Term Change  | (Value - Reference) / Reference | trend[last] | max(trend[last - 3mths]..trend[last - 1week]) |
+-------------------+-------------------+---------------------------------+-------------+-----------------------------------------------+

Caveats
-------

Obviously, if the result history is too short, the true Trend[t] value
may not by available. We use the earliest Trend available instead.

The current implementaton does not track time of the samples,
it counts runs instead.
For "- 1week" we use "10 runs ago, 5 runs for topo-arch with 1 TB",
for "- 3mths" we use "180 days or 180 runs ago, whatever comes first".

Anomalies in graphs
~~~~~~~~~~~~~~~~~~~

In graphs, the start of the following group is marked
as a regression (red circle) or progression (green circle),
if the new trend is lower (or higher respectively)
then the previous group's.

Implementation details
~~~~~~~~~~~~~~~~~~~~~~

Partitioning into groups
------------------------

While sometimes the samples within a group are far from being
distributed normally, currently we do not have a better tractable model.

Here, "sample" should be the result of single trial measurement,
with group boundaries set only at test run granularity.
But in order to avoid detecting causes unrelated to VPP performance,
the current presentation takes average of all trials
within the run as the sample.
Effectively, this acts as a single trial with aggregate duration.

Performance graphs show the run average as a dot
(not all individual trial results).

The group boundaries are selected based on `Minimum Description Length`_.

Minimum Description Length
--------------------------

`Minimum Description Length`_ (MDL) is a particular formalization
of `Occam's razor`_ principle.

The general formulation mandates to evaluate a large set of models,
but for anomaly detection purposes, it is useful to consider
a smaller set of models, so that scoring and comparing them is easier.

For each candidate model, the data should be compressed losslessly,
which includes model definitions, encoded model parameters,
and the raw data encoded based on probabilities computed by the model.
The model resulting in shortest compressed message is the "the" correct model.

For our model set (groups of normally distributed samples),
we need to encode group length (which penalizes too many groups),
group average (more on that later), group stdev and then all the samples.

Luckily, the "all the samples" part turns out to be quite easy to compute.
If sample values are considered as coordinates in (multi-dimensional)
Euclidean space, fixing stdev means the point with allowed coordinates
lays on a sphere. Fixing average intersects the sphere with a (hyper)-plane,
and Gaussian probability density on the resulting sphere is constant.
So the only contribution is the "area" of the sphere, which only depends
on the number of samples and stdev.

A somehow ambiguous part is in choosing which encoding
is used for group size, average and stdev.
Different encodings cause different biases to large or small values.
In our implementation we have chosen probability density
corresponding to uniform distribution (from zero to maximal sample value)
for stdev and average of the first group,
but for averages of subsequent groups we have chosen a distribution
which disourages delimiting groups with averages close together.

Our implementation assumes that measurement precision is 1.0 pps.
Thus it is slightly wrong for trial durations other than 1.0 seconds.
Also, all the calculations assume 1.0 pps is totally negligible,
compared to stdev value.

The group selection algorithm currently has no parameters,
all the aforementioned encodings and handling of precision is hardcoded.
In principle, every group selection is examined, and the one encodable
with least amount of bits is selected.
As the bit amount for a selection is just sum of bits for every group,
finding the best selection takes number of comparisons
quadratically increasing with the size of data,
the overall time complexity being probably cubic.

The resulting group distribution looks good
if samples are distributed normally enough within a group.
But for obviously different distributions (for example `bimodal distribution`_)
the groups tend to focus on less relevant factors (such as "outlier" density).

.. _Minimum Description Length: https://en.wikipedia.org/wiki/Minimum_description_length
.. _Occam's razor: https://en.wikipedia.org/wiki/Occam%27s_razor
.. _bimodal distribution: https://en.wikipedia.org/wiki/Bimodal_distribution

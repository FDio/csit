.. _trend_analysis:

Trend Analysis
--------------

All measured performance trend data is treated as time-series data that
can be modelled as concatenation of groups, each group modelled
using normal distribution. While sometimes the samples within a group
are far from being distributed normally, currently we do not have a
better tractable model.

Here, "sample" should be the result of single trial measurement,
with group boundaries set only at test run granularity.
But in order to avoid detecting causes unrelated to VPP performance,
the default presentation (without /new/ in URL)
takes average of all trials within the run as the sample.
Effectively, this acts as a single trial with aggregate duration.

Performance graphs always show the run average (not all trial results).

The group boundaries are selected based on `Minimum Description Length`_.

Minimum Description Length
``````````````````````````

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

Anomaly Detection
`````````````````

Once the trend data is divided into groups, each group has its population average.
The start of the following group is marked as a regression (or progression)
if the new group's average is lower (higher) then the previous group's.

In the text below, "average at time <t>", shorthand "AVG[t]"
means "the group average of the group the sample at time <t> belongs to".

Trend Compliance
````````````````

Trend compliance metrics are targeted to provide an indication of trend
changes over a short-term (i.e. weekly) and a long-term (i.e.
quarterly), comparing the last group average AVG[last], to the one from week
ago, AVG[last - 1week] and to the maximum of trend values over last
quarter except last week, max(AVG[last - 3mths]..ANV[last - 1week]),
respectively. This results in following trend compliance calculations:

+-------------------------+---------------------------------+-----------+-------------------------------------------+
| Trend Compliance Metric | Trend Change Formula            | Value     | Reference                                 |
+=========================+=================================+===========+===========================================+
| Short-Term Change       | (Value - Reference) / Reference | AVG[last] | AVG[last - 1week]                         |
+-------------------------+---------------------------------+-----------+-------------------------------------------+
| Long-Term Change        | (Value - Reference) / Reference | AVG[last] | max(AVG[last - 3mths]..AVG[last - 1week]) |
+-------------------------+---------------------------------+-----------+-------------------------------------------+

.. _Minimum Description Length: https://en.wikipedia.org/wiki/Minimum_description_length
.. _Occam's razor: https://en.wikipedia.org/wiki/Occam%27s_razor
.. _bimodal distribution: https://en.wikipedia.org/wiki/Bimodal_distribution

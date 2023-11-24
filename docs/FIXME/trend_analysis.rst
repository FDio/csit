.. _trend_analysis:

Trend Analysis
^^^^^^^^^^^^^^

All measured performance trend data is treated as time-series data
that is modeled as a concatenation of groups,
within each group the samples come (independently) from
the same normal distribution (with some center and standard deviation).

Center of the normal distribution for the group (equal to population average)
is called a trend for the group.
All the analysis is based on finding the right partition into groups
and comparing their trends.

Anomalies in graphs
~~~~~~~~~~~~~~~~~~~

In graphs, the start of the following group is marked as a regression (red
circle) or progression (green circle), if the new trend is lower (or higher
respectively) then the previous group's.

Implementation details
~~~~~~~~~~~~~~~~~~~~~~

Partitioning into groups
````````````````````````

While sometimes the samples within a group are far from being distributed
normally, currently we do not have a better tractable model.

Here, "sample" should be the result of single trial measurement, with group
boundaries set only at test run granularity. But in order to avoid detecting
causes unrelated to VPP performance, the current presentation takes average of
all trials within the run as the sample. Effectively, this acts as a single
trial with aggregate duration.

Performance graphs show the run average as a dot (not all individual trial
results).

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
which discourages delimiting groups with averages close together.

Our implementation assumes that measurement precision is 1.0 pps.
Thus it is slightly wrong for trial durations other than 1.0 seconds.
Also, all the calculations assume 1.0 pps is totally negligible,
compared to stdev value.

The group selection algorithm currently has no parameters,
all the aforementioned encodings and handling of precision is hard-coded.
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

Common Patterns
~~~~~~~~~~~~~~~

When an anomaly is detected, it frequently falls into few known patterns,
each having its typical behavior over time.

We are going to describe the behaviors,
as they motivate our choice of trend compliance metrics.

Sample time and analysis time
`````````````````````````````

But first we need to distinguish two roles time plays in analysis,
so it is more clear which role we are referring to.

Sample time is the more obvious one.
It is the time the sample is generated.
It is the start time or the end time of the Jenkins job run,
does not really matter which (parallel runs are disabled,
and length of gap between samples does not affect metrics).

Analysis time is the time the current analysis is computed.
Again, the exact time does not usually matter,
what matters is how many later (and how fewer earlier) samples
were considered in the computation.

For some patterns, it is usual for a previously reported
anomaly to "vanish", or previously unseen anomaly to "appear late",
as later samples change which partition into groups is more probable.

Dashboard and graphs are always showing the latest analysis time,
the compliance metrics are using earlier sample time
with the same latest analysis time.

Alerting e-mails use the latest analysis time at the time of sending,
so the values reported there are likely to be different
from the later analysis time results shown in dashboard and graphs.

Ordinary regression
```````````````````

The real performance changes from previously stable value
into a new stable value.

For medium to high magnitude of the change, one run
is enough for anomaly detection to mark this regression.

Ordinary progressions are detected in the same way.

Small regression
````````````````

The real performance changes from previously stable value
into a new stable value, but the difference is small.

For the anomaly detection algorithm, this change is harder to detect,
depending on the standard deviation of the previous group.

If the new performance value stays stable, eventually
the detection algorithm is able to detect this anomaly
when there are enough samples around the new value.

If the difference is too small, it may remain undetected
(as new performance change happens, or full history of samples
is still not enough for the detection).

Small progressions have the same behavior.

Reverted regression
```````````````````

This pattern can have two different causes.
We would like to distinguish them, but that is usually
not possible to do just by looking at the measured values (and not telemetry).

In one cause, the real DUT performance has changed,
but got restored immediately.
In the other cause, no real performance change happened,
just some temporary infrastructure issue
has caused a wrong low value to be measured.

For small measured changes, this pattern may remain undetected.
For medium and big measured changes, this is detected when the regression
happens on just the last sample.

For big changes, the revert is also immediately detected
as a subsequent progression. The trend is usually different
from the previously stable trend (as the two population averages
are not likely to be exactly equal), but the difference
between the two trends is relatively small.

For medium changes, the detection algorithm may need several new samples
to detect a progression (as it dislikes single sample groups),
in the meantime reporting regressions (difference decreasing
with analysis time), until it stabilizes the same way as for big changes
(regression followed by progression, small difference
between the old stable trend and last trend).

As it is very hard for a fault code or an infrastructure issue
to increase performance, the opposite (temporary progression)
almost never happens.

Summary
```````

There is a trade-off between detecting small regressions
and not reporting the same old regressions for a long time.

For people reading e-mails, a sudden regression with a big number of samples
in the last group means this regression was hard for the algorithm to detect.

If there is a big regression with just one run in the last group,
we are not sure if it is real, or just a temporary issue.
It is useful to wait some time before starting an investigation.

With decreasing (absolute value of) difference, the number of expected runs
increases. If there is not enough runs, we still cannot distinguish
real regression from temporary regression just from the current metrics
(although humans frequently can tell by looking at the graph).

When there is a regression or progression with just a small difference,
it is probably an artifact of a temporary regression.
Not worth examining, unless temporary regressions happen somewhat frequently.

It is not easy for the metrics to locate the previous stable value,
especially if multiple anomalies happened in the last few weeks.
It is good to compare last trend with long term trend maximum,
as it highlights the difference between "now" and "what could be".
It is good to exclude last week from the trend maximum,
as including the last week would hide all real progressions.

.. _Minimum Description Length: https://en.wikipedia.org/wiki/Minimum_description_length
.. _Occam's razor: https://en.wikipedia.org/wiki/Occam%27s_razor
.. _bimodal distribution: https://en.wikipedia.org/wiki/Bimodal_distribution

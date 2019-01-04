.. _trending_methodology:

Trending Methodology
====================

Overview
--------

This document describes a high-level design of a system for continuous
performance measuring, trending and change detection for FD.io VPP SW
data plane (and other performance tests run withing CSIT sub-project).

There is a Performance Trending (PT) CSIT module, and a separate
Performance Analysis (PA) module ingesting results from PT and
analysing, detecting and reporting any performance anomalies using
historical data and statistical metrics. PA does also produce
trending dashboard and graphs with summary and drill-down views across
all specified tests that can be reviewed and inspected regularly by
FD.io developers and users community.

Performance Tests
-----------------

Performance trending relies on Maximum Receive Rate (MRR) tests.
MRR tests measure the packet forwarding rate, in multiple trials of set duration,
under the maximum load offered by traffic generator
regardless of packet loss. Maximum load for specified Ethernet frame
size is set to the bi-directional link rate.

Current parameters for performance trending MRR tests:

- **Ethernet frame sizes**: 64B (78B for IPv6 tests) for all tests, IMIX for
  selected tests (vhost, memif); all quoted sizes include frame CRC, but
  exclude per frame transmission overhead of 20B (preamble, inter frame
  gap).
- **Maximum load offered**: 10GE and 40GE link (sub-)rates depending on NIC
  tested, with the actual packet rate depending on frame size,
  transmission overhead and traffic generator NIC forwarding capacity.

  - For 10GE NICs the maximum packet rate load is 2* 14.88 Mpps for 64B,
    a 10GE bi-directional link rate.
  - For 40GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 40GE bi-directional link sub-rate limited by the packet forwarding
    capacity of 2-port 40GE NIC model (XL710) used on T-Rex Traffic
    Generator.

- **Trial duration**: 1 sec.
- **Number of trials per test**: 10.
- **Test execution frequency**: twice a day, every 12 hrs (02:00,
  14:00 UTC).

Note: MRR tests should be reporting bi-directional link rate (or NIC
rate, if lower) if tested VPP configuration can handle the packet rate
higher than bi-directional link rate, e.g. large packet tests and/or
multi-core tests. In other words MRR = min(VPP rate, bi-dir link rate,
NIC rate).

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
Diferent encodings cause different biases to large or small values.
In our implementation we have chosen probability density
corresponding to uniform distribution (from zero to maximal sample value)
for stdev and average of the first group,
but for averages of subsequent groups we have chosen a distribution
which disourages deliminating groups with averages close together.

Our implementation assumes thef measuremen precision is 1.0 pps.
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

In the text below, "average at time <t>", shorhand "AVG[t]"
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

Trend Presentation
------------------

Performance Dashboard
`````````````````````

Dashboard tables list a summary of per test-case VPP MRR performance
trend and trend compliance metrics and detected number of anomalies.

Separate tables are generated for each tested number of physical cores
for VPP workers (1c, 2c, 4c). Test case names are linked to
respective trending graphs for ease of navigation through the test data.

Trendline Graphs
````````````````

Trendline graphs show measured per run averages of MRR values,
group average values, and detected anomalies.
The graphs are constructed as follows:

- X-axis represents performance trend job build Id (csit-vpp-perf-mrr-
  daily-master-build).
- Y-axis represents run-average MRR value in Mpps.
- Markers to indicate anomaly classification:

  - Regression - red circle.
  - Progression - green circle.

- The line shows average MRR value of each group.

In addition the graphs show dynamic labels while hovering over graph
data points, representing (trend job build Id, MRR value) and the actual
vpp build number (b<XXX>) tested.


Jenkins Jobs
------------

Performance Trending (PT)
`````````````````````````

CSIT PT runs regular performance test jobs measuring and collecting MRR
data per test case. PT is designed as follows:

1. PT job triggers:

   a) Periodic e.g. daily.
   b) On-demand gerrit triggered.

2. Measurements and data calculations per test case:

  a) Max Received Rate (MRR) - for each trial measurement,
     send packets at link rate for trial duration,
     count total received packets, divide by trial duration.

3. Archive MRR values per test case.
4. Archive all counters collected at MRR.

Performance Analysis (PA)
`````````````````````````

CSIT PA runs performance analysis
including anomaly detection as described above.
PA is defined as follows:

1. PA job triggers:

   a) By PT job at its completion.
   b) On-demand gerrit triggered.

2. Download and parse archived historical data and the new data:

   a) Download RF output.xml files from latest PT job and compressed
      archived data.
   b) Parse out the data filtering test cases listed in PA specification
      (part of CSIT PAL specification file).

3. Re-calculate new groups and their averages.

4. Evaluate new test data:

   a) If the existing group is prolonged => Result = Pass,
      Reason = Normal. (to be updated base on the final Jenkins code).
   b) If a new group is detected with lower average => Result = Fail, Reason = Regression.
   c) If a new group is detected with higher average => Result = Pass, Reason = Progression.

5. Generate and publish results

   a) Relay evaluation result to job result. (to be updated base on the
      final Jenkins code).
   b) Generate a new set of trend summary dashboard and graphs.
   c) Publish trend dashboard and graphs in html format on
      https://docs.fd.io/.

Testbed HW configuration
------------------------

The testbed HW configuration is described on
`this FD.IO wiki page <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed#FD.IO_CSIT_testbed_-_Server_HW_Configuration>`_.

.. _Minimum Description Length: https://en.wikipedia.org/wiki/Minimum_description_length
.. _Occam's razor: https://en.wikipedia.org/wiki/Occam%27s_razor
.. _bimodal distribution: https://en.wikipedia.org/wiki/Bimodal_distribution

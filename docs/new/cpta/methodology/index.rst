.. _trending_methodology:

Trending Methodology
====================

Overview
--------

This document describes a high-level design of a system for continuous
performance measuring, trending and change detection for FD.io VPP SW
data plane. It builds upon the existing FD.io CSIT framework with
extensions to its throughput testing methodology, CSIT data analytics
engine (PAL – Presentation-and-Analytics-Layer) and associated Jenkins
jobs definitions.

Proposed design replaces existing CSIT performance trending jobs and
tests with new Performance Trending (PT) CSIT module and separate
Performance Analysis (PA) module ingesting results from PT and
analysing, detecting and reporting any performance anomalies using
historical trending data and statistical metrics. PA does also produce
trending dashboard and graphs with summary and drill-down views across
all specified tests that can be reviewed and inspected regularly by
FD.io developers and users community.

Performance Tests
-----------------

Performance trending is currently relying on the Maximum Receive Rate
(MRR) tests. MRR tests measure the packet forwarding rate under the
maximum load offered by traffic generator over a set trial duration,
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
    a 40GE bi-directional link sub-rate limited by TG 40GE NIC used,
    XL710.

- **Trial duration**: 10sec.
- **Execution frequency**: twice a day, every 12 hrs (02:00, 14:00 UTC).

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
are far from being distributed normally, we do not have a better tractable model.

The group boundaries are selected based on `Minimum Description Length`_.

TODO: Decide the level of detail for describing group selection.

Anomaly Detection
`````````````````

Once the trend data is divided into groups, each group has its population average.
The start of the following group is marked as a regression (or progression)
if the new group's average is lower (higher) then the previous group's.

Metrics
```````

TODO: Only needed for current trend compliance.

Following statistical metrics are used as performance trend indicators
over the rolling window of last <N> sets of historical measurement data:

- **TMM** : **Trimmed Moving Median**, median across the data set of <N>
  values excluding the outliers. Used as a trending value and as a
  reference for anomaly detection.

Trend Compliance
````````````````

TODO: Apply new detection algorithm also to trend compliance.

Trend compliance metrics are targeted to provide an indication of trend
changes over a short-term (i.e. weekly) and a long-term (i.e.
quarterly), comparing the last trend value, TMM[last], to one from week
ago, TMM[last - 1week] and to the maximum of trend values over last
quarter except last week, max(TMM[(last - 3mths)..(last - 1week)]),
respectively. This results in following trend compliance calculations:

+-------------------------+---------------------------------+-----------+------------------------------------------+
| Trend Compliance Metric | Trend Change Formula            | Value     | Reference                                |
+=========================+=================================+===========+==========================================+
| Short-Term Change       | (Value - Reference) / Reference | TMM[last] | TMM[last - 1week]                        |
+-------------------------+---------------------------------+-----------+------------------------------------------+
| Long-Term Change        | (Value - Reference) / Reference | TMM[last] | max(TMM[(last - 3mths)..(last - 1week)]) |
+-------------------------+---------------------------------+-----------+------------------------------------------+

Trend Presentation
------------------

Performance Dashboard
`````````````````````

Dashboard tables list a summary of per test-case VPP MRR performance
trend and trend compliance metrics and detected number of anomalies.

Separate tables are generated for tested VPP worker-thread-core
combinations (1t1c, 2t2c, 4t4c). Test case names are linked to
respective trending graphs for ease of navigation thru the test data.

Trendline Graphs
````````````````

Trendline graphs show per test case measured MRR throughput values with
associated gruop averages. The graphs are constructed as follows:

- X-axis represents performance trend job build Id (csit-vpp-perf-mrr-
  daily-master-build).
- Y-axis represents MRR throughput in Mpps.
- Markers to indicate anomaly classification:

  - Outlier - gray circle around MRR value point.
  - Regression - red circle.
  - Progression - green circle.

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

  a) Max Received Rate (MRR) - send packets at link rate over a trial
     period, count total received packets, divide by trial period.

3. Archive MRR per test case.
4. Archive all counters collected at MRR.

Performance Analysis (PA)
`````````````````````````

CSIT PA runs performance analysis including trendline calculation, trend
compliance and anomaly detection using specified trend analysis metrics
over the rolling window of last <N> sets of historical measurement data.
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

4. Evaluate new test data (TODO: Update.):

   a) If within the range of (TMA +/- 3*TMSD) => Result = Pass,
      Reason = Normal. (to be updated base on the final Jenkins code).
   b) If below the range => Result = Fail, Reason = Regression.
   c) If above the range => Result = Pass, Reason = Progression.

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

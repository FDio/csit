Trending Methodology
====================

Continuous Trending and Analysis
--------------------------------

This document describes a high-level design of a system for continuous
measuring, trending and performance change detection for FD.io VPP SW
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

Performance Trending Tests
--------------------------

Performance trending is currently relying on the Maximum Receive Rate
(MRR) tests. MRR tests measure the maximum forwarding rate under the
line rate packet load over a set trial duration, regardless of packet
loss.

Current parameters for performance trending MRR tests:

    - packet sizes: 64B (78B for IPv6 tests) for all tests, IMIX for
      selected tests (vhost, memif).
    - trial duration: 10sec.
    - execution frequency: twice a day, every 12 hrs (02:00, 14:00 UTC).

Performance Trend Analysis
--------------------------

All measured performance trend data is treated as time-series data that
can be modelled using normal distribution. After trimming the outliers,
the median and deviations from median are used for detecting performance
change anomalies following the three-sigma rule of thumb (a.k.a.
68-95-99.7 rule).

Analysis Metrics
````````````````

Following statistical metrics are proposed as performance trend
indicators over the rolling window of last <N> sets of historical
measurement data:

    - Q1, Q2, Q3 : Quartiles, three points dividing a ranked data set
      into four equal parts, Q2 is the median of the data.
    - IQR = Q3 - Q1 : Inter Quartile Range, measure of variability, used
      here to calculate and eliminate outliers.
    - Outliers : extreme values that are at least (1.5 * IQR) below Q1.

        - Note: extreme values that are at least (1.5 * IQR) above Q3 are not
          considered outliers, and are likely to be classified as
          progressions.

    - TMA: Trimmed Moving Average, average across the data set of the
      rolling window of <N> values without the outliers. Used here to
      calculate TMSD.
    - TMSD: Trimmed Moving Standard Deviation, standard deviation over the
      data set of the rolling window of <N> values without the outliers,
      requires calculating TMA. Used for anomaly detection.
    - TMM: Trimmed Moving Median, median across the data set of the rolling
      window of <N> values with all data points, excluding the outliers.
      Used as a trending value and as a reference for anomaly detection.

Outlier Detection
`````````````````

Outlier evaluation of test result of value <X> follows the definition
from previous section:

::

    Outlier Evaluation Formula      Evaluation Result
    ====================================================
    X < (Q1 - 1.5 * IQR)            Outlier
    X >= (Q1 - 1.5 * IQR)           Valid (For Trending)

Anomaly Detection
`````````````````

To verify compliance of test result of value <X> against defined trend
metrics and detect anomalies, three simple evaluation formulas are
used:

::

          Anomaly                                   Compliance        Evaluation
    Evaluation Formula                            Confidence Level      Result
    =============================================================================
    (TMM - 3 * TMSD) <= X <= (TMM + 3 * TMSD)         99.73%            Normal
    X < (TMM - 3 * TMSD)                              Anomaly         Regression
    X > (TMM + 3 * TMSD)                              Anomaly         Progression

TMM is used for the central trend reference point instead of TMA as it
is more robust to anomalies.

Trend Compliance
````````````````

Trend compliance metrics are targeted to provide an indication of trend
changes over a short-term (i.e. weekly) and a long-term (i.e.
quarterly), comparing the last trend value, TMM[last], to one from week
ago, TMM[last - 1week] and to the maximum of trend values over last
quarter except last week, max(TMM[(last - 3mths)..(last - 1week)]),
respectively. This results in following trend compliance calculations:

::

    Trend
    Compliance Metric     Change Formula    V(alue)      R(eference)
    =============================================================================================
    Short-Term Change     ((V - R) / R)     TMM[last]    TMM[last - 1week]
    Long-Term Change      ((V - R) / R)     TMM[last]    max(TMM[(last - 3mths)..(last - 1week)])

Trend Presentation
------------------

Trend Dashboard
```````````````

Dashboard tables list a summary of per test-case VPP MRR performance
trend and trend compliance metrics and detected number of anomalies.

Separate tables are generated for tested VPP worker-thread-core
combinations (1t1c, 2t2c, 4t4c). Test case names are linked to
respective trending graphs for ease of navigation thru the test data.

Trend Graphs
``````````````

Trends graphs show per test case measured MRR throughput values with
associated trendlines. The graphs are constructed as follows:

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


Jenkins Jobs Description
------------------------

Performance Trending (PT)
`````````````````````````

CSIT PT runs regular performance test jobs finding MRR per test case. PT
is designed as follows:

    #. PT job triggers:

        #. Periodic e.g. daily.
        #. On-demand gerrit triggered.

    #. Measurements and calculations per test case:

        #. MRR Max Received Rate

            #. Measured: Unlimited tolerance of packet loss.
            #. Send packets at link rate, count total received packets, divide
               by test trial period.

    #. Archive MRR per test case.
    #. Archive all counters collected at MRR.

Performance Analysis (PA)
`````````````````````````

CSIT PA runs performance analysis including trending and anomaly
detection using specified trend analysis metrics over the rolling window
of last <N> sets of historical measurement data. PA is defined as
follows:

    #. PA job triggers:

        #. By PT job at its completion.
        #. On-demand gerrit triggered.

    #. Download and parse archived historical data and the new data:

        #. Evalute new data from latest PT job against the rolling window of
           <N> sets of historical data.
        #. Download RF output.xml files and compressed archived data.
        #. Parse out the data filtering test cases listed in PA specification
           (part of CSIT PAL specification file).

    #. Calculate trend metrics for the rolling window of <N> sets of
       historical data:

        #. Calculate quartiles Q1, Q2, Q3.
        #. Trim outliers using IQR.
        #. Calculate TMA and TMSD.
        #. Calculate normal trending range per test case based on TMM and TMSD.

    #. Evaluate new test data against trend metrics:

        #. If within the range of (TMA +/- 3*TMSD) => Result = Pass, 
           Reason = Normal.
        #. If below the range => Result = Fail, Reason = Regression.
        #. If above the range => Result = Pass, Reason = Progression.

    #. Generate and publish results

        #. Relay evaluation result to job result.
        #. Generate a new set of trend summary dashboard and graphs.
        #. Publish trend dashboard and graphs in html format on https://docs.fd.io/.

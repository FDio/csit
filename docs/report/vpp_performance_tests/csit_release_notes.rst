CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. **Added VPP performance tests**

   - **MRR tests** : New MRR tests measure the packet forwarding rate
       under the maximum load offered by traffic generator over a set
       trial duration, regardless of packet loss. Maximum load for
       specified Ethernet frame size is set to the bi-directional link
       rate. MRR tests are used for continuous performance trending and
       for comparison between releases.

   - **Service Chaining with SRv6** : SRv6 (Segment Routing IPv6) proxy tests
       verifying performance of Endpoint to SR-unaware appliance via
       masquerading (End.AM), dynamic proxy (End.AD) or static proxy (End.AS)
       functions.

#. **Presentation and Analytics Layer (PAL)**

     - Added continuous performance measuring, trending and anomaly
       detection. Includes new PAL code and Jenkins jobs for Performance
       Trending (PT) and Performance Analysis (PA) producing performance
       trending dashboard and trendline graphs with summary and drill-
       down views across all specified tests that can be reviewed and
       inspected regularly by FD.io developers and users community.

#. **Test Framework Optimizations**

     - **Performance tests efficiency** : Qemu build/install
     optimizations, warmup phase handling, vpp restart handling.
     Resulted in improved stability and reduced total execution time by
     30% for single pkt size e.g. 64B/78B.

     - **General code housekeeping** : ongoing RF keywords
     optimizations, removal of redundant RF keywords.

Performance Changes
-------------------

Relative performance changes in measured packet throughput in CSIT
|release| are calculated against the results from CSIT |release-1|
report. Listed mean and standard deviation values are computed based on
a series of the same tests executed against respective VPP releases to
verify test results repeatibility, with percentage change calculated for
mean values. Note that the standard deviation is quite high for a small
number of packet throughput tests, what indicates poor test results
repeatability and makes the relative change of mean throughput value not
fully representative for these tests. The root causes behind poor
results repeatibility vary between the test cases.

NDR Throughput Changes
~~~~~~~~~~~~~~~~~~~~~~

NDR small packet throughput changes between releases are available in a CSV and
pretty ASCII formats:

  - `csv format for 1t1c <../_static/vpp/performance-changes-ndr-1t1c-full.csv>`_,
  - `csv format for 2t2c <../_static/vpp/performance-changes-ndr-2t2c-full.csv>`_,
  - `pretty ASCII format for 1t1c <../_static/vpp/performance-changes-ndr-1t1c-full.txt>`_,
  - `pretty ASCII format for 2t2c <../_static/vpp/performance-changes-ndr-2t2c-full.txt>`_.

PDR Throughput Changes
~~~~~~~~~~~~~~~~~~~~~~

NDR small packet throughput changes between releases are available in a CSV and
pretty ASCII formats:

  - `csv format for 1t1c <../_static/vpp/performance-changes-pdr-1t1c-full.csv>`_,
  - `csv format for 2t2c <../_static/vpp/performance-changes-pdr-2t2c-full.csv>`_,
  - `pretty ASCII format for 1t1c <../_static/vpp/performance-changes-pdr-1t1c-full.txt>`_,
  - `pretty ASCII format for 2t2c <../_static/vpp/performance-changes-pdr-2t2c-full.txt>`_.

MRR Throughput Changes
~~~~~~~~~~~~~~~~~~~~~~

MRR changes between releases are available in a CSV and
pretty ASCII formats:

  - `csv format for 1t1c <../_static/vpp/performance-changes-mrr-1t1c-full.csv>`_,
  - `csv format for 2t2c <../_static/vpp/performance-changes-mrr-2t2c-full.csv>`_,
  - `csv format for 4t4c <../_static/vpp/performance-changes-mrr-4t4c-full.csv>`_,
  - `pretty ASCII format for 1t1c <../_static/vpp/performance-changes-mrr-1t1c-full.txt>`_,
  - `pretty ASCII format for 2t2c <../_static/vpp/performance-changes-mrr-2t2c-full.txt>`_,
  - `pretty ASCII format for 4t4c <../_static/vpp/performance-changes-mrr-4t4c-full.txt>`_.

Known Issues
------------

<to be updated before rls1804 release>

Here is the list of known issues in CSIT |release| for VPP performance tests:

+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                           | Jira ID    | Description                                                     |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | Vic1385 and Vic1227 low performance.            | VPP-664    | Low NDR performance.                                            |
|   |                                                 |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | Sporadic (1 in 200) NDR discovery test failures | CSIT-570   | DPDK reporting rx-errors, indicating L1 issue. Suspected issue  |
|   | on x520.                                        |            | with HW combination of X710-X520 in LF testbeds. Not observed   |
|   |                                                 |            | outside of LF testbeds.                                         |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 3 | Lower than expected NDR throughput with         | CSIT-571   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 4 | rls1801 plugin related performance regression   | CSIT-925   | With all plugins loaded NDR, PDR and MaxRates vary              |
|   |                                                 |            | intermittently from 3% to 5% across multiple test executions.   |
|   |                                                 |            | Requires plugin code bisecting.                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 5 | rls1801 generic small performance regression    | CSIT-926   | Generic performance regression of discovered NDR, PDR and       |
|   | ip4base, l2xcbase, l2bdbase                     |            | MaxRates of -3%..-1% vs. rls1710, affects ip4base, l2xcbase,    |
|   |                                                 |            | l2bdbase test suites. Not detected by CSIT performance trending |
|   |                                                 |            | scheme as it was masked out by another issue CSIT-925.          |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 6 | rls1801 substantial NDR/PDR regression for      | CSIT-928   | NDR regression of -7%..-15%, PDR regression of -3%..-15%        |
|   | IPSec tunnel scale with HW QAT crypto-dev       |            | compared to rls1710.                                            |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+

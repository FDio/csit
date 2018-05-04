CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added VPP performance tests

   - **Container Service Chain Topologies Orchestrated by K8s with VPP Memif**

     - Added tests with VPP vswitch in container connecting a number of VPP-
       in-container service chain topologies with L2 Cross-Connect and L2
       Bridge-Domain configurations, orchestrated by Kubernetes. Added
       following forwarding topologies: i) "Parallel" with packets flowing from
       NIC via VPP to container and back to VPP and NIC; ii) "Chained" (a.k.a.
       "Snake") with packets flowing via VPP to container, back to VPP, to next
       container, back to VPP and so on until the last container in a chain,
       then back to VPP and NIC; iii) "Horizontal" with packets flowing via VPP
       to container, then via "horizontal" memif to next container, and so on
       until the last container, then back to VPP and NIC;

   - **VPP TCP/IP stack**

     - Added tests for VPP TCP/IP stack using VPP built-in HTTP server.
       WRK traffic generator is used as a client-side;

   - **SRv6**

     - Initial SRv6 (Segment Routing IPv6) tests verifying performance of
       IPv6 and SRH (Segment Routing Header) encapsulation, decapsulation,
       lookups and rewrites based on configured End and End.DX6 SRv6 egress
       functions;

   - **IPSecSW**

     - SW computed IPSec encryption with AES-GCM, CBC-SHA1 ciphers, in
       combination with IPv4 routed-forwarding;

#. Presentation and Analytics Layer

     - Added throughput speedup analysis for multi-core and multi-thread
       VPP tests into Presentation and Analytics Layer (PAL) for automated
       CSIT test results analysis;

#. Other changes

     - **Framework optimizations**

       - Ability to run CSIT framework on ARM architecture;

       - Overall stability improvements;

     - **NDR and PDR throughput binary search change**

       - Increased binary search resolution by reducing final step from
         100kpps to 50kpps;

     - **VPP plugin loaded as needed by tests**

       - From this release only plugins required by tests are loaded at
         VPP initialization time. Previously all plugins were loaded for
         all tests;

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
| 4 | QAT IPSec scale with 1000 tunnels (interfaces)  | VPP-1121   | VPP crashes during configuration of 1000 IPsec tunnels.         |
|   | in 2t2c config, all tests are failing.          |            | 1t1c tests are not affected                                     |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 5 | rls1801 plugin related performance regression   | CSIT-925   | With all plugins loaded NDR, PDR and MaxRates vary              |
|   |                                                 |            | intermittently from 3% to 5% across multiple test executions.   |
|   |                                                 |            | Requires plugin code bisecting.                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 6 | rls1801 generic small performance regression    | CSIT-926   | Generic performance regression of discovered NDR, PDR and       |
|   | ip4base, l2xcbase, l2bdbase                     |            | MaxRates of -3%..-1% vs. rls1710, affects ip4base, l2xcbase,    |
|   |                                                 |            | l2bdbase test suites. Not detected by CSIT performance trending |
|   |                                                 |            | scheme as it was masked out by another issue CSIT-925.          |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 7 | rls1801 substantial NDR performance regression  | CSIT-927   | Much lower NDR for vhostvr1024 tests, with mean values          |
|   | for vhost-user vring size of 1024               |            | regression of -17%..-42% vs. rls1710, but also very high        |
|   |                                                 |            | standard deviation of up to 1.46 Mpps => poor repeatibility.    |
|   |                                                 |            | Making mean values not fully representative.                    |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 8 | rls1801 substantial NDR/PDR regression for      | CSIT-928   | NDR regression of -7%..-15%, PDR regression of -3%..-15%        |
|   | IPSec tunnel scale with HW QAT crypto-dev       |            | compared to rls1710.                                            |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+

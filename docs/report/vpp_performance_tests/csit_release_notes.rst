Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - CSIT test environment is versioned, see
     :ref:`test_environment_versioning`.

   - To identify performance changes due to VPP code changes from
     v20.01.0 to v20.05.0, both have been tested in CSIT environment
     ver. 4 and compared against each other. All substantial
     progressions has been marked up with RCA analysis. See
     :ref:`vpp_compare_current_vs_previous_release` and
     :ref:`vpp_known_issues`.

#. TEST FRAMEWORK

   - **CSIT PAPI support**: Due to issues with PAPI performance, VAT is
     still used in CSIT for all VPP scale tests. See known issues below.

   - **General Code Housekeeping**: Ongoing RF keywords optimizations,
     removal of redundant RF keywords and aligning of suite/test
     setup/teardowns.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs improvements**: Added possibility to use Gbps on Y-axis in
     Packet Throughput and Speedup Multi-Core graphs, added unidirectional
     mode to the Latency graphs.

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

List of known issues in |csit-release| for VPP performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-570                               | Sporadic (1 in 200) NDR discovery test failures on x520. DPDK reporting rx-errors, indicating L1 issue.   |
|    | <https://jira.fd.io/browse/CSIT-570>`_  | Suspected issue with HW combination of X710-X520 in LF testbeds. Not observed outside of LF testbeds.     |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `VPP-662                                | 9000B packets not supported by NICs VIC1227 and VIC1387.                                                  |
|    | <https://jira.fd.io/browse/VPP-662>`_   |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `VPP-1677                               | 9000B ip4 nat44: VPP crash + coredump.                                                                    |
|    | <https://jira.fd.io/browse/VPP-1677>`_  | VPP crashes very often in case that NAT44 is configured and it has to process IP4 jumbo frames (9000B).   |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1591                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1499>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+                                                                                                           |
|    | `VPP-1763                               |                                                                                                           |
|    | <https://jira.fd.io/browse/VPP-1763>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `VPP-1675                               | IPv4 IPSEC 9000B packet tests are failing as no packet is forwarded.                                      |
|    | <https://jira.fd.io/browse/VPP-1675>`_  | Reason: chained buffers are not supported.                                                                |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1593                              | IPv4 AVF 9000B packet tests are failing on 3n-skx while passing on 2n-skx.                                |
|    | <https://jira.fd.io/browse/CSIT-1593>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1679                              | 2n-clx VPP ip4 tests with xxv710 and avf driver are sporadically failing.                                 |
|    | <https://jira.fd.io/browse/CSIT-1679>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1731                              | Confirm the cause for ip4scale -rnd regressions.                                                          |
|    | <https://jira.fd.io/browse/CSIT-1731>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1735                              | Identify cause of ethip6-ip6scale2m progression.                                                          |
|    | <https://jira.fd.io/browse/CSIT-1735>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1738                              | Identify cause for vppl2xc CSIT progressions.                                                             |
|    | <https://jira.fd.io/browse/CSIT-1738>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1739                              | Identify cause of ACL regressions.                                                                        |
|    | <https://jira.fd.io/browse/CSIT-1739>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1740                              | Identify cause for avf-eth-l2xcbase CSIT progression.                                                     |
|    | <https://jira.fd.io/browse/CSIT-1740>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1741                              | Identify cause for vppl2xc VPP regressions.                                                               |
|    | <https://jira.fd.io/browse/CSIT-1741>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1742                              | Identify cause of ipsec CSIT regression.                                                                  |
|    | <https://jira.fd.io/browse/CSIT-1742>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  8 | `CSIT-1744                              | Identify cause of memif VPP progression.                                                                  |
|    | <https://jira.fd.io/browse/CSIT-1744>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  9 | `CSIT-1745                              | Verify cause of l2bdscale10kmaclrn VPP progression.                                                       |
|    | <https://jira.fd.io/browse/CSIT-1745>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 10 | `CSIT-1746                              | Identify cause for avf-dot1q-ip6base VPP progression.                                                     |
|    | <https://jira.fd.io/browse/CSIT-1746>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 11 | `CSIT-1747                              | Identify cause of ip4base-nat44 VPP progression.                                                          |
|    | <https://jira.fd.io/browse/CSIT-1747>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 12 | `CSIT-1748                              | Identify cause of aes128cbc-hmac512sha VPP progression.                                                   |
|    | <https://jira.fd.io/browse/CSIT-1748>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 13 | `CSIT-1749                              | Identify cause for l2bdbasemaclrn VPP progression in tests with dpdk app in VM.                           |
|    | <https://jira.fd.io/browse/CSIT-1749>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

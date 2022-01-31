.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Intel Xeon Ice Lake**: Performance test data for these platforms
     continues to be provided by external Intel benchmarking labs
     executing |csit-release| tests. For details about the physical
     setup see :ref:`tested_physical_topologies`.

   - **Reduction of tests**: Removed certain test variations executed
     iteratively for the report (as well as in daily and weekly
     trending) due to physical testbeds overload.

#. TEST FRAMEWORK

   - **CSIT test environment** version has been updated to ver. 9, see
     :ref:`test_environment_versioning`.

   - **CSIT PAPI support**: Due to issues with PAPI performance, and
     deprecation of VAT, CLI is used in CSIT for many VPP scale tests.
     See known issues below.

   - **General Code Housekeeping**: Ongoing code optimizations and bug
     fixes.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs improvements**: Updated Packet Latency graphs,
     see :ref:`latency_methodology`.

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

Fixed
_____

Issues reported in previous releases which were fixed in this release:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1789                              | AVF driver does not perform RSS in a deterministic way.                                                   |
|    | <https://jira.fd.io/browse/CSIT-1789>`_ | VPP now uses the same RSS key with AVF driver as with DPDK driver.                                        |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1786                              | IP4 and IP6 scale tests failing with no traffic forwarded.                                                |
|    | <https://jira.fd.io/browse/CSIT-1786>`_ | CSIT replaced the old single VAT command by file full of "exec" CLI commands executed by VAT.             |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Old
___

Issues reported in previous releases which still affect the current results.

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  3 | `CSIT-1782                              | Multicore AVF tests are failing when trying to create interface.                                          |
|    | <https://jira.fd.io/browse/CSIT-1782>`_ | Frequency is reduced by s CSIT workaround, but occasional failures do still happen.                       |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1671                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1671>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+ Currently, the time critical code uses VAT running large files with exec statements and CLI commands.     |
|    | `VPP-1763                               | Still, we needed to reduce the number of scale tests run to keep overall duration reasonable.             |
|    | <https://jira.fd.io/browse/VPP-1763>`_  | More improvements needed to achieve sufficient configuration speed.                                       |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1789                              | IPSEC SW async scheduler tests show bad behavior.                                                         |
|    | <https://jira.fd.io/browse/CSIT-1789>`_ | VPP code is not behaving correctly when crypto workers are the bottleneck.                                |
|    +-----------------------------------------+                                                                                                           |
|  5 | `VPP-1998                               |                                                                                                           |
|    | <https://jira.fd.io/browse/VPP-1998>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1785                              | NAT44ED tests failing to establish all TCP sessions.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1785>`_ | At least for max scale, in allotted time (limited by session 500s timeout) due to worse                   |
|    +-----------------------------------------+ slow path performance than previously measured and calibrated for.                                        |
|    | `VPP-1972                               | CSIT removed the max scale NAT tests to avoid this issue.                                                 |
|    | <https://jira.fd.io/browse/VPP-1972>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1791                              | Performance regression in RDMA tests, due to CSIT environment changes.                                    |
|    | <https://jira.fd.io/browse/CSIT-1791>`_ | Two symptoms: 1. 10-20% regression across most tests. 2. DUT performance cap just below 38 Mpps.          |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

New
___

No new issues appeared in |csit-release| for VPP performance tests,
except for the performance changes listed below.

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                          |
+====+=========================================+============================================================+
|  0 |                                         | To be updated when descriptions in Jira tickets are ready. |
+----+-----------------------------------------+------------------------------------------------------------+

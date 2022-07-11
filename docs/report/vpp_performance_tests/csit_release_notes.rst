.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Regressions with DPDK drivers**: Change from DPDK v21.08 to DPDK
     v21.11 introduced regression across all tests using dpdk
     drivers (with dpdk_plugin loaded). Compared to previous VPP
     release performance drop varies in the range of -15% to -6%,
     depending on test. It is related to updated MTU checks within
     DPDK code and associated VPP code changes. See
     `VPP v2202 release notes <https://s3-docs.fd.io/vpp/22.02/aboutvpp/releasenotes/v22.02.html>`_
     and :ref:`vpp_known_issues`.

   - **Number of CSIT 9000B frame tests failing**: tests with higher
     encapsulation overhead are failing due to exceeding default
     Ethernet Maximum Frame Size value that has been reduced by MTU
     related VPP code changes. See
     `VPP v2202 release notes <https://s3-docs.fd.io/vpp/22.02/aboutvpp/releasenotes/v22.02.html>`_
     and :ref:`vpp_known_issues`.

   - **Intel Xeon Ice Lake**: Performance test data for these platforms
     is now provided by testbeds newly installed in FD.io CSIT labs.
     For details about the physical setup see
     :ref:`physical_testbeds_2n_icx` and
     :ref:`physical_testbeds_3n_icx`.

   - **Arm Ampere Altra**: Performance test data for these platforms
     is now provided by testbeds newly installed in FD.io CSIT labs.
     For details about the physical setup see
     :ref:`physical_testbeds_3n_alt`.

   - **Reduction of tests**: Removed certain test variations executed
     iteratively for the report (as well as in daily and weekly
     trending) due to physical testbeds overload.

   - **RC2 coverage test data is used for 2n-icx test bed**: There is only
     one 2n-icx test bed and the amount of tests is large (same as 2n-skx with 4
     test beds), so we decided to use test data already available from RC2
     testing.

#. TEST FRAMEWORK

   - **CSIT test environment** version has been updated to ver. 10, see
     :ref:`test_environment_versioning`.

   - **CSIT PAPI support**: Due to issues with PAPI performance, and
     deprecation of VAT, VPP CLI is used in CSIT for many VPP scale
     tests. See :ref:`vpp_known_issues`.

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

New
___

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1827                              | 3n-icx, 3n-skx: all AVF crypto tests sporadically fail. 1518B with no traffic, IMIX with excessive        |
|    | <https://jira.fd.io/browse/CSIT-1827>`_ | packet loss.                                                                                              |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1830                              | All testbeds: All TCP tput (and pps) tests are failing for small packets.                                 |
|    | <https://jira.fd.io/browse/CSIT-1830>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1832                              | 3n-alt: NDR 1 packet lost on random tests.                                                                |
|    | <https://jira.fd.io/browse/CSIT-1832>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1834                              | 2n-icx, 2n-skx: sporadic AVF soak tests failing to find critical load with PLRsearch.                     |
|    | <https://jira.fd.io/browse/CSIT-1834>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1846                              | 2n-skx, 2n-clx, 2n-icx: ALL 1518B TCP tput tests failing with big packet loss.                            |
|    | <https://jira.fd.io/browse/CSIT-1846>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1847                              | 2n-skx: all 10vm-1t test failed with half of packets dropped.                                             |
|    | <https://jira.fd.io/browse/CSIT-1847>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Previous
________

Issues reported in previous releases which still affect the current results.

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1799                              | All NAT44-ED 16M scale tests fail while setting NAT44 address range.                                      |
|    | <https://jira.fd.io/browse/CSIT-1799>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1800                              | All Geneve L3 mode scale tests (1024 tunnels) are failing.                                                |
|    | <https://jira.fd.io/browse/CSIT-1800>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1802                              | AF-XDP - NDR tests failing from time to time.                                                             |
|    | <https://jira.fd.io/browse/CSIT-1802>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1803                              | 3n-icx testbeds (Icelake): all IMIX aes128cbc-hmac512sha tests are failing due to excessive packet loss.  |
|    | <https://jira.fd.io/browse/CSIT-1803>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1804                              | 3n-tsh testbed (Taishan): NDR tests failing from time to time.                                            |
|    | <https://jira.fd.io/browse/CSIT-1804>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1812                              | All IMIX NAT44DET 4m 16m scale tests fail due to not creating required session count.                     |
|    | <https://jira.fd.io/browse/CSIT-1812>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1782                              | Multicore AVF tests are failing when trying to create interface.                                          |
|    | <https://jira.fd.io/browse/CSIT-1782>`_ | Frequency is reduced by CSIT workaround, but occasional failures do still happen.                         |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  8 | `CSIT-1671                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1671>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+ Currently, the time critical code uses VAT running large files with exec statements and CLI commands.     |
|    | `VPP-1763                               | Still, we needed to reduce the number of scale tests run to keep overall duration reasonable.             |
|    | <https://jira.fd.io/browse/VPP-1763>`_  | More improvements needed to achieve sufficient configuration speed.                                       |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  9 | `CSIT-1785                              | NAT44ED tests failing to establish all TCP sessions.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1785>`_ | At least for max scale, in allotted time (limited by session 500s timeout) due to worse                   |
|    +-----------------------------------------+ slow path performance than previously measured and calibrated for.                                        |
|    | `VPP-1972                               | CSIT removed the max scale NAT tests to avoid this issue.                                                 |
|    | <https://jira.fd.io/browse/VPP-1972>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 10 | `CSIT-1801                              | 9000B payload frames not forwarded over tunnels due to violating supported Max Frame Size (VxLAN, LISP,   |
|    | <https://jira.fd.io/browse/CSIT-1801>`_ | SRv6).                                                                                                    |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 11 | `CSIT-1808                              | All tests with 9000B payload frames not forwarded over memif interfaces.                                  |
|    | <https://jira.fd.io/browse/CSIT-1808>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 12 | `CSIT-1809                              | All tests with 9000B payload frames not forwarded over vhostuser interfaces.                              |
|    | <https://jira.fd.io/browse/CSIT-1809>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Fixed
_____

Issues reported in previous releases which were fixed in this release:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1810                              | DPDK - performance regression with DPDK driver when Max Frame Size is set to less than 2023.              |
|    | <https://jira.fd.io/browse/CSIT-1810>`_ |                                                                                                           |
|    +-----------------------------------------+                                                                                                           |
|    | `VPP-1876                               | Worse performance with DPDK driver when MTU is set to 2022 or less.                                       |
|    | <https://jira.fd.io/browse/VPP-1876>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1811                              | All 9000B NAT44DET 64k 1m scale tests fail due to bps rate set to high on TRex.                           |
|    | <https://jira.fd.io/browse/CSIT-1811>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1791                              | Performance regression in RDMA tests, due to CSIT environment changes.                                    |
|    | <https://jira.fd.io/browse/CSIT-1791>`_ | Two symptoms: 1. 10-20% regression across most tests. 2. DUT performance cap just below 38 Mpps.          |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

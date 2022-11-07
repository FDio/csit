.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Tweaks to test selection**:
     - Removed 2n-skx and 3n-skx as testbeds are decommisioned.
     - Added 3n-snr as an officially supported testbed.
     - Added wireguard tests.
     - Added TRex tests to 2n-icx and 1n-aws.

#. TEST FRAMEWORK

   - **CSIT test environment** version has been updated to ver. 11, see
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
|  7 | `CSIT-1849                              | 2n-skx: UDP 16m tput tests fail to create all sessions.                                                   |
|    | <https://jira.fd.io/browse/CSIT-1849>`_ |                                                                                                           |
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
|  5 | `CSIT-1804                              | 3n-tsh, 3n-alt testbed (Taishan, Altra): NDR tests failing from time to time.                             |
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

.. _vpp_rca:

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                   |
+====+=========================================+=====================================================================================+
|  1 | `CSIT-1851                              | trending regression: various icelake tests around 2202-04-15                        |
|    | <https://jira.fd.io/browse/CSIT-1851>`_ | Somewhat expected consequence of a VPP usability fix,                               |
|    |                                         | the previous VPP compiler version was too new for the OS used.                      |
+----+-----------------------------------------+-------------------------------------------------------------------------------------+
|  2 | `VPP-2030                               | regression: ip6base on ICX around 2022-03-23                                        |
|    | <https://jira.fd.io/browse/VPP-2030>`_  | "Loads blocked due to overlapping with a preceding store that cannot be forwarded." |
|    |                                         | started happening in ip6-lookup graph node.                                         |
+----+-----------------------------------------+-------------------------------------------------------------------------------------+
|  3 | `CSIT-1852                              | 2n-zn2 mellanox performance cap                                                     |
|    | <https://jira.fd.io/browse/CSIT-1852>`_ | Old issue, only now distinguished from CSIT-1751.                                   |
|    |                                         | This testbed+nic combination is capped below 28 Mpps, cause not identified yet.     |
+----+-----------------------------------------+-------------------------------------------------------------------------------------+
|  4 | `CSIT-1853                              | trending regression: nat44ed cps around 2202-04-01                                  |
|    | <https://jira.fd.io/browse/CSIT-1853>`_ | VPP change added more computation to slow path (in order to support multiple VRFs). |
|    |                                         | Not clear if the VPP implementation is optimized enough.                            |
+----+-----------------------------------------+-------------------------------------------------------------------------------------+

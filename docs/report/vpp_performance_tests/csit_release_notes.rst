.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Enhanced and added VPP hoststack tests** to daily and weekly
     trending including: Quic VPP Echo, UDP+TCP LD_PRELOAD iPerf3,
     LD_PRELOAD NGINX.

   - **Added Nvidia/Mellanox DPDK tests** to daily and weekly trending
     and report, in addition to RDMA_CORE ones that were already
     there.

   - **Jumbo frames tests** got fixed and re-added number of to report
     coverage tests.

   - **Intel Xeon SKX performance testbeds** got decommissioned and
     removed from FD.io performance lab.

#. TEST FRAMEWORK

   - **CSIT test environment** version has not changed from ver. 11 used
     in previous release, see :ref:`test_environment_versioning`.

   - **CSIT PAPI optimizations for scale** got applied improving PAPI
     programming speed especially for large scale tests. VAT has been
     now completely deprecated from CSIT.

   - **General Code Housekeeping**: Ongoing code optimizations and bug
     fixes.

#. PRESENTATION AND ANALYTICS LAYER

   - **C-Dash** `performance dashboard <http://csit.fd.io/>`_ got updated UI and
     updated backend increasing its performance and robustness.

telemetry in CSIT Dash DONE

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

Editing Note: below listed known issues need to be updated to reflect the current state as tracked on `CSIT TestFailuresTracking wiki <https://wiki.fd.io/view/CSIT/TestFailuresTracking>`_.

New
___

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1890                              | 3n-alt: Tests failing until 40Ge Interface comes up.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1890>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Previous
________

Issues reported in previous releases which still affect the current results.

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1782                              | Multicore AVF tests are failing when trying to create interface.                                          |
|    | <https://jira.fd.io/browse/CSIT-1782>`_ | Frequency is reduced by CSIT workaround, but occasional failures do still happen.                         |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1785                              | NAT44ED tests failing to establish all TCP sessions.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1785>`_ | At least for max scale, in allotted time (limited by session 500s timeout) due to worse                   |
|    +-----------------------------------------+ slow path performance than previously measured and calibrated for.                                        |
|    | `VPP-1972                               | CSIT removed the max scale NAT tests to avoid this issue.                                                 |
|    | <https://jira.fd.io/browse/VPP-1972>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1799                              | All NAT44-ED 16M sessions CPS scale tests fail while setting NAT44 address range.                         |
|    | <https://jira.fd.io/browse/CSIT-1799>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1800                              | All Geneve L3 mode scale tests (1024 tunnels) are failing.                                                |
|    | <https://jira.fd.io/browse/CSIT-1800>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1801                              | 9000B payload frames not forwarded over tunnels due to violating supported Max Frame Size (VxLAN, LISP,   |
|    | <https://jira.fd.io/browse/CSIT-1801>`_ | SRv6).                                                                                                    |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1802                              | all testbeds: AF-XDP - NDR tests failing from time to time.                                               |
|    | <https://jira.fd.io/browse/CSIT-1802>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1804                              | All testbeds: NDR tests failing from time to time.                                                        |
|    | <https://jira.fd.io/browse/CSIT-1804>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  8 | `CSIT-1808                              | All tests with 9000B payload frames not forwarded over memif interfaces.                                  |
|    | <https://jira.fd.io/browse/CSIT-1808>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  9 | `CSIT-1827                              | 3n-icx, 3n-skx: all AVF crypto tests sporadically fail. 1518B with no traffic, IMIX with excessive        |
|    | <https://jira.fd.io/browse/CSIT-1827>`_ | packet loss.                                                                                              |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 10 | `CSIT-1835                              | 3n-icx: QUIC vppecho BPS tests failing on timeout when checking hoststack finished.                       |
|    | <https://jira.fd.io/browse/CSIT-1835>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 11 | `CSIT-1849                              | 2n-skx, 2n-clx, 2n-icx: UDP 16m TPUT tests fail to create all sessions.                                   |
|    | <https://jira.fd.io/browse/CSIT-1849>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 12 | `CSIT-1864                              | 2n-clx: half of the packets lost on PDR tests.                                                            |
|    | <https://jira.fd.io/browse/CSIT-1864>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 13 | `CSIT-1877                              | 3n-tsh: all VM tests failing to boot VM.                                                              |
|    | <https://jira.fd.io/browse/CSIT-1877>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 14 | `CSIT-1883                              | 3n-snr: All hwasync wireguard tests failing when trying to verify device.                                 |
|    | <https://jira.fd.io/browse/CSIT-1883>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 15 | `CSIT-1884                              | 2n-clx, 2n-icx: All NAT44DET NDR PDR IMIX over 1M sessions BIDIR tests failing to create enough sessions. |
|    | <https://jira.fd.io/browse/CSIT-1884>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 16 | `CSIT-1885                              | 3n-icx: 9000b ip4 ip6 l2 NDRPDR AVF tests are failing to forward traffic.                                 |
|    | <https://jira.fd.io/browse/CSIT-1885>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 17 | `CSIT-1886                              | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.                               |
|    | <https://jira.fd.io/browse/CSIT-1886>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Fixed
_____

Issues reported in previous releases which were fixed in this release:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1868                              | 2n-clx: ALL ldpreload-nginx tests fails when trying to start nginx.                                       |
|    | <https://jira.fd.io/browse/CSIT-1868>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1871                              | 3n-snr: 25GE interface between SUT and TG/TRex goes down randomly.                                        |
|    | <https://jira.fd.io/browse/CSIT-1871>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

.. _vpp_rca:

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+--------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                  |
+====+=========================================+====================================================================+
|  1 | `CSIT-1887                              | rls2210 RCA: ASTF tests                                            |
|    | <https://jira.fd.io/browse/CSIT-1887>`_ | TRex upgrade decreased TRex performance. NAT results not affected, |
|    |                                         | except on Denverton due to interference from VPP-2010.             |
+----+-----------------------------------------+--------------------------------------------------------------------+
|  2 | `CSIT-1888                              | rls2210 RCA: testbed differences, especially for ipsec             |
|    | <https://jira.fd.io/browse/CSIT-1888>`_ | Not caused by VPP code nor CSIT code.                              |
|    |                                         | Most probable cause is clang-14 behavior.                          |
+----+-----------------------------------------+--------------------------------------------------------------------+
|  3 | `CSIT-1889                              | rls2210 RCA: policy-outbound-nocrypto                              |
|    | <https://jira.fd.io/browse/CSIT-1889>`_ | When VPP added spd fast path matching (Gerrit 36097),              |
|    |                                         | it decreased MRR of the corresponding tests, at least on 3-alt.    |
+----+-----------------------------------------+--------------------------------------------------------------------+

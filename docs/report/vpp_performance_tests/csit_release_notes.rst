.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Added new performance testbed 3n-snr** (3 Node SnowRidge, with Intel
     Atom processors).

   - **Added GTPU HW offload tests** using VPP GTPU hardware offload
     with Intel e810 4p25ge NICs (3n-icx testbeds only). These tests
     were already there in CSIT-2206, but were yielding invalid
     results due to using TRex v2.97 that was incompatible with e810
     NICs used for those tests.

   - **Added Wireguard tests** using VPP software crypto (3n-icx, 3n-snr
     testbeds) and using built-in hardware crypto QAT device (3n-snr testbed
     only).

   - **Reduction of tests**: Removed certain test variations executed
     iteratively for the report (as well as in daily and weekly
     trending) due to physical testbeds overload.

#. TEST FRAMEWORK

   - CSIT-2210 executes all VPP v22.10 performance tests using vpp ubuntu2204
     images, due to CSIT execution environment change as noted below. This
     applies to all performance testbeds except Denverton. Consequently, VPP
     v22.06 has not been re-tested in CSIT-2210 environment, as no ubuntu204
     images are available for that VPP version. Performance comparison
     between VPP v22.10 (current version) vs VPP v22.06 (previous version)
     may be impacted by VPP build environment change (ubuntu2004 to ubuntu
     2204) change and CSIT environment change. See :ref:`vpp_rca` for
     details.

   - **CSIT test environment** version has been updated to ver. 11, see
     :ref:`test_environment_versioning`.

   - **TCP TPUT profiles** had to be changed, as newer TRex versions
     are not deterministic enough when deciding when to send an ACK.

   - **CSIT PAPI support**: Due to issues with PAPI performance, and
     deprecation of VAT, VPP CLI is used in CSIT for many VPP scale
     tests. See :ref:`vpp_known_issues`.

   - **General Code Housekeeping**: Ongoing code optimizations and bug
     fixes.

#. PRESENTATION AND ANALYTICS LAYER

   - **C-Dash** `performance dashboard <http://csit.fd.io/>`_ got updated UI and
     updated backend increasing its performance and robustness.

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

+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                       |
+====+=========================================+=========================================================================================================+
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

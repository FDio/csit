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

   - `Performance dashboard <http://csit.fd.io/>`_ got updated with
     addition of VPP telemetry trending across all VPP tests. A number
     of code and AWS resource usage optimizations got applied to the
     data processing pipeline and UI frontend and backend.

   - Examples of release iterative data visualisation:

     - `Packet throughput 2n-icx-e810cq-ip4-base-scale-pdr <https://csit.fd.io/report/#eNrdVcluwjAQ_Zr0ggbZDml64QDkP5BxhhJlwYxNVPr1OAhpYiGO7cEHb3pv1qeRnT8T7h1266zYZuU2U2VThy3LN4twUOdULhSM1oLKl-FG2KF2CGqAxvyAFOIblZX4JYW5gB6P0NgVfK4OIA2gP02vsA6Tja1pcq12T9cvcRitr57RED1CRiQGo7SYZk-3GeddsszXhJoNQsYMeXSzZOKamHUk3aNrfpGpoQuMm9BohqSJ_fubnaHPRpXVg_F3qjijO1RCtEBDnZo8UXFJ6NQmKlGbgjp9ujPU_8cEFdXHcKb-8Q8V1R2PI8PX>`_
     - `Speedup Multi-Core throughput graph for 2n-icx-e810cq-ip4-base-pdr <https://csit.fd.io/report/#eNrtlM8OgjAMxp8GL6aGFRAvHlTew8xRhAR1bpOoT-8wJIUYEg8mXjjsX35fu65fMusuhvaW6nWQbIN0G2Ba5X4Kos3cL6a2GIUIjdaA0cLvDNUkLQGeoVJ3EGF4JNSCViJUV5BNAZWOYRkfQCggV7YnPw5tjM5Nmxp3XeqPe5jmN8fU3z4gDRmGg7JYpstHTzNWLOulIckBvmJGjmyvmOGbWFUYeSJbPYmlvgvMlW80I6GG-d1D92jXqDR7K37qCk6ujLuC_3IlnlwZdyX-0pUkm50v5vT-yZLsBXP6Swk>`_
     - `MRR, NDR and PDR comparison for 2n-icx-e810cq-ip4-base <https://csit.fd.io/report/#eNrtVMsOgjAQ_Bq8mDW0gHjxoPIfppZVSQDrthLx6y2GuBBj4kVPHvrKzG6nM0mtOxFuLZbLIFkH6TqQaZH7KYhWU79QaWUUSmiMARnN_I6wRGURZA2FvoIIwwNKI3AhQn0G1eyhMDHM4x0IDeiO3cmPXVdTEXWt5aZv_XIPo_nFMepvHyENEoMjWUwzx3bAeSeW-YpQcYFXzJBDOxAzfhOz9qQqtMUNmepdYFx7oxkSetzftWaA9kal2YPx5VTq_J_KR6n0Rv0mFfNP5bNUzDOVJJvUJ6oeP1mS3QG2H0sT>`_
     - `Normalized throughput architecture comparison for 2n-[icx|clx]-e810cq-ip4-base-pdr <https://csit.fd.io/report/#eNrVk00OgjAQhU-DGzOGFhA3LlTuYUoZhKRibSsRT28hJANRF-500b98rzOvM6l1F4NHi2obJPsg3Qc8rQs_BdFu6RejLI9CDq3WwKOV3xlUKCwCb0CqO7AwPCHXDDcslFcQbQm1jmEd58AkoKv6kx95f0cXpg_ND2PolzxEi5sj6rPPSIuG4MwWyXTVTTSfzJJeGBR0wTsm5NBOzMzfRKrSiDPa-oEk9VUgLn2hCTE5j-86PaFjodJsUHzXlVr-UVfem_35riTZormY8_BneNpvhRpzJNkT6FzkMw>`_
     - `NICs comparison for 2n-icx-ip4-base-pdr <https://csit.fd.io/report/#eNrll99ugyAUh5_G3SxnESx1N7to53s0FI6rmbYMnKF7-qFrcmRmV7vReuG__A74wSckuvZi8eCwfknEPsn3Cc8rHU5JtnsMF1s7nqUcOmOAZ0_hzmKN0iHwM6jaA0vTN-SGKS_EVkJTewGV2cB2cwSmANtT_xSOY9_IaNv3zV9vfU9eRKn-bCkNr4-SDi2FEReVmdN1VPMnLTWQFiW1CMgUtehGNPGgqKq0skFXfSGVhmmgXIWppoipuP_2akbpbabyYqj4txerG7kcLz3tnXvBZ5aqD5BduQAtBLsOK9ro9-Vo6Wnv1sswUJ-zdPZLJSJdgY_ZL5IY9U6NcPEzTN8NX14JXpsZW_mNewi46zAz691rwroKJzPfwaaws7ciiofzxTbDv6QovgETwNPp>`_

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
|  1 | `VPP-2070                               | CSIT rdma 4c tests fail on 2n-zn2.                                                                        |
|    | <https://jira.fd.io/browse/VPP-2070>`_  | Memory alignment issue caused by a recent VPP merge.                                                      |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1876                              | 1n-aws: TRex NDR PDR ALL IP4 scale and L2 scale tests failing with 50% packet loss.                       |
|    | <https://jira.fd.io/browse/CSIT-1876>`_ | AWS perhaps changed its policy.                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1901                              | 3n-icx: negative ipackets on TB38 AVF 4c l2patch                                                          |
|    | <https://jira.fd.io/browse/CSIT-1901>`_ | Hardware or TRex issue.                                                                                   |
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
|  3 | `CSIT-1798                              | Investigate why vhost with testpmd in VM has two-band structure.                                          |
|    | <https://jira.fd.io/browse/CSIT-1798>`_ | Probably QEMU not allocating memory on the correct NUMA socket.                                           |
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
|  9 | `CSIT-1890                              | 3n-alt: Tests failing until 40Ge Interface comes up.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1890>`_ | A consequence of CSIT-1848 link slowness persisting over to other job runs.                               |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 10 | `CSIT-1849                              | 2n-skx, 2n-clx, 2n-icx: UDP 16m TPUT tests fail to create all sessions.                                   |
|    | <https://jira.fd.io/browse/CSIT-1849>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 11 | `CSIT-1864                              | 2n-clx: half of the packets lost on PDR tests.                                                            |
|    | <https://jira.fd.io/browse/CSIT-1864>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 12 | `CSIT-1877                              | 3n-tsh: all VM tests sometimes too slow to boot VM.                                                       |
|    | <https://jira.fd.io/browse/CSIT-1877>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 13 | `CSIT-1883                              | 3n-snr: All hwasync wireguard tests failing when trying to verify device.                                 |
|    | <https://jira.fd.io/browse/CSIT-1883>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 14 | `CSIT-1884                              | 2n-clx, 2n-icx: All NAT44DET NDR PDR IMIX over 1M sessions BIDIR tests failing to create enough sessions. |
|    | <https://jira.fd.io/browse/CSIT-1884>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| 15 | `CSIT-1886                              | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.                               |
|    | <https://jira.fd.io/browse/CSIT-1886>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Fixed
_____

Issues reported in previous releases which were fixed in this release:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1799                              | All NAT44-ED 16M sessions CPS scale tests fail while setting NAT44 address range.                         |
|    | <https://jira.fd.io/browse/CSIT-1799>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1827                              | 3n-icx, 3n-skx: all AVF crypto tests sporadically fail. 1518B with no traffic, IMIX with excessive        |
|    | <https://jira.fd.io/browse/CSIT-1827>`_ | packet loss.                                                                                              |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1835                              | 3n-icx: QUIC vppecho BPS tests failing on timeout when checking hoststack finished.                       |
|    | <https://jira.fd.io/browse/CSIT-1835>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1885                              | 3n-icx: 9000b ip4 ip6 l2 NDRPDR AVF tests are failing to forward traffic.                                 |
|    | <https://jira.fd.io/browse/CSIT-1885>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

.. _vpp_rca:

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1902                              | 3n-tsh: Investigate performance changes seen on some tests.                                               |
|    | <https://jira.fd.io/browse/CSIT-1902>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `VPP-2072                               | RSS is not deterministic on Intel-E822CQ NIC.                                                             |
|    | <https://jira.fd.io/browse/VPP-2072>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

---
title: "VPP Performance"
weight: 1
---

# Changes in {{< release_csit >}}

1. VPP PERFORMANCE TESTS
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
2. TEST FRAMEWORK
   - **CSIT test environment** version has not changed from ver. 11 used
     in previous release, see
     [Environment Versioning]({{< ref "infrastructure#Release Notes" >}}).
   - **CSIT PAPI optimizations for scale** got applied improving PAPI
     programming speed especially for large scale tests. VAT has been
     now completely deprecated from CSIT.
   - **General Code Housekeeping**: Ongoing code optimizations and bug
     fixes.
3. PRESENTATION AND ANALYTICS LAYER
   - [Performance dashboard](https://csit.fd.io/) got updated with
     addition of VPP telemetry trending across all VPP tests. A number
     of code and AWS resource usage optimizations got applied to the
     data processing pipeline and UI frontend and backend.
   - Examples of release iterative data visualisation:

     - [Packet throughput 2n-icx-e810cq-ip4-base-scale-pdr](https://csit.fd.io/report/#eNrdVcluwjAQ_Zr0ggbZDml64QDkP5BxhhJlwYxNVPr1OAhpYiGO7cEHb3pv1qeRnT8T7h1266zYZuU2U2VThy3LN4twUOdULhSM1oLKl-FG2KF2CGqAxvyAFOIblZX4JYW5gB6P0NgVfK4OIA2gP02vsA6Tja1pcq12T9cvcRitr57RED1CRiQGo7SYZk-3GeddsszXhJoNQsYMeXSzZOKamHUk3aNrfpGpoQuMm9BohqSJ_fubnaHPRpXVg_F3qjijO1RCtEBDnZo8UXFJ6NQmKlGbgjp9ujPU_8cEFdXHcKb-8Q8V1R2PI8PX)
     - [Speedup Multi-Core throughput graph for 2n-icx-e810cq-ip4-base-pdr](https://csit.fd.io/report/#eNrtlM8OgjAMxp8GL6aGFRAvHlTew8xRhAR1bpOoT-8wJIUYEg8mXjjsX35fu65fMusuhvaW6nWQbIN0G2Ba5X4Kos3cL6a2GIUIjdaA0cLvDNUkLQGeoVJ3EGF4JNSCViJUV5BNAZWOYRkfQCggV7YnPw5tjM5Nmxp3XeqPe5jmN8fU3z4gDRmGg7JYpstHTzNWLOulIckBvmJGjmyvmOGbWFUYeSJbPYmlvgvMlW80I6GG-d1D92jXqDR7K37qCk6ujLuC_3IlnlwZdyX-0pUkm50v5vT-yZLsBXP6Swk>)
     - [MRR, NDR and PDR comparison for 2n-icx-e810cq-ip4-base](https://csit.fd.io/report/#eNrtVMsOgjAQ_Bq8mDW0gHjxoPIfppZVSQDrthLx6y2GuBBj4kVPHvrKzG6nM0mtOxFuLZbLIFkH6TqQaZH7KYhWU79QaWUUSmiMARnN_I6wRGURZA2FvoIIwwNKI3AhQn0G1eyhMDHM4x0IDeiO3cmPXVdTEXWt5aZv_XIPo_nFMepvHyENEoMjWUwzx3bAeSeW-YpQcYFXzJBDOxAzfhOz9qQqtMUNmepdYFx7oxkSetzftWaA9kal2YPx5VTq_J_KR6n0Rv0mFfNP5bNUzDOVJJvUJ6oeP1mS3QG2H0sT>)
     - [Normalized throughput architecture comparison for 2n-[icx|clx]-e810cq-ip4-base-pdr](https://csit.fd.io/report/#eNrVk00OgjAQhU-DGzOGFhA3LlTuYUoZhKRibSsRT28hJANRF-500b98rzOvM6l1F4NHi2obJPsg3Qc8rQs_BdFu6RejLI9CDq3WwKOV3xlUKCwCb0CqO7AwPCHXDDcslFcQbQm1jmEd58AkoKv6kx95f0cXpg_ND2PolzxEi5sj6rPPSIuG4MwWyXTVTTSfzJJeGBR0wTsm5NBOzMzfRKrSiDPa-oEk9VUgLn2hCTE5j-86PaFjodJsUHzXlVr-UVfem_35riTZormY8_BneNpvhRpzJNkT6FzkMw>)
     - [NICs comparison for 2n-icx-ip4-base-pdr](https://csit.fd.io/report/#eNrll99ugyAUh5_G3SxnESx1N7to53s0FI6rmbYMnKF7-qFrcmRmV7vReuG__A74wSckuvZi8eCwfknEPsn3Cc8rHU5JtnsMF1s7nqUcOmOAZ0_hzmKN0iHwM6jaA0vTN-SGKS_EVkJTewGV2cB2cwSmANtT_xSOY9_IaNv3zV9vfU9eRKn-bCkNr4-SDi2FEReVmdN1VPMnLTWQFiW1CMgUtehGNPGgqKq0skFXfSGVhmmgXIWppoipuP_2akbpbabyYqj4txerG7kcLz3tnXvBZ5aqD5BduQAtBLsOK9ro9-Vo6Wnv1sswUJ-zdPZLJSJdgY_ZL5IY9U6NcPEzTN8NX14JXpsZW_mNewi46zAz691rwroKJzPfwaaws7ciiofzxTbDv6QovgETwNPp>)

# Known Issues

Editing Note: below listed known issues need to be updated to reflect the
current state as tracked on
[CSIT TestFailuresTracking wiki](https://wiki.fd.io/view/CSIT/TestFailuresTracking).

## New

 **#** | **JiraID**                                       | **Issue Description**
-------|--------------------------------------------------|------------------------------------------------------
 1     | [CSIT-1890](https://jira.fd.io/browse/CSIT-1890) | 3n-alt: Tests failing until 40Ge Interface comes up.


## Previous

Issues reported in previous releases which still affect the current results.

 **#** | **JiraID**                                                                                      | **Issue Description**
-------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 1     | [CSIT-1782](https://jira.fd.io/browse/CSIT-1782)                                                | Multicore AVF tests are failing when trying to create interface. Frequency is reduced by CSIT workaround, but occasional failures do still happen.
 2     | [CSIT-1785](https://jira.fd.io/browse/CSIT-1785) [VPP-1972](https://jira.fd.io/browse/VPP-1972) | NAT44ED tests failing to establish all TCP sessions. At least for max scale, in allotted time (limited by session 500s timeout) due to worse slow path performance than previously measured and calibrated for. CSIT removed the max scale NAT tests to avoid this issue.
 3     | [CSIT-1799](https://jira.fd.io/browse/CSIT-1799)                                                | All NAT44-ED 16M sessions CPS scale tests fail while setting NAT44 address range.
 4     | [CSIT-1800](https://jira.fd.io/browse/CSIT-1800)                                                | All Geneve L3 mode scale tests (1024 tunnels) are failing.
 5     | [CSIT-1801](https://jira.fd.io/browse/CSIT-1801)                                                | 9000B payload frames not forwarded over tunnels due to violating supported Max Frame Size (VxLAN, LISP,
 6     | [CSIT-1802](https://jira.fd.io/browse/CSIT-1802)                                                | all testbeds: AF-XDP - NDR tests failing from time to time.
 7     | [CSIT-1804](https://jira.fd.io/browse/CSIT-1804)                                                | All testbeds: NDR tests failing from time to time.
 8     | [CSIT-1808](https://jira.fd.io/browse/CSIT-1808)                                                | All tests with 9000B payload frames not forwarded over memif interfaces.
 9     | [CSIT-1827](https://jira.fd.io/browse/CSIT-1827)                                                | 3n-icx, 3n-skx: all AVF crypto tests sporadically fail. 1518B with no traffic, IMIX with excessive
 10    | [CSIT-1835](https://jira.fd.io/browse/CSIT-1835)                                                | 3n-icx: QUIC vppecho BPS tests failing on timeout when checking hoststack finished.
 11    | [CSIT-1849](https://jira.fd.io/browse/CSIT-1849)                                                | 2n-skx, 2n-clx, 2n-icx: UDP 16m TPUT tests fail to create all sessions.
 12    | [CSIT-1864](https://jira.fd.io/browse/CSIT-1864)                                                | 2n-clx: half of the packets lost on PDR tests.
 13    | [CSIT-1877](https://jira.fd.io/browse/CSIT-1877)                                                | 3n-tsh: all VM tests failing to boot VM.
 14    | [CSIT-1883](https://jira.fd.io/browse/CSIT-1883)                                                | 3n-snr: All hwasync wireguard tests failing when trying to verify device.
 15    | [CSIT-1884](https://jira.fd.io/browse/CSIT-1884)                                                | 2n-clx, 2n-icx: All NAT44DET NDR PDR IMIX over 1M sessions BIDIR tests failing to create enough sessions.
 16    | [CSIT-1885](https://jira.fd.io/browse/CSIT-1885)                                                | 3n-icx: 9000b ip4 ip6 l2 NDRPDR AVF tests are failing to forward traffic.
 17    | [CSIT-1886](https://jira.fd.io/browse/CSIT-1886)                                                | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.

## Fixed

Issues reported in previous releases which were fixed in this release:

 **#** | **JiraID**                                       | **Issue Description**
-------|--------------------------------------------------|---------------------------------------------------------------------
 1     | [CSIT-1868](https://jira.fd.io/browse/CSIT-1868) | 2n-clx: ALL ldpreload-nginx tests fails when trying to start nginx.
 2     | [CSIT-1871](https://jira.fd.io/browse/CSIT-1871) | 3n-snr: 25GE interface between SUT and TG/TRex goes down randomly.

# Root Cause Analysis for Performance Changes

List of RCAs in {{< release_csit >}} for VPP performance changes:

 **#** | **JiraID**                                       | **Issue Description**
-------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------
 1     | [CSIT-1887](https://jira.fd.io/browse/CSIT-1887) | rls2210 RCA: ASTF tests TRex upgrade decreased TRex performance. NAT results not affected, except on Denverton due to interference from VPP-2010.
 2     | [CSIT-1888](https://jira.fd.io/browse/CSIT-1888) | rls2210 RCA: testbed differences, especially for ipsec. Not caused by VPP code nor CSIT code. Most probable cause is clang-14 behavior.
 3     | [CSIT-1889](https://jira.fd.io/browse/CSIT-1889) | rls2210 RCA: policy-outbound-nocrypto. When VPP added spd fast path matching (Gerrit 36097), it decreased MRR of the corresponding tests, at least on 3-alt.

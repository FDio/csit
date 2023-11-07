---
title: "VPP Performance"
weight: 1
---

# CSIT 23.10 - VPP Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 13, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
   - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
   - **Trending**: Ndrpdr tests use newer code (MLRsearch 1.2.1) and configuration,
     gaining more stability and speed. Release results still use the old code
     to keep comparability with RC1 and RC2 results.
2. VPP PERFORMANCE TESTS
   - Added 2n-c6in testbed.
3. PRESENTATION AND ANALYTICS LAYER
   - [Performance dashboard](https://csit.fd.io/) got updated with graphs
     presenting bandwidth in bits per second for MRR and NDRPDR tests.

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    |                                                  |

## Previous

Issues reported in previous releases which still affect the current results.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   | [CSIT-1782](https://jira.fd.io/browse/CSIT-1782) | Multicore AVF tests are failing when trying to create interface. Frequency is reduced by CSIT workaround, but occasional failures do still happen.
  2   | [CSIT-1785](https://jira.fd.io/browse/CSIT-1785) | NAT44ED tests failing to establish all TCP sessions. At least for max scale, in allotted time (limited by session 500s timeout) due to worse slow path performance than previously measured and calibrated for. CSIT removed the max scale NAT tests to avoid this issue.
  3   | [CSIT-1795](https://jira.fd.io/browse/CSIT-1795) | Ocassionally not all DET44 sessions have been established: 4128767 != 4128768
  4   | [CSIT-1802](https://jira.fd.io/browse/CSIT-1802) | all testbeds: AF-XDP - NDR tests failing from time to time on small loss
  5   | [CSIT-1804](https://jira.fd.io/browse/CSIT-1804) | All testbeds: NDR tests failing from time to time.
  6   | [CSIT-1808](https://jira.fd.io/browse/CSIT-1808) | All tests with 9000B payload frames not forwarded over memif interfaces.
  7   | [CSIT-1827](https://jira.fd.io/browse/CSIT-1827) | 3n-icx, 3n-skx: all AVF crypto tests sporadically fail. 1518B with no traffic, IMIX with excessive packet loss
  8   | [CSIT-1849](https://jira.fd.io/browse/CSIT-1849) | 2n-skx, 2n-clx, 2n-icx: UDP 16m TPUT tests fail to create all sessions.
  9   | [CSIT-1864](https://jira.fd.io/browse/CSIT-1864) | 2n-clx: half of the packets lost on PDR tests.
 10   | [CSIT-1881](https://jira.fd.io/browse/CSIT-1881) | 2n-icx: NFV density tests ocassionally breaks VPP which fails to start.
 11   | [CSIT-1883](https://jira.fd.io/browse/CSIT-1883) | 3n-snr: All hwasync wireguard tests failing when trying to verify device.
 12   | [CSIT-1886](https://jira.fd.io/browse/CSIT-1886) | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.
 13   | [CSIT-1892](https://jira.fd.io/browse/CSIT-1892) | 3n-alt: two-band structure of ipsec and vxlan.
 14   | [CSIT-1896](https://jira.fd.io/browse/CSIT-1896) | Depending on topology, l3fwd avoids dut-dut link.
 15   | [CSIT-1901](https://jira.fd.io/browse/CSIT-1901) | 3n-icx: negative ipackets on TB38 AVF 4c l2patch.
 16   | [CSIT-1904](https://jira.fd.io/browse/CSIT-1904) | DPDK 23.03 testpmd startup fails on some testbeds.
 17   | [CSIT-1906](https://jira.fd.io/browse/CSIT-1906) | Zero traffic with cx7 rdma. Cause not know yet, trending uses mlx5-core for cx7 and cx6.
 18   | [VPP-2077](https://jira.fd.io/browse/VPP-2077)   | IP fragmentation: running_fragment_id is not thread safe. Causes reduced performance and failures in gtpu reassembly tests.
 19   | [CSIT-1914](https://jira.fd.io/browse/CSIT-1914) | TRex does not produce latency data on ICE NICs.
 20   | [CSIT-1915](https://jira.fd.io/browse/CSIT-1915) | 2n-icx testbeds to not have the same performance
 21   | [CSIT-1916](https://jira.fd.io/browse/CSIT-1916) | Poor CPU scaling on 2n-zn2 RDMA.
 22   | [CSIT-1917](https://jira.fd.io/browse/CSIT-1917) | TRex STL performance is unstable at high pps due to unsent packets.
 23   | [CSIT-1922](https://jira.fd.io/browse/CSIT-1922) | 2n-tx2: af_xdp mrr failures. On other testbeds MRR regressions and PDR failures.
 24   | [CSIT-1923](https://jira.fd.io/browse/CSIT-1923) | 3n-icx, 3n-snr: first few swasync scheduler tests timing out in runtime stat.
 25   | [CSIT-1924](https://jira.fd.io/browse/CSIT-1924) | l3fwd error in 200Ge2P1Cx7Veat-Mlx5 test with 9000B.

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1800](https://jira.fd.io/browse/CSIT-1800) | All Geneve L3 mode scale tests (1024 tunnels) are failing.
 2    | [CSIT-1801](https://jira.fd.io/browse/CSIT-1801) | 9000B payload frames not forwarded over tunnels due to violating supported Max Frame Size (VxLAN, LISP, SRv6)
 3    | [CSIT-1809](https://jira.fd.io/browse/CSIT-1809) | All tests with 9000B payload frames not forwarded over vhost-user interfaces.
 4    | [CSIT-1884](https://jira.fd.io/browse/CSIT-1884) | 2n-clx, 2n-icx: All NAT44DET NDR PDR IMIX over 1M sessions BIDIR tests failing to create enough sessions.
 5    | [CSIT-1885](https://jira.fd.io/browse/CSIT-1885) | 3n-icx: 9000b ip4 ip6 l2 NDRPDR AVF tests are failing to forward traffic.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 23.10 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions not limit usefulness of CSIT testing.
So even if they are not fixed (e.g. when the regression is an expected
consequence of added functionality), they will not be re-listed in the next
release report.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1933](https://jira.fd.io/browse/CSIT-1933) | Regresion in nat44ed tests around 2023-09-07
 2    | [CSIT-1934](https://jira.fd.io/browse/CSIT-1934) | rls 2310: Regression in nginx rps around 2023-10-09
 3    | [CSIT-1935](https://jira.fd.io/browse/CSIT-1935) | rls 2310: Zero traffic reported in udpquic tests

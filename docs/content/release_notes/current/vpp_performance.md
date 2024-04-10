---
title: "VPP Performance"
weight: 1
---

# CSIT 24.02 - VPP Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 14, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
   - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
   - **Trending and release testing**: Ndrpdr tests use newer code
     (MLRsearch 1.2.1) and configuration, gaining more stability and speed.
1. VPP PERFORMANCE TESTS
   - Added 2n-c7gn and 3n-icxd testbeds.
2. PRESENTATION AND ANALYTICS LAYER
   - [Performance dashboard](https://csit.fd.io/) got updated with the
     possibility to [search in tests](https://csit.fd.io/search/).
   - [Per Release Performance Comparisons](https://csit.fd.io/comparisons/) got
     updated with the function removing extreme outliers from data presented in
     the comparison table.

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   | [CSIT-1845](https://jira.fd.io/browse/CSIT-1845) | AVF 9000B any ndrpdr test may start failing due to packets not arriving in one or both directions.
  2   | [CSIT-1946](https://jira.fd.io/browse/CSIT-1946) | Ipsec hwasync fails with large scale and multiple queues.
  3   | [CSIT-1947](https://jira.fd.io/browse/CSIT-1947) | VPP crash in udp nat avf 4c tests.
  4   | [CSIT-1948](https://jira.fd.io/browse/CSIT-1948) | NICs do not consistently distribute tunnels over RXQs depending on model or plugin.
  5   | [CSIT-1950](https://jira.fd.io/browse/CSIT-1950) | 9000B tests with high encap overhead see fragmented packets.
  6   | [CSIT-1951](https://jira.fd.io/browse/CSIT-1951) | Combination of AVF and vhost drops all 9000B packets.
  7   | [CSIT-1954](https://jira.fd.io/browse/CSIT-1954) | 3n-icx: 9000B AVF ip6 tests show zero traffic in one direction due to no free tx slots.

## Previous

Issues reported in previous releases which still affect the current results.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   | [CSIT-1782](https://jira.fd.io/browse/CSIT-1782) | Multicore AVF tests are failing when trying to create interface. Frequency is reduced by CSIT workaround, but occasional failures do still happen.
  2   | [CSIT-1785](https://jira.fd.io/browse/CSIT-1785) | NAT44ED tests failing to establish all TCP sessions. At least for max scale, in allotted time (limited by session 500s timeout) due to worse slow path performance than previously measured and calibrated for. CSIT removed the max scale NAT tests to avoid this issue.
  3   | [CSIT-1795](https://jira.fd.io/browse/CSIT-1795) | Ocassionally not all DET44 sessions have been established: 4128767 != 4128768
  4   | [CSIT-1802](https://jira.fd.io/browse/CSIT-1802) | All testbeds: AF-XDP - NDR tests failing from time to time on small loss.
  5   | [CSIT-1804](https://jira.fd.io/browse/CSIT-1804) | 3n-tsh: NDR fails on ierrors.
  6   | [CSIT-1849](https://jira.fd.io/browse/CSIT-1849) | 2n-clx, 2n-icx: UDP 16m TPUT tests fail to create all sessions.
  7   | [CSIT-1881](https://jira.fd.io/browse/CSIT-1881) | 2n-icx: NFV density tests ocassionally breaks VPP which fails to start.
  8   | [CSIT-1886](https://jira.fd.io/browse/CSIT-1886) | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.
  9   | [CSIT-1892](https://jira.fd.io/browse/CSIT-1892) | 3n-alt: Unexpected two-band structure of ipsec and vxlan.
 10   | [CSIT-1896](https://jira.fd.io/browse/CSIT-1896) | Depending on topology, l3fwd avoids dut-dut link.
 11   | [CSIT-1901](https://jira.fd.io/browse/CSIT-1901) | 3n-icx: Negative ipackets on TB38 AVF 4c l2patch.
 12   | [CSIT-1904](https://jira.fd.io/browse/CSIT-1904) | DPDK 23.03 testpmd startup fails on some testbeds.
 13   | [CSIT-1906](https://jira.fd.io/browse/CSIT-1906) | Zero traffic with cx7 rdma. Testing migrated to mlx5-core on all Mellanox NICs.
 14   | [VPP-2077](https://jira.fd.io/browse/VPP-2077)   | IP fragmentation: running_fragment_id is not thread safe. Causes reduced performance and failures in gtpu reassembly tests.
 15   | [CSIT-1914](https://jira.fd.io/browse/CSIT-1914) | TRex does not produce latency data on ICE NICs.
 16   | [CSIT-1915](https://jira.fd.io/browse/CSIT-1915) | The 2n-icx testbeds to not have the same performance.
 17   | [CSIT-1916](https://jira.fd.io/browse/CSIT-1916) | Poor CPU scaling on 2n-zn2 RDMA.
 18   | [CSIT-1917](https://jira.fd.io/browse/CSIT-1917) | TRex STL performance is unstable at high pps due to unsent packets.
 19   | [CSIT-1921](https://jira.fd.io/browse/CSIT-1921) | Two-band structure in SRv6, causes PDR failure in rare cases.
 20   | [CSIT-1922](https://jira.fd.io/browse/CSIT-1922) | 2n-tx2: AF_XDP MRR failures. On other testbeds MRR regressions and PDR failures.
 21   | [CSIT-1924](https://jira.fd.io/browse/CSIT-1924) | An l3fwd error in 200Ge2P1Cx7Veat-Mlx5 test with 9000B.
 22   | [CSIT-1935](https://jira.fd.io/browse/CSIT-1935) | Zero traffic reported in udpquic tests due to session close errors.
 23   | [CSIT-1936](https://jira.fd.io/browse/CSIT-1936) | TRex occasionally sees link down in L2 perf tests.
 24   | [CSIT-1937](https://jira.fd.io/browse/CSIT-1937) | Small but frequent loss in ASTF UDP on cx7 mlx5.
 25   | [CSIT-1938](https://jira.fd.io/browse/CSIT-1938) | 3n-alt: High scale ipsec policy tests may crash VPP.
 26   | [CSIT-1939](https://jira.fd.io/browse/CSIT-1939) | 3na-spr, 2n-zn2: VPP fails to start in first test cases.
 27   | [CSIT-1941](https://jira.fd.io/browse/CSIT-1941) | TRex may wrongly detect link bandwidth.
 28   | [CSIT-1942](https://jira.fd.io/browse/CSIT-1942) | 3nb-spr hoststack: Interface not up after first test.
 29   | [CSIT-1943](https://jira.fd.io/browse/CSIT-1943) | IMIX 4c tests may fail PDR due to ~10% loss.
 30   | [CSIT-1944](https://jira.fd.io/browse/CSIT-1944) | Memif LXC: unrecognized option '--no-validate'.
 31   | [VPP-2090](https://jira.fd.io/browse/VPP-2090)   | MRR < PDR: DPDK plugin with MLX5 driver does not read full queue.
 32   | [VPP-2091](https://jira.fd.io/browse/VPP-2091)   | Memif crashes with jumbo frames.

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   | [CSIT-1883](https://jira.fd.io/browse/CSIT-1883) | 3n-snr: All hwasync wireguard tests failing when trying to verify device.
  2   | [CSIT-1940](https://jira.fd.io/browse/CSIT-1940) | Hardware acceleration does not work yet.
  3   | [VPP-2087](https://jira.fd.io/browse/VPP-2087)   | VPP crash and other symptoms in tests with AVF, jumbo packets.
  4   | [VPP-2088](https://jira.fd.io/browse/VPP-2088)   | virtio: Bad CLI argument parsing introduced with tx-queue-size.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 24.02 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   | [VPP-2099](https://jira.fd.io/browse/VPP-2099)   | Bump of rdma-core to 49.0 decreased performance.

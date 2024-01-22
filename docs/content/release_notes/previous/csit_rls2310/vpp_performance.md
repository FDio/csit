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
  1   | [CSIT-1935](https://jira.fd.io/browse/CSIT-1935) | Zero traffic reported in udpquic tests due to session close errors.
  2   | [CSIT-1936](https://jira.fd.io/browse/CSIT-1936) | TRex occasionally sees link down in L2 perf tests.
  3   | [CSIT-1937](https://jira.fd.io/browse/CSIT-1937) | Small but frequent loss in ASTF UDP on cx7 mlx5.
  4   | [CSIT-1938](https://jira.fd.io/browse/CSIT-1938) | 3n-alt: High scale ipsec policy tests may crash VPP.
  5   | [CSIT-1939](https://jira.fd.io/browse/CSIT-1939) | 3na-spr, 2n-zn2: VPP fails to start in first test cases.
  6   | [CSIT-1940](https://jira.fd.io/browse/CSIT-1940) | Hardware acceleration does not work yet.
  7   | [CSIT-1941](https://jira.fd.io/browse/CSIT-1941) | TRex may wrongly detect link bandwidth.
  8   | [CSIT-1942](https://jira.fd.io/browse/CSIT-1942) | 3nb-spr hoststack: Interface not up after first test.
  9   | [CSIT-1943](https://jira.fd.io/browse/CSIT-1943) | IMIX 4c tests may fail PDR due to ~10% loss.
 10   | [VPP-2087](https://jira.fd.io/browse/VPP-2087)   | VPP crash and other symptoms in tests with AVF, jumbo packets.
 11   | [VPP-2088](https://jira.fd.io/browse/VPP-2088)   | virtio: Bad CLI argument parsing introduced with tx-queue-size.
 12   | [CSIT-1944](https://jira.fd.io/browse/CSIT-1944) | Memif LXC: unrecognized option '--no-validate'.
 13   | [CSIT-1945](https://jira.fd.io/browse/CSIT-1945) | Some srv6 9000B tests crash VPP.
 14   | [VPP-2090](https://jira.fd.io/browse/VPP-2090)   | MRR < PDR: DPDK plugin with MLX5 driver does not read full queue.
 15   | [VPP-2091](https://jira.fd.io/browse/VPP-2091)   | Memif crashes with jumbo frames.

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
  8   | [CSIT-1883](https://jira.fd.io/browse/CSIT-1883) | 3n-snr: All hwasync wireguard tests failing when trying to verify device.
  9   | [CSIT-1886](https://jira.fd.io/browse/CSIT-1886) | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.
 10   | [CSIT-1892](https://jira.fd.io/browse/CSIT-1892) | 3n-alt: Unexpected two-band structure of ipsec and vxlan.
 11   | [CSIT-1896](https://jira.fd.io/browse/CSIT-1896) | Depending on topology, l3fwd avoids dut-dut link.
 12   | [CSIT-1901](https://jira.fd.io/browse/CSIT-1901) | 3n-icx: Negative ipackets on TB38 AVF 4c l2patch.
 13   | [CSIT-1904](https://jira.fd.io/browse/CSIT-1904) | DPDK 23.03 testpmd startup fails on some testbeds.
 14   | [CSIT-1906](https://jira.fd.io/browse/CSIT-1906) | Zero traffic with cx7 rdma. Testing migrated to mlx5-core on all Mellanox NICs.
 15   | [VPP-2077](https://jira.fd.io/browse/VPP-2077)   | IP fragmentation: running_fragment_id is not thread safe. Causes reduced performance and failures in gtpu reassembly tests.
 16   | [CSIT-1914](https://jira.fd.io/browse/CSIT-1914) | TRex does not produce latency data on ICE NICs.
 17   | [CSIT-1915](https://jira.fd.io/browse/CSIT-1915) | The 2n-icx testbeds to not have the same performance.
 18   | [CSIT-1916](https://jira.fd.io/browse/CSIT-1916) | Poor CPU scaling on 2n-zn2 RDMA.
 19   | [CSIT-1917](https://jira.fd.io/browse/CSIT-1917) | TRex STL performance is unstable at high pps due to unsent packets.
 20   | [CSIT-1921](https://jira.fd.io/browse/CSIT-1921) | Two-band structure in SRv6, causes PDR failure in rare cases.
 21   | [CSIT-1922](https://jira.fd.io/browse/CSIT-1922) | 2n-tx2: AF_XDP MRR failures. On other testbeds MRR regressions and PDR failures.
 22   | [CSIT-1924](https://jira.fd.io/browse/CSIT-1924) | An l3fwd error in 200Ge2P1Cx7Veat-Mlx5 test with 9000B.

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   | [CSIT-1800](https://jira.fd.io/browse/CSIT-1800) | All Geneve L3 mode scale tests (1024 tunnels) are failing.
  2   | [CSIT-1801](https://jira.fd.io/browse/CSIT-1801) | 9000B payload frames not forwarded over tunnels due to violating supported Max Frame Size (VxLAN, LISP, SRv6).
  3   | [CSIT-1809](https://jira.fd.io/browse/CSIT-1809) | All tests with 9000B payload frames not forwarded over vhost-user interfaces.
  4   | [CSIT-1864](https://jira.fd.io/browse/CSIT-1864) | 2n-clx: Half of the packets lost on PDR tests.
  5   | [CSIT-1884](https://jira.fd.io/browse/CSIT-1884) | 2n-clx, 2n-icx: All NAT44DET NDR PDR IMIX over 1M sessions BIDIR tests failing to create enough sessions.
  6   | [CSIT-1923](https://jira.fd.io/browse/CSIT-1923) | 3n-icx, 3n-snr: First few swasync scheduler tests timing out in runtime stat.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 23.10 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1933](https://jira.fd.io/browse/CSIT-1933) | Regression in nat44ed tests around 2023-09-07.
 2    | [CSIT-1934](https://jira.fd.io/browse/CSIT-1934) | Regression in nginx rps around 2023-10-09.

---
title: "VPP Performance"
weight: 1
---

# CSIT 23.06 - VPP Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 12, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
2. VPP PERFORMANCE TESTS
   - Added tests for IP packet reassembly (using IPsec or GTPU).
   - Existing IPsec fastpath tests converted to apply optimizations also
     on inbound (previously only on outbound).

# Known Issues

These are issues that cause test failures
or otherwise limit usefulness of CSIT testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1892](https://jira.fd.io/browse/CSIT-1892) | 3n-alt: two-band structure of ipsec and vxlan.
 2    | [CSIT-1896](https://jira.fd.io/browse/CSIT-1896) | Depending on topology, l3fwd avoids dut-dut link.
 3    | [CSIT-1901](https://jira.fd.io/browse/CSIT-1901) | 3n-icx: negative ipackets on TB38 AVF 4c l2patch.
 4    | [CSIT-1904](https://jira.fd.io/browse/CSIT-1904) | DPDK 23.03 testpmd startup fails on some testbeds.
 5    | [CSIT-1906](https://jira.fd.io/browse/CSIT-1906) | Zero traffic with cx7 rdma. Cause not know yet, trending uses mlx5-core for cx7 and cx6.
 6    | [VPP-2077](https://jira.fd.io/browse/VPP-2077)   | IP fragmentation: running_fragment_id is not thread safe. Causes reduced performance and failures in gtpu reassembly tests.
 7    | [CSIT-1914](https://jira.fd.io/browse/CSIT-1914) | TRex does not produce latency data on ICE NICs.
 8    | [CSIT-1915](https://jira.fd.io/browse/CSIT-1915) | 2n-icx testbeds to not have the same performance
 9    | [CSIT-1916](https://jira.fd.io/browse/CSIT-1916) | Poor CPU scaling on 2n-zn2 RDMA.
 10   | [CSIT-1917](https://jira.fd.io/browse/CSIT-1917) | TRex STL performance is unstable at high pps due to unsent packets.
 11   | [CSIT-1922](https://jira.fd.io/browse/CSIT-1922) | 2n-tx2: af_xdp mrr failures.
 12   | [CSIT-1923](https://jira.fd.io/browse/CSIT-1923) | 3n-icx, 3n-snr: first few swasync scheduler tests timing out in runtime stat.
 13   | [CSIT-1924](https://jira.fd.io/browse/CSIT-1924) | l3fwd error in 200Ge2P1Cx7Veat-Mlx5 test with 9000B.

## Previous

Issues reported in previous releases which still affect the current results.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1782](https://jira.fd.io/browse/CSIT-1782) | Multicore AVF tests are failing when trying to create interface. Frequency is reduced by CSIT workaround, but occasional failures do still happen.
 2    | [CSIT-1785](https://jira.fd.io/browse/CSIT-1785) | NAT44ED tests failing to establish all TCP sessions. At least for max scale, in allotted time (limited by session 500s timeout) due to worse slow path performance than previously measured and calibrated for. CSIT removed the max scale NAT tests to avoid this issue.
 3    | [CSIT-1795](https://jira.fd.io/browse/CSIT-1795) | Ocassionally not all DET44 sessions have been established: 4128767 != 4128768
 4    | [CSIT-1800](https://jira.fd.io/browse/CSIT-1800) | All Geneve L3 mode scale tests (1024 tunnels) are failing.
 5    | [CSIT-1801](https://jira.fd.io/browse/CSIT-1801) | 9000B payload frames not forwarded over tunnels due to violating supported Max Frame Size (VxLAN, LISP, SRv6)
 6    | [CSIT-1802](https://jira.fd.io/browse/CSIT-1802) | all testbeds: AF-XDP - NDR tests failing from time to time.
 7    | [CSIT-1804](https://jira.fd.io/browse/CSIT-1804) | All testbeds: NDR tests failing from time to time.
 8    | [CSIT-1808](https://jira.fd.io/browse/CSIT-1808) | All tests with 9000B payload frames not forwarded over memif interfaces.
 9    | [CSIT-1809](https://jira.fd.io/browse/CSIT-1809) | All tests with 9000B payload frames not forwarded over vhost-user interfaces.
 10   | [CSIT-1827](https://jira.fd.io/browse/CSIT-1827) | 3n-icx, 3n-skx: all AVF crypto tests sporadically fail. 1518B with no traffic, IMIX with excessive packet loss
 11   | [CSIT-1849](https://jira.fd.io/browse/CSIT-1849) | 2n-skx, 2n-clx, 2n-icx: UDP 16m TPUT tests fail to create all sessions.
 12   | [CSIT-1864](https://jira.fd.io/browse/CSIT-1864) | 2n-clx: half of the packets lost on PDR tests.
 13   | [CSIT-1881](https://jira.fd.io/browse/CSIT-1881) | 2n-icx: NFV density tests ocassionally breaks VPP which fails to start.
 14   | [CSIT-1883](https://jira.fd.io/browse/CSIT-1883) | 3n-snr: All hwasync wireguard tests failing when trying to verify device.
 15   | [CSIT-1884](https://jira.fd.io/browse/CSIT-1884) | 2n-clx, 2n-icx: All NAT44DET NDR PDR IMIX over 1M sessions BIDIR tests failing to create enough sessions.
 16   | [CSIT-1885](https://jira.fd.io/browse/CSIT-1885) | 3n-icx: 9000b ip4 ip6 l2 NDRPDR AVF tests are failing to forward traffic.
 17   | [CSIT-1886](https://jira.fd.io/browse/CSIT-1886) | 3n-icx: Wireguard tests with 100 and more tunnels are failing PDR criteria.

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1799](https://jira.fd.io/browse/CSIT-1799) | All NAT44-ED 16M sessions CPS scale tests fail while setting NAT44 address range.
 2    | [CSIT-1890](https://jira.fd.io/browse/CSIT-1890) | 3n-alt: Tests failing until 40Ge Interface comes up. The fix for CSIT-1848 was enough to prevent this from happening.
 3    | [CSIT-1835](https://jira.fd.io/browse/CSIT-1835) | 3n-icx: QUIC vppecho BPS tests failing on timeout when checking hoststack finished.
 4    | [CSIT-1877](https://jira.fd.io/browse/CSIT-1877) | 3n-tsh: all VM tests failing to boot VM. Fixed by increasing the timeout.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 23.06 for VPP performance regressions.

Contrary to issues, these do not limit usefulness of CSIT testing.
So even if they are not fixed (e.g. when the regression is an expected
consequence of added functionality), they will not be re-listed in the next
release report.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1912](https://jira.fd.io/browse/CSIT-1912) | trending regression: l2scale around 2023-03-18.
 2    | [CSIT-1918](https://jira.fd.io/browse/CSIT-1918) | summarize performance consequences of ipsec changes.
 3    | [CSIT-1919](https://jira.fd.io/browse/CSIT-1919) | rls2306: find cause of wireguard regression.
 4    | [CSIT-1920](https://jira.fd.io/browse/CSIT-1920) | find cause of zn2 mlx5 memif regression near 2023-04-11.
 5    | [CSIT-1921](https://jira.fd.io/browse/CSIT-1921) | investigate two-band structure in SRv6.

---
title: "VPP Performance"
weight: 1
---

# CSIT 24.10 - VPP Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version 15 is used, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
   - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
2. VPP PERFORMANCE TESTS

3. PRESENTATION AND ANALYTICS LAYER
   - Max value on time axis has been set to utc.now

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|-------------------------------------------------------------------------
  1   | [CSIT-1968](https://jira.fd.io/browse/CSIT-1968) | 3n-icx: two testbeds behave differently in some ipsec tests with AVF.
  2   | [CSIT-1969](https://jira.fd.io/browse/CSIT-1969) | nsim scale: Transport endpoint is not connected.
  3   | [CSIT-1970](https://jira.fd.io/browse/CSIT-1970) | JSON export validation does not prevent EPL from consuming invalid data.
  4   | [CSIT-1971](https://jira.fd.io/browse/CSIT-1971) | Investigate two-band structure in nginx 2c cps tests.
  5   | [CSIT-1977](https://jira.fd.io/browse/CSIT-1977) | E810: Unsent packets at moderate load can fail soak.
  6   | [CSIT-1978](https://jira.fd.io/browse/CSIT-1978) | 3na-spr, 3nb-spr: Vhost tests cannot access testpmd.
  7   | [CSIT-1979](https://jira.fd.io/browse/CSIT-1979) | 3na-spr: Flow related ipsec tests fail on CX7.

## Previous

Issues reported in previous releases which still affect the current results.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  1   | [CSIT-1785](https://jira.fd.io/browse/CSIT-1785) | NAT44ED tests failing to establish all TCP sessions. At least for max scale, in allotted time (limited by session 500s timeout) due to worse slow path performance than previously measured and calibrated for. CSIT removed the max scale NAT tests to avoid this issue.
  2   | [CSIT-1795](https://jira.fd.io/browse/CSIT-1795) | Ocassionally not all DET44 sessions have been established: 4128767 != 4128768.
  3   | [CSIT-1802](https://jira.fd.io/browse/CSIT-1802) | All testbeds: AF-XDP - NDR tests failing from time to time on small loss.
  4   | [CSIT-1845](https://jira.fd.io/browse/CSIT-1845) | AVF 9000B any ndrpdr test may start failing due to packets not arriving in one or both directions.
  5   | [CSIT-1884](https://jira.fd.io/browse/CSIT-1884) | 2n-icx, 2n-spr: All NAT44DET IMIX large scale BIDIR tests fail to create enough sessions.
  6   | [CSIT-1886](https://jira.fd.io/browse/CSIT-1886) | 3n: Wireguard tests with 100 and more tunnels are failing PDR criteria.
  7   | [CSIT-1892](https://jira.fd.io/browse/CSIT-1892) | 3n-alt: Unexpected two-band structure of ipsec and vxlan.
  8   | [CSIT-1896](https://jira.fd.io/browse/CSIT-1896) | Depending on topology, l3fwd avoids dut-dut link.
  9   | [CSIT-1901](https://jira.fd.io/browse/CSIT-1901) | 2n-icx 3n-icx: Trex may report negative ipackets on high-performance AVF trial.
 10   | [CSIT-1904](https://jira.fd.io/browse/CSIT-1904) | 3n-alt: DPDK testpmd startup check fails on DUT2.
 11   | [CSIT-1906](https://jira.fd.io/browse/CSIT-1906) | Zero traffic with cx7 rdma. Testing migrated to mlx5-core on all Mellanox NICs.
 12   | [VPP-2077](https://jira.fd.io/browse/VPP-2077)   | IP fragmentation: running_fragment_id is not thread safe. Causes reduced performance and failures in gtpu reassembly tests.
 13   | [CSIT-1914](https://jira.fd.io/browse/CSIT-1914) | TRex does not produce latency data on ICE NICs.
 14   | [CSIT-1915](https://jira.fd.io/browse/CSIT-1915) | The 2n-icx testbeds do not have the same performance.
 15   | [CSIT-1916](https://jira.fd.io/browse/CSIT-1916) | Poor CPU scaling on 2n-zn2 RDMA.
 16   | [CSIT-1917](https://jira.fd.io/browse/CSIT-1917) | TRex STL performance is unstable at high pps due to unsent packets.
 17   | [CSIT-1922](https://jira.fd.io/browse/CSIT-1922) | AF_XDP MRR regressions and PDR failures. Affects subsequent tests, that is why we are not testing AF-XDP now.
 18   | [CSIT-1929](https://jira.fd.io/browse/CSIT-1929) | Lossy trials in nat udp mlx5 tests.
 19   | [CSIT-1935](https://jira.fd.io/browse/CSIT-1935) | Zero traffic reported in udpquic tests due to session close errors.
 20   | [CSIT-1936](https://jira.fd.io/browse/CSIT-1936) | TRex occasionally sees link down in E8xx (dpdk) tests.
 21   | [CSIT-1938](https://jira.fd.io/browse/CSIT-1938) | 3n-alt: High scale ipsec policy tests may crash VPP.
 22   | [CSIT-1941](https://jira.fd.io/browse/CSIT-1941) | TRex may wrongly detect link bandwidth.
 23   | [CSIT-1942](https://jira.fd.io/browse/CSIT-1942) | 3nb-spr hoststack: Interface not up after first test.
 24   | [VPP-2090](https://jira.fd.io/browse/VPP-2090)   | MRR < PDR: DPDK plugin with MLX5 driver does not read full queue.
 25   | [VPP-2091](https://jira.fd.io/browse/VPP-2091)   | Memif crashes VPP in container with jumbo frames.
 26   | [CSIT-1946](https://jira.fd.io/browse/CSIT-1946) | Ipsec hwasync fails with large scale and multiple queues.
 27   | [CSIT-1947](https://jira.fd.io/browse/CSIT-1947) | Rare VPP crash in nat avf tests.
 28   | [CSIT-1948](https://jira.fd.io/browse/CSIT-1948) | NICs do not consistently distribute tunnels over RXQs depending on model or plugin.
 29   | [CSIT-1950](https://jira.fd.io/browse/CSIT-1950) | 9000B tests with encap overhead and non-dpdk plugins see fragmented packets.
 30   | [CSIT-1951](https://jira.fd.io/browse/CSIT-1951) | Combination of AVF and vhost drops all 9000B packets.
 31   | [CSIT-1953](https://jira.fd.io/browse/CSIT-1953) | 3n-icx 3nb-spr: Failed to enable GTPU offload RX.
 32   | [VPP-2118](https://jira.fd.io/browse/VPP-2118)   | 3n spr: Unusable performance of ipsec tests with SHA_256_128.
 33   | [CSIT-1960](https://jira.fd.io/browse/CSIT-1960) | 2n-zn2: AVF xxv710 sometimes loses one direction of traffic, mostly with geneve.
 34   | [CSIT-1961](https://jira.fd.io/browse/CSIT-1961) | Some tests have too long ramp-up trials. Only for highest scale tests that shuld have been removed already.
 35   | [CSIT-1962](https://jira.fd.io/browse/CSIT-1962) | 3n-icx hoststack: Udpquicscale tests sometimes fail with various symptoms.
 36   | [CSIT-1963](https://jira.fd.io/browse/CSIT-1963) | 3n-icxd: Various symptoms pointing to hardware (cable/nic/driver) issues. Probably fixed on CSIT master already.
 37   | [CSIT-1964](https://jira.fd.io/browse/CSIT-1964) | 3nb-spr: Wireguardhw tests are likely to crash.
 38   | [VPP-2121](https://jira.fd.io/browse/VPP-2121)   | sw_interface_add_del_address: avf process node failed to reply in 5 seconds. Fixed only for iavf plugin.

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|-----------------------------------------------------------------------------------------------
  1   | [CSIT-1943](https://jira.fd.io/browse/CSIT-1943) | IMIX 4c tests may fail PDR due to ~10% loss. Fixed by DPDK upgrade.
  2   | [CSIT-1944](https://jira.fd.io/browse/CSIT-1944) | Memif LXC: unrecognized option '--no-validate'. Fixed in CSIT but also discontinued this test.
  3   | [CSIT-1966](https://jira.fd.io/browse/CSIT-1966) | 3n-snr: Increased heap size in ipsec policy tests prevents VPP from starting.
  4   | [CSIT-1967](https://jira.fd.io/browse/CSIT-1967) | 3na-spr: Unable to configure large MTU for 9000B tests.

Not listing issues that became unreproducible, e.g. by CSIT decomissioning older testbeds.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 24.10 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------
  1   | [CSIT-1980](https://jira.fd.io/browse/CSIT-1980) | 2n-zn2: Regression in l2xcbase around 2024-10-10.
  2   | [CSIT-1981](https://jira.fd.io/browse/CSIT-1981) | Ip6scale regression around early july 2024.

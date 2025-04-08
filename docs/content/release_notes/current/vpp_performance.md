---
title: "VPP Performance"
weight: 1
---

# CSIT 25.02 - VPP Performance

1. TEST FRAMEWORK
    - **CSIT test environment** version has been updated to ver. 17, see
      [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
        - Most notably, the tests are now running on Ubuntu 24.04.1.
        - Also iperf3 version got updated, affecting hoststack and GSO performance.
    - The testbeds 3n-alt and 3n-emr are out-of-service for 25.02 release.
    - HW related parts that are out-of-service for 25.02 release:
        - DSA.
    - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
2. VPP PERFORMANCE TESTS
    - Migrated AVF tests to use plugins/dev_iavf instead of plugins/avf.
    - Stopped running some tests where CSIT support got broken (various reasons).

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.

**#** | **Github issue number**                          | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

This table is temporarily left empty until all results are analyzed.

## Previous

Issues reported in previous releases which still affect the current results
(or would be affecting if other issues were not hiding the symptoms):

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------
  1   | [csit/issues/3974](https://github.com/FDio/csit/issues/3974) | [CSIT-1892] 3n-alt: two-band structure of ipsec and vxlan.
  2   | [csit/issues/3879](https://github.com/FDio/csit/issues/3879) | [CSIT-1795] Ocassionally not all DET44 sessions have been established: 4128767 != 4128768.
  3   | [csit/issues/3885](https://github.com/FDio/csit/issues/3885) | [CSIT-1802] all testbeds: AF-XDP - NDR tests failing from time to time on small loss
  4   | [csit/issues/3927](https://github.com/FDio/csit/issues/3927) | [CSIT-1845] AVF 9000B any ndrpdr test may start failing due to packets not arriving in one or both directions.
  5   | [csit/issues/3966](https://github.com/FDio/csit/issues/3966) | [CSIT-1884] 2n-icx, 2n-spr: All NAT44DET IMIX large scale BIDIR tests fail to create enough sessions.
  6   | [csit/issues/3968](https://github.com/FDio/csit/issues/3968) | [CSIT-1886] 3n: Wireguard tests with 100 and more tunnels are failing PDR criteria
  7   | [csit/issues/3978](https://github.com/FDio/csit/issues/3978) | [CSIT-1896] depending on topology, l3fwd avoids dut-dut link
  8   | [csit/issues/3983](https://github.com/FDio/csit/issues/3983) | [CSIT-1901] 2n-icx 3n-icx: Trex may report negative ipackets on high-performance AVF trial.
  9   | [csit/issues/3986](https://github.com/FDio/csit/issues/3986) | [CSIT-1904] 3n-alt: DPDK testpmd startup check fails on DUT2.
 10   | [csit/issues/3988](https://github.com/FDio/csit/issues/3988) | [CSIT-1906] Zero traffic with cx6/cx7 rdma. Testing migrated to mlx5-core only, on CX7 and CX6 Mellanox NICs.
 11   | [vpp/issues/3538](https://github.com/FDio/vpp/issues/3538)   | [VPP-2077] IP fragmentation: running_fragment_id is not thread safe.
 12   | [csit/issues/3996](https://github.com/FDio/csit/issues/3996) | [CSIT-1914] TRex does not produce latency data on ICE NICs.
 13   | [csit/issues/3997](https://github.com/FDio/csit/issues/3997) | [CSIT-1915] 2n-icx testbeds do not have the same performance.
 14   | [csit/issues/3998](https://github.com/FDio/csit/issues/3998) | [CSIT-1916] Poor CPU scaling on 2n-zn2 RDMA.
 15   | [csit/issues/3999](https://github.com/FDio/csit/issues/3999) | [CSIT-1917] TRex STL performance is unstable at high pps due to unsent packets.
 16   | [csit/issues/4004](https://github.com/FDio/csit/issues/4004) | [CSIT-1922] AF_XDP MRR regressions and PDR failures. Affects subsequent tests, that is why we are not testing AF-XDP now.
 17   | [csit/issues/4011](https://github.com/FDio/csit/issues/4011) | [CSIT-1929] Lossy trials in nat udp mlx5 tests.
 18   | [csit/issues/4017](https://github.com/FDio/csit/issues/4017) | [CSIT-1935] Zero traffic reported in udpquic tests due to session close errors.
 19   | [csit/issues/4018](https://github.com/FDio/csit/issues/4018) | [CSIT-1936] TRex occasionally sees link down in E8xx (dpdk) tests.
 20   | [csit/issues/4020](https://github.com/FDio/csit/issues/4020) | [CSIT-1938] 3n-alt: High scale ipsec policy tests may crash VPP.
 21   | [csit/issues/4023](https://github.com/FDio/csit/issues/4023) | [CSIT-1941] TRex may wrongly detect link bandwidth.
 22   | [csit/issues/4024](https://github.com/FDio/csit/issues/4024) | [CSIT-1942] 3nb-spr hoststack: interface not up after first test.
 23   | [vpp/issues/3551](https://github.com/FDio/vpp/issues/3551)   | [VPP-2090] MRR < PDR: dpdk plugin with mlx5 driver does not read full queue.
 24   | [vpp/issues/3552](https://github.com/FDio/vpp/issues/3552)   | [VPP-2091] Memif crashes VPP in container with jumbo frames.
 25   | [csit/issues/4029](https://github.com/FDio/csit/issues/4029) | [CSIT-1947] Rare VPP crash in nat avf tests.
 26   | [csit/issues/4030](https://github.com/FDio/csit/issues/4030) | [CSIT-1948] NICs do not consistently distribute tunnels over RXQs depending on model or plugin.
 27   | [csit/issues/4033](https://github.com/FDio/csit/issues/4033) | [CSIT-1951] Combination of AVF and vhost drops all 9000B packets.
 28   | [vpp/issues/3579](https://github.com/FDio/vpp/issues/3579)   | [VPP-2118] 3n spr: Unusable performance of ipsec tests with SHA_256_128.
 29   | [csit/issues/4041](https://github.com/FDio/csit/issues/4041) | [CSIT-1960] 2n-zn2: AVF xxv710 sometimes loses one direction of traffic, mostly with geneve.
 30   | [csit/issues/4043](https://github.com/FDio/csit/issues/4043) | [CSIT-1962] 3n-icx, 3na-spr: Udpquicscale tests sometimes fail with various symptoms.
 31   | [csit/issues/4044](https://github.com/FDio/csit/issues/4044) | [CSIT-1963] 3n-icxd: Various symptoms pointing to hardware (cable/nic/driver) issues.
 32   | [csit/issues/4045](https://github.com/FDio/csit/issues/4045) | [CSIT-1964] 3nb-spr, 3n-snr: Wireguardhw tests are likely to crash
 33   | [csit/issues/4049](https://github.com/FDio/csit/issues/4049) | [CSIT-1968] 3n-icx: two testbeds behave differently in some ipsec tests with AVF.
 34   | [csit/issues/4050](https://github.com/FDio/csit/issues/4050) | [CSIT-1969] nsim scale: Transport endpoint is not connected.
 35   | [csit/issues/4051](https://github.com/FDio/csit/issues/4051) | [CSIT-1970] JSON export validation does not prevent EPL from consuming invalid data.
 36   | [csit/issues/4052](https://github.com/FDio/csit/issues/4052) | [CSIT-1971] investigate two-band structure in nginx 2c cps tests.
 37   | [csit/issues/4058](https://github.com/FDio/csit/issues/4058) | [CSIT-1977] E810: Unsent packets at moderate load can fail soak.
 38   | [csit/issues/4059](https://github.com/FDio/csit/issues/4059) | [CSIT-1978] 3na-spr, 3nb-spr: Vhost tests cannot access testpmd.

This table is complete.

## Fixed

Issues reported in previous releases which were fixed
(or stopped being tested forever) in this release:

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  1   | [csit/issues/3869](https://github.com/FDio/csit/issues/3869) | [CSIT-1785] NAT44ED tests failing to establish all TCP sessions. At least for max scale, in allotted time (limited by session 500s timeout) due to worse slow path performance than previously measured and calibrated for. CSIT removed the max scale NAT tests to avoid this issue.
  2   | [csit/issues/4028](https://github.com/FDio/csit/issues/4028) | [CSIT-1946] ipsec hwasync fails with large scale and multiple queues.
  3   | [csit/issues/4032](https://github.com/FDio/csit/issues/4032) | [CSIT-1950] 9000B tests with encap overhead and non-dpdk plugins see fragmented packets.
  4   | [csit/issues/4035](https://github.com/FDio/csit/issues/4035) | [CSIT-1953] 3n-icx 3nb-spr: Failed to enable GTPU offload RX.
  5   | [csit/issues/4042](https://github.com/FDio/csit/issues/4042) | [CSIT-1961] Some tests have too long ramp-up trials. CSIT removed the max scale NAT tests to avoid this issue.
  6   | [vpp/issues/3582](https://github.com/FDio/vpp/issues/3582)   | [VPP-2121] sw_interface_add_del_address: avf process node failed to reply in 5 seconds. Hidden by testing plugins/iavf instead.
  7   | [csit/issues/4060](https://github.com/FDio/csit/issues/4060) | [CSIT-1979] 3na-spr: Flow related ipsec tests fail on CX7. Fixed by no longer running those tests on that NIC.

This list does not include issues that became unreproducible,
e.g. by CSIT decomissioning older testbeds.

Other than that, this table is complete.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 25.02 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **Github issue number**                          | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

This table is temporarily left empty until all results are analyzed.

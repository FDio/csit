---
title: "VPP Performance"
weight: 1
---

# CSIT 25.06 - VPP Performance

1. TEST FRAMEWORK
    - **CSIT test environment** version is ver. 18, see
      [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
    - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
2. VPP PERFORMANCE TESTS
    - **Added iterative and coverage performance tests** for 3n-oct testbed.

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.
For reporting reasons, even issues fixed during release are listed here,
as long as they caused some results to be missing (or performance wrong).

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   |                                                              |

## Previous

Issues reported in previous releases which still affect the current results
(or would be affecting if other issues were not hiding the symptoms):

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   | [csit/issues/3879](https://github.com/FDio/csit/issues/3879) | [CSIT-1795] Ocassionally not all DET44 sessions have been established: 4128767 != 4128768.
  2   | [csit/issues/3885](https://github.com/FDio/csit/issues/3885) | [CSIT-1802] all testbeds: AF-XDP - NDR tests failing from time to time on small loss.
  3   | [csit/issues/3966](https://github.com/FDio/csit/issues/3966) | [CSIT-1884] 2n-icx, 2n-spr: All NAT44DET IMIX large scale BIDIR tests fail to create enough sessions.
  4   | [csit/issues/3968](https://github.com/FDio/csit/issues/3968) | [CSIT-1886] 3n: Wireguard tests with 100 and more tunnels are failing PDR criteria.
  5   | [csit/issues/3978](https://github.com/FDio/csit/issues/3978) | [CSIT-1896] depending on topology, l3fwd avoids dut-dut link.
  6   | [csit/issues/3986](https://github.com/FDio/csit/issues/3986) | [CSIT-1904] 3n-alt: DPDK testpmd startup check fails on DUT2.
  7   | [csit/issues/3988](https://github.com/FDio/csit/issues/3988) | [CSIT-1906] Zero traffic with cx6/cx7 rdma. Testing migrated to mlx5-core only, on CX7 and CX6 Mellanox NICs.
  8   | [vpp/issues/3538](https://github.com/FDio/vpp/issues/3538)   | [VPP-2077] IP fragmentation: running_fragment_id is not thread safe.
  9   | [csit/issues/3996](https://github.com/FDio/csit/issues/3996) | [CSIT-1914] TRex does not produce latency data on ICE NICs.
 10   | [csit/issues/3997](https://github.com/FDio/csit/issues/3997) | [CSIT-1915] 2n-icx testbeds do not have the same performance.
 11   | [csit/issues/3998](https://github.com/FDio/csit/issues/3998) | [CSIT-1916] Poor CPU scaling on 2n-zn2 RDMA.
 12   | [csit/issues/3999](https://github.com/FDio/csit/issues/3999) | [CSIT-1917] TRex STL performance is unstable at high pps due to unsent packets.
 13   | [csit/issues/4004](https://github.com/FDio/csit/issues/4004) | [CSIT-1922] AF_XDP MRR regressions and PDR failures. Affects subsequent tests, that is why we are not testing AF-XDP now.
 14   | [csit/issues/4011](https://github.com/FDio/csit/issues/4011) | [CSIT-1929] Lossy trials in nat udp mlx5 tests.
 15   | [csit/issues/4018](https://github.com/FDio/csit/issues/4018) | [CSIT-1936] TRex occasionally sees link down in E8xx (dpdk) tests.
 16   | [csit/issues/4020](https://github.com/FDio/csit/issues/4020) | [CSIT-1938] 3n-alt: High scale ipsec policy tests may crash VPP.
 17   | [csit/issues/4023](https://github.com/FDio/csit/issues/4023) | [CSIT-1941] TRex may wrongly detect link bandwidth.
 18   | [csit/issues/4024](https://github.com/FDio/csit/issues/4024) | [CSIT-1942] 3nb-spr hoststack: interface not up after first test.
 19   | [vpp/issues/3551](https://github.com/FDio/vpp/issues/3551)   | [VPP-2090] MRR < PDR: dpdk plugin with mlx5 driver does not read full queue.
 20   | [vpp/issues/3552](https://github.com/FDio/vpp/issues/3552)   | [VPP-2091] Memif crashes VPP in container with jumbo frames.
 21   | [csit/issues/4029](https://github.com/FDio/csit/issues/4029) | [CSIT-1947] Rare VPP crash in nat avf tests.
 22   | [csit/issues/4030](https://github.com/FDio/csit/issues/4030) | [CSIT-1948] NICs do not consistently distribute tunnels over RXQs depending on model or plugin.
 23   | [csit/issues/4033](https://github.com/FDio/csit/issues/4033) | [CSIT-1951] Combination of AVF and vhost drops all 9000B packets.
 24   | [vpp/issues/3579](https://github.com/FDio/vpp/issues/3579)   | [VPP-2118] 3n spr: Unusable performance of ipsec tests with SHA_256_128.
 25   | [csit/issues/4043](https://github.com/FDio/csit/issues/4043) | [CSIT-1962] 3n-icx, 3na-spr: Udpquicscale tests sometimes fail with various symptoms.
 26   | [csit/issues/4044](https://github.com/FDio/csit/issues/4044) | [CSIT-1963] 3n-icxd: Various symptoms pointing to hardware (cable/nic/driver) issues.
 27   | [csit/issues/4045](https://github.com/FDio/csit/issues/4045) | [CSIT-1964] 3nb-spr, 3n-snr: Wireguardhw tests are likely to crash.
 28   | [csit/issues/4051](https://github.com/FDio/csit/issues/4051) | [CSIT-1970] JSON export validation does not prevent EPL from consuming invalid data.
 29   | [csit/issues/4058](https://github.com/FDio/csit/issues/4058) | [CSIT-1977] E810: Unsent packets at moderate load can fail soak.
 30   | [csit/issues/4066](https://github.com/FDio/csit/issues/4066) | 2n-icx: iavf bus error in one run.
 31   | [vpp/issues/3597](https://github.com/FDio/vpp/issues/3597)   | dev_iavf: Unable to use more queues than offered initially.
 32   | [csit/issues/4073](https://github.com/FDio/csit/issues/4073) | Tests combining iavf+jumbo gradually run out of buffers for rx.
 33   | [csit/issues/4076](https://github.com/FDio/csit/issues/4076) | 3n-icx: vhost mounting /dev failed.

## Fixed

Issues reported in previous releases which were fixed
(or stopped being tested forever) in this release:

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   | [csit/issues/3974](https://github.com/FDio/csit/issues/3974) | [CSIT-1892] 3n-alt: two-band structure of ipsec and vxlan.
  2   | [csit/issues/3983](https://github.com/FDio/csit/issues/3983) | [CSIT-1901] 2n-icx 3n-icx: Trex may report negative ipackets on high-performance AVF trial.
  3   | [csit/issues/4017](https://github.com/FDio/csit/issues/4017) | [CSIT-1935] Zero traffic reported in udpquic tests due to session close errors.
  4   | [csit/issues/4049](https://github.com/FDio/csit/issues/4049) | [CSIT-1968] 3n-icx: two testbeds behave differently in some ipsec tests with AVF.
  5   | [csit/issues/4050](https://github.com/FDio/csit/issues/4050) | [CSIT-1969] nsim scale: Transport endpoint is not connected.
  6   | [csit/issues/4059](https://github.com/FDio/csit/issues/4059) | [CSIT-1978] 3na-spr, 3nb-spr: Vhost tests cannot access testpmd.
  7   | [csit/issues/4063](https://github.com/FDio/csit/issues/4063) | 2n-emr: NGINX tests fail due to missing libpcre.
  8   | [csit/issues/4064](https://github.com/FDio/csit/issues/4064) | 2n-emr: DSA tests fail on accel-config: command not found.
  9   | [csit/issues/4065](https://github.com/FDio/csit/issues/4065) | 2n-spr: Failed to enable DMA work queue on DUT.
 10   | [csit/issues/4068](https://github.com/FDio/csit/issues/4068) | DSA: enabled 0 wq(s) out of 1.
 11   | [csit/issues/4069](https://github.com/FDio/csit/issues/4069) | tap: Command execution failed.
 12   | [csit/issues/4070](https://github.com/FDio/csit/issues/4070) | 2n-grc: VPP in VM sometimes too slow to start with 4C.
 13   | [vpp/issues/3598](https://github.com/FDio/vpp/issues/3598)   | dev_iavf: Setting promisc fails due to uninitialized byte.
 14   | [csit/issues/4071](https://github.com/FDio/csit/issues/4071) | bonding+iavf: l3 mac mismatch.
 15   | [csit/issues/4072](https://github.com/FDio/csit/issues/4072) | QAT1: 1tnl tests are crashing.
 16   | [csit/issues/4074](https://github.com/FDio/csit/issues/4074) | rls2502: CSIT does not wait long enough after killing VPP; fixed during rls2502 testing.
 17   | [csit/issues/4075](https://github.com/FDio/csit/issues/4075) | EMR: Sometimes cli.sock is not responding.
 18   | [vpp/issues/3602](https://github.com/FDio/vpp/issues/3602)   | device framework: next node not updated when a feature is enabled; fixed now.

# Root Cause Analysis for Regressions

List of RCAs in CSIT 25.06 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   |                                                              |

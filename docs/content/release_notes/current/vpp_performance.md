---
title: "VPP Performance"
weight: 1
---

# CSIT 25.10 - VPP Performance

1. TEST FRAMEWORK
    - **CSIT test environment** version is ver. 18, see
      [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
      - We no longer support Intel-XL710 in 3n-alt.
    - **New Suite Generator** has been implemented. For more information see
      - [Suite Generation]({{< ref "../../overview/csit/suite_generation" >}})
      - [Job Triggering]({{< ref "../../overview/csit/job_triggering" >}})
    - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
2. VPP PERFORMANCE TESTS
    - **Modifications in the coverage jobs:** The job specifications for
      coverage tests were changed to run the same tests as in iterative but with
      more combinations of
      - frame sizes
      - cpus/cores
      - scales

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

Tables stay empty until the list of issues there is finalized.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.
For reporting reasons, even issues fixed during release are listed here,
as long as they caused some results to be missing (or performance wrong).

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------------------------------
  1   | [csit/issues/4106](https://github.com/FDio/csit/issues/4106) | Unstable performance of ldpreload+tcp tests.
  2   | [csit/issues/4112](https://github.com/FDio/csit/issues/4112) | tests relying on docker fail on 3n-alt.
  3   | [csit/issues/4113](https://github.com/FDio/csit/issues/4113) | 2n-grc: rarely, Linux is too slow to re-detect interfaces after VPP kill.
(one or two tickets related to gtpuhw jumbo will go here)

## Previous

Issues reported in previous releases which still affect the current results
(or would be affecting if other issues were not hiding the symptoms):

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------
  1   | [csit/issues/3879](https://github.com/FDio/csit/issues/3879) | [CSIT-1795] Ocassionally not all DET44 sessions have been established: 4128767 != 4128768.
  2   | [csit/issues/3966](https://github.com/FDio/csit/issues/3966) | [CSIT-1884] 2n-icx, 2n-spr: All NAT44DET IMIX large scale BIDIR tests fail to create enough sessions.
  3   | [csit/issues/3968](https://github.com/FDio/csit/issues/3968) | [CSIT-1886] 3n: Wireguard tests with 100 and more tunnels are failing PDR criteria.
  4   | [vpp/issues/3538](https://github.com/FDio/vpp/issues/3538)   | [VPP-2077] IP fragmentation: running_fragment_id is not thread safe.
  5   | [csit/issues/3996](https://github.com/FDio/csit/issues/3996) | [CSIT-1914] TRex does not produce latency data on ICE NICs.
  6   | [csit/issues/3997](https://github.com/FDio/csit/issues/3997) | [CSIT-1915] 2n-icx testbeds do not have the same performance.
  7   | [csit/issues/3998](https://github.com/FDio/csit/issues/3998) | [CSIT-1916] Poor CPU scaling on 2n-zn2 RDMA.
  8   | [csit/issues/3999](https://github.com/FDio/csit/issues/3999) | [CSIT-1917] TRex STL performance is unstable at high pps due to unsent packets.
  9   | [csit/issues/4011](https://github.com/FDio/csit/issues/4011) | [CSIT-1929] Lossy trials in nat udp mlx5 tests.
 10   | [csit/issues/4018](https://github.com/FDio/csit/issues/4018) | [CSIT-1936] TRex occasionally sees link down in E8xx (dpdk) tests.
 11   | [csit/issues/4020](https://github.com/FDio/csit/issues/4020) | [CSIT-1938] 3n-alt: High scale ipsec policy tests may crash VPP.
 12   | [csit/issues/4023](https://github.com/FDio/csit/issues/4023) | [CSIT-1941] TRex may wrongly detect link bandwidth.
 13   | [csit/issues/4024](https://github.com/FDio/csit/issues/4024) | [CSIT-1942] 3nb-spr hoststack: interface not up after first test.
 14   | [vpp/issues/3551](https://github.com/FDio/vpp/issues/3551)   | [VPP-2090] MRR < PDR: dpdk plugin with mlx5 driver does not read full queue.
 15   | [vpp/issues/3552](https://github.com/FDio/vpp/issues/3552)   | [VPP-2091] Memif crashes VPP in container with jumbo frames.
 16   | [csit/issues/4029](https://github.com/FDio/csit/issues/4029) | [CSIT-1947] Rare VPP crash in nat avf tests.
 17   | [csit/issues/4030](https://github.com/FDio/csit/issues/4030) | [CSIT-1948] NICs do not consistently distribute tunnels over RXQs depending on model or plugin.
 18   | [csit/issues/4033](https://github.com/FDio/csit/issues/4033) | [CSIT-1951] Combination of AVF and vhost drops all 9000B packets.
 19   | [vpp/issues/3579](https://github.com/FDio/vpp/issues/3579)   | [VPP-2118] 3n spr: Unusable performance of ipsec tests with SHA_256_128.
 20   | [csit/issues/4043](https://github.com/FDio/csit/issues/4043) | [CSIT-1962] 3n-icx, 3na-spr: Udpquicscale tests sometimes fail with various symptoms.
 21   | [csit/issues/4044](https://github.com/FDio/csit/issues/4044) | [CSIT-1963] 3n-icxd: Various symptoms pointing to hardware (cable/nic/driver) issues.
 22   | [csit/issues/4045](https://github.com/FDio/csit/issues/4045) | [CSIT-1964] 3nb-spr, 3n-snr: Wireguardhw tests are likely to crash.
 23   | [vpp/issues/3597](https://github.com/FDio/vpp/issues/3597)   | dev_iavf: Unable to use more queues than offered initially.
 24   | [csit/issues/4073](https://github.com/FDio/csit/issues/4073) | Tests combining iavf+jumbo gradually run out of buffers for rx.
 25   | [csit/issues/4076](https://github.com/FDio/csit/issues/4076) | 3n-icx: vhost mounting /dev failed.
 26   | [csit/issues/4087](https://github.com/FDio/csit/issues/4087) | 2n-aws: Infrequent error 11 when dpdk plugin initializes interface.
 27   | [csit/issues/4088](https://github.com/FDio/csit/issues/4088) | Occasional timeout in iperf vhost non-gso.
 28   | [csit/issues/4089](https://github.com/FDio/csit/issues/4089) | 2n-zn2 iavf 2c: PDR fails due to delayed packets.
 29   | [csit/issues/4090](https://github.com/FDio/csit/issues/4090) | crypto engine error in 1tnl wireguardhw test.
 30   | [csit/issues/4091](https://github.com/FDio/csit/issues/4091) | udpquicbase fails due to: Echo connect failed.
 31   | [csit/issues/4092](https://github.com/FDio/csit/issues/4092) | udp ldpreload fails on no test data retrieved.
 32   | [csit/issues/4094](https://github.com/FDio/csit/issues/4094) | 3n-oct: unsent packets even at min load.
 33   | [csit/issues/4096](https://github.com/FDio/csit/issues/4096) | rare crash in nginx tests.
 34   | [csit/issues/4097](https://github.com/FDio/csit/issues/4097) | 2n-zn2 iavf: two-band structure in 1c mrr tests.
 35   | [vpp/issues/3628](https://github.com/FDio/vpp/issues/3628)   | ip: route APIs are not thread safe.

## Hidden

Issues listed here are not affecting current release results,
either because we are no longer running the affected tests or testbeds,
or because the adverse effect would be triggered by a symptom not curently present.
Issues listed here would generally need to be verified unsing an unmerged CSIT code,
which was not done for most of the issues.
Having this list here is useful if the symptom appears in next release,
either by a diiferent trigger enabling it, or CSIT increasing test coverage.

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------
  1   | [csit/issues/3885](https://github.com/FDio/csit/issues/3885) | [CSIT-1802] all testbeds: AF-XDP - NDR tests failing from time to time on small loss.
  2   | [csit/issues/3978](https://github.com/FDio/csit/issues/3978) | [CSIT-1896] depending on topology, l3fwd avoids dut-dut link.
  3   | [csit/issues/3986](https://github.com/FDio/csit/issues/3986) | [CSIT-1904] 3n-alt: DPDK testpmd startup check fails on DUT2.
  4   | [csit/issues/3988](https://github.com/FDio/csit/issues/3988) | [CSIT-1906] Zero traffic with cx6/cx7 rdma. Testing migrated to mlx5-core only, on CX7 and CX6 Mellanox NICs.
  5   | [csit/issues/4004](https://github.com/FDio/csit/issues/4004) | [CSIT-1922] AF_XDP MRR regressions and PDR failures. Affects subsequent tests, that is why we are not testing AF-XDP now.
  6   | [csit/issues/4051](https://github.com/FDio/csit/issues/4051) | [CSIT-1970] JSON export validation does not prevent EPL from consuming invalid data.
  7   | [csit/issues/4066](https://github.com/FDio/csit/issues/4066) | 2n-icx: iavf bus error in one run.
  8   | [csit/issues/4095](https://github.com/FDio/csit/issues/4095) | jumbo+iavf buffer alloc error: loadbalancer.
  9   | [vpp/issues/3624](https://github.com/FDio/vpp/issues/3624)   | perfmon: asan reports global-buffer-overflow on Intel Xeons.
 10   | [vpp/issues/3627](https://github.com/FDio/vpp/issues/3627)   | ASAN: VPP silently quits after 41560.

## Fixed

Issues reported in previous releases which were fixed
(or stopped being tested forever) in this release:

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   | [csit/issues/4093](https://github.com/FDio/csit/issues/4093) | out of memory in hoststack; fixed after rls2506.
  2   | [csit/issues/4098](https://github.com/FDio/csit/issues/4098) | 2n-zn2 xxv710 iavf: all 9000b tests fail on retval: -168.
  3   | [csit/issues/4103](https://github.com/FDio/csit/issues/4103) | 2n-c7gn: multi-band structure in 1c results

# Root Cause Analysis for Regressions

List of RCAs in CSIT 25.10 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|-----------------------------------------------------------------
  1   | [csit/issues/4109](https://github.com/FDio/csit/issues/4109) | dev/iavf: RX queue on main thread (fixed shortly after rls2510).
  2   | [csit/issues/4110](https://github.com/FDio/csit/issues/4110) | ARM (expected) anomalies near 2025-08-30.
  3   | [csit/issues/4111](https://github.com/FDio/csit/issues/4111) | probable regression on 2n-aws mid July 2025.
  4   | [csit/issues/4114](https://github.com/FDio/csit/issues/4114) | ip6 regressions end of November 2025.
  5   | [csit/issues/4115](https://github.com/FDio/csit/issues/4115) | ip6 regression early July 2025.
(might get split into two tickets depending on bisect)

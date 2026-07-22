---
title: "VPP Performance"
weight: 1
---

# CSIT 26.06 - VPP Performance

1. TEST FRAMEWORK
    - **CSIT test environment** version is ver. 19, see
      [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
    - **Hands-Free Releasing**: Automation of CSIT release flow so that a single
      action drives a fully automated pipeline.
    - **Local compilation**: CSIT no longer downloads generic builds from packagecloud.
    - **Platform builds**: After ARM in previous releases, three generations of Xeon processors
      were also switched to platform builds, mainly to restore IPsec perfomance.
    - **General Code Housekeeping**: Ongoing code optimizations and bug fixes,
      including tweaks to job specifications.
2. VPP PERFORMANCE TESTS
    - **SFDP suites**: Added for initial coverage for VPP's SFDP functionality and performance.
    - **Added 2n-gnr, 3n-gnr and 3n-srf testbeds**, see
      [FD.io DC Testbed Specifications]({{< ref "../../../infrastructure/fdio_dc_testbed_specifications" >}})
    - **Removed 3n-snr and 3n-icxd testbeds**.

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
------|--------------------------------------------------------------|--------------------------------------------------
  1   |                                                              |

## Previous

Issues reported in previous releases which still affect the current results
(or would be affecting if other issues were not hiding the symptoms):

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   | [csit/issues/3879](https://github.com/FDio/csit/issues/3879) | [CSIT-1795] Ocassionally not all DET44 sessions have been established: 4128767 != 4128768
  2   | [csit/issues/3966](https://github.com/FDio/csit/issues/3966) | [CSIT-1884] 2n-icx, 2n-spr: All NAT44DET IMIX large scale BIDIR tests fail to create enough sessions
  3   | [csit/issues/3968](https://github.com/FDio/csit/issues/3968) | [CSIT-1886] 3n: Wireguard tests with 100 and more tunnels are failing PDR criteria
  4   | [csit/issues/3996](https://github.com/FDio/csit/issues/3996) | [CSIT-1914] TRex does not produce latency data on ICE NICs
  5   | [csit/issues/3997](https://github.com/FDio/csit/issues/3997) | [CSIT-1915] 2n-icx testbeds do not have the same performance
  6   | [csit/issues/3998](https://github.com/FDio/csit/issues/3998) | [CSIT-1916] Poor CPU scaling on 2n-zn2 RDMA
  7   | [csit/issues/3999](https://github.com/FDio/csit/issues/3999) | [CSIT-1917] TRex STL performance is unstable at high pps due to unsent packets
  8   | [csit/issues/4011](https://github.com/FDio/csit/issues/4011) | [CSIT-1929] Lossy trials in nat udp mlx5 and avf tests
  9   | [csit/issues/4018](https://github.com/FDio/csit/issues/4018) | [CSIT-1936] TRex occasionally sees link down in E8xx (dpdk) tests
 10   | [csit/issues/4020](https://github.com/FDio/csit/issues/4020) | [CSIT-1938] 3n-alt: High scale ipsec policy tests may crash VPP
 11   | [csit/issues/4023](https://github.com/FDio/csit/issues/4023) | [CSIT-1941] TRex may wrongly detect link bandwidth
 12   | [csit/issues/4024](https://github.com/FDio/csit/issues/4024) | [CSIT-1942] 3nb-spr hoststack: interface not up after first test
 13   | [vpp/issues/3551](https://github.com/FDio/vpp/issues/3551)   | [VPP-2090] MRR < PDR: dpdk plugin with mlx5 driver does not read full queue
 14   | [csit/issues/4030](https://github.com/FDio/csit/issues/4030) | [CSIT-1948] NICs do not consistently distribute tunnels over RXQs depending on model or plugin
 15   | [csit/issues/4033](https://github.com/FDio/csit/issues/4033) | [CSIT-1951] Combination of AVF and vhost drops all 9000B packets
 16   | [csit/issues/4045](https://github.com/FDio/csit/issues/4045) | [CSIT-1964] 3nb-spr, 3n-snr: Wireguardhw tests are likely to crash
 17   | [csit/issues/4073](https://github.com/FDio/csit/issues/4073) | Tests combining iavf+jumbo gradually run out of buffers for rx
 18   | [csit/issues/4076](https://github.com/FDio/csit/issues/4076) | 3n-icx: vhost mounting /dev failed
 19   | [csit/issues/4088](https://github.com/FDio/csit/issues/4088) | Occasional timeout in iperf vhost non-gso
 20   | [csit/issues/4090](https://github.com/FDio/csit/issues/4090) | crypto engine error in 1tnl wireguardhw test
 21   | [csit/issues/4091](https://github.com/FDio/csit/issues/4091) | udpquicbase fails due to: Echo connect failed
 22   | [csit/issues/4092](https://github.com/FDio/csit/issues/4092) | udp ldpreload fails on no test data retrieved
 23   | [csit/issues/4094](https://github.com/FDio/csit/issues/4094) | 3n-oct: unsent packets even at min load
 24   | [csit/issues/4096](https://github.com/FDio/csit/issues/4096) | rare crash in nginx tests
 25   | [csit/issues/4097](https://github.com/FDio/csit/issues/4097) | 2n-zn2 iavf: two-band structure in 1c mrr tests
 26   | [vpp/issues/3628](https://github.com/FDio/vpp/issues/3628)   | ip: route APIs are not thread safe
 27   | [csit/issues/4106](https://github.com/FDio/csit/issues/4106) | Unstable performance of ldpreload+tcp tests
 28   | [csit/issues/4113](https://github.com/FDio/csit/issues/4113) | 2n-grc: rarely, Linux is too slow to re-detect interfaces after VPP kill
 29   | [csit/issues/4118](https://github.com/FDio/csit/issues/4118) | GTPUhw jumbo has zero traffic due to tx_errors

## Fixed

Issues reported in previous releases which were fixed (or stopped being tested
forever) in this release:

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   | [vpp/issues/3538](https://github.com/FDio/vpp/issues/3538)   | [VPP-2077] IP fragmentation: running_fragment_id is not thread safe
  2   | [vpp/issues/3552](https://github.com/FDio/vpp/issues/3552)   | [VPP-2091] Memif crashes VPP in container with jumbo frames
  3   | [vpp/issues/3597](https://github.com/FDio/vpp/issues/3597)   | dev_iavf: Unable to use more queues than offered initially
  4   | [csit/issues/4089](https://github.com/FDio/csit/issues/4089) | 2n-zn2 iavf 2c: PDR fails due to delayed packets
  5   | [csit/issues/4140](https://github.com/FDio/csit/issues/4140) | udpquic: signum=11 on quic set fifo-size

# Root Cause Analysis for Regressions

List of RCAs in CSIT 26.06 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomised RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   |                                                              |

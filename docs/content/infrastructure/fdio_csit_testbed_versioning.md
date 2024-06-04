---
bookToc: true
title: "FD.io CSIT Testbed Versioning"
weight: 4
---

# FD.io CSIT Testbed Versioning

CSIT test environment versioning has been introduced to track modifications of
the test environment.

Any benchmark anomalies (progressions, regressions) between releases of a DUT
application (e.g. VPP, DPDK), are determined by testing it in the same test
environment, to avoid test environment changes clouding the picture.
To beter distinguish impact of test environment changes, we also execute tests
without any SUT (just with TRex TG sending packets over a link looping back to
TG).

A mirror approach is introduced to determine benchmarking anomalies due to the
test environment change. This is achieved by testing the same DUT application
version between releases of CSIT test system. This works under the assumption
that the behaviour of the DUT is deterministic under the test conditions.

CSIT test environment versioning scheme ensures integrity of all the test system
components, including their HW revisions, compiled SW code versions and SW
source code, within a specific CSIT version. Components included in the CSIT
environment versioning include:

- **HW** Server hardware firmware and BIOS (motherboard, processsor,
  NIC(s), accelerator card(s)), tracked in CSIT branch.
- **Linux** Server Linux OS version and configuration, tracked in CSIT
  Reports.
- **TRex** TRex Traffic Generator version, drivers and configuration
  tracked in TG Settings.
- **CSIT** CSIT framework code tracked in CSIT release branches.

Following is the list of CSIT versions to date:

- Ver. 15 associated with CSIT rls2406 branch (
  [HW](https://git.fd.io/csit/tree/docs/content/infrastructure/testbed_configuration?h=rls2406),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2406)
  ).
- Ver. 14 associated with CSIT rls2402 branch (
  [HW](https://git.fd.io/csit/tree/docs/content/infrastructure/testbed_configuration?h=rls2402),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2402)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
  - Mellanox 556A/CX6-DX/MCX713106AS-VEAT series firmware upgrade based on DPDK
    compatibility matrix.
- Ver. 13 associated with CSIT rls2310 branch (
  [HW](https://git.fd.io/csit/tree/docs/content/infrastructure/testbed_configuration?h=rls2310),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2310)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
  - Mellanox 556A/CX6-DX/MCX713106AS-VEAT series firmware upgrade based on DPDK
    compatibility matrix.
- Ver. 12 associated with CSIT rls2306 branch (
  [HW](https://git.fd.io/csit/tree/docs/content/infrastructure/testbed_configuration?h=rls2306),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2306)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
  - Mellanox 556A/CX6-DX/MCX713106AS-VEAT series firmware upgrade based on DPDK
    compatibility matrix.
  - TRex version upgrade: increase from 3.00 to 3.03.
- Ver. 11 associated with CSIT rls2210 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2210),
  [Linux](https://s3-docs.fd.io/csit/rls2210/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://s3-docs.fd.io/csit/rls2210/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2210)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
  - Mellanox 556A series firmware upgrade based on DPDK compatibility
    matrix.
  - Ubuntu upgrade from 20.04.2 LTS to 22.04.1 LTS.
  - TRex version upgrade: increase from 2.97 to 3.00.
- Ver. 10 associated with CSIT rls2206 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2206),
  [Linux](https://s3-docs.fd.io/csit/rls2206/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://s3-docs.fd.io/csit/rls2206/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2206)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
  - Mellanox 556A series firmware upgrade based on DPDK compatibility
    matrix.
  - Intel IceLake all core turbo frequency turned off. Current base frequency
    is 2.6GHz.
  - TRex version upgrade: increase from 2.88 to 2.97.
- Ver. 9 associated with CSIT rls2202 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2202),
  [Linux](https://s3-docs.fd.io/csit/rls2202/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://s3-docs.fd.io/csit/rls2202/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2202)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
- Ver. 8 associated with CSIT rls2110 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2110),
  [Linux](https://s3-docs.fd.io/csit/rls2110/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://s3-docs.fd.io/csit/rls2110/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2110)
  ).
  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
- Ver. 7 associated with CSIT rls2106 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2106),
  [Linux](https://s3-docs.fd.io/csit/rls2106/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://s3-docs.fd.io/csit/rls2106/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2106)
  ).
  - TRex version upgrade: increase from 2.86 to 2.88.
  - Ubuntu upgrade from 18.04 LTS to 20.04.2 LTS.
- Ver. 6 associated with CSIT rls2101 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2101),
  [Linux](https://docs.fd.io/csit/rls2101/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://docs.fd.io/csit/rls2101/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2101)
  ).
  - The main change is TRex version upgrade: increase from 2.82 to 2.86.
- Ver. 5 associated with CSIT rls2009 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2009),
  [Linux](https://docs.fd.io/csit/rls2009/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://docs.fd.io/csit/rls2009/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2009)
  ).
  - The main change is TRex data-plane core resource adjustments:
    [increase from 7 to 8 cores and pinning cores to interfaces](https://gerrit.fd.io/r/c/csit/+/28184)
    for better TRex performance with symmetric traffic profiles.
- Ver. 4 associated with CSIT rls2005 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2005),
  [Linux](https://docs.fd.io/csit/rls2005/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://docs.fd.io/csit/rls2005/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2005)
  ).
- Ver. 2 associated with CSIT rls2001 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls2001),
  [Linux](https://docs.fd.io/csit/rls2001/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://docs.fd.io/csit/rls2001/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls2001)
  ).
- Ver. 1 associated with CSIT rls1908 branch (
  [HW](https://git.fd.io/csit/tree/docs/lab?h=rls1908),
  [Linux](https://docs.fd.io/csit/rls1908/report/vpp_performance_tests/test_environment.html#sut-settings-linux),
  [TRex](https://docs.fd.io/csit/rls1908/report/vpp_performance_tests/test_environment.html#tg-settings-trex),
  [CSIT](https://git.fd.io/csit/tree/?h=rls1908)
  ).

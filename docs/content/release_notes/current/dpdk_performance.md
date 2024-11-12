---
title: "DPDK Performance"
weight: 2
---

# CSIT 24.10 - DPDK Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version 15 is used, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
2. DPDK PERFORMANCE TESTS
   - No updates
3. DPDK RELEASE VERSION CHANGE
   - Version 24.07 is now tested.

# Known Issues

List of known issues in CSIT 24.10 for DPDK performance tests:

## New

List of new issues in CSIT 24.10 for DPDK performance tests:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------
  1   | [CSIT-1972](https://jira.fd.io/browse/CSIT-1972) | 2n-zn2, 3nb-spr: Testpmd occasionally does not forward in one direction in 9000B test.
  2   | [CSIT-1973](https://jira.fd.io/browse/CSIT-1973) | 3n-snr: One lossy testpmd test+run.
  3   | [CSIT-1974](https://jira.fd.io/browse/CSIT-1974) | cx7: Persistent losses in testpmd 4c imix test. (Already present in previous release, just not reported back then.)

## Previous

List of known issues in CSIT 24.10 for DPDK performance tests:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|-----------------------------------------------------
  1   | [CSIT-1924](https://jira.fd.io/browse/CSIT-1924) | L3fwd error in 200Ge2P1Cx7Veat-Mlx5 test with 9000B.
  2   | [CSIT-1936](https://jira.fd.io/browse/CSIT-1936) | TRex occasionally sees link down in L3fwd tests.

## Fixed

List of fixed issues in CSIT 24.10 for DPDK performance tests:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|----------------------
 1    |                                                  |

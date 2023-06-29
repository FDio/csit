---
title: "DPDK Performance"
weight: 2
---

# CSIT 23.06 - DPDK Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 12, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
2. DPDK PERFORMANCE TESTS
   - Added support for new NICs.
3. DPDK RELEASE VERSION CHANGE
   - Version 23.03 is now tested.

# Known Issues

List of known issues in CSIT 23.06 for DPDK performance tests:

## New

List of new issues in CSIT 23.06 for DPDK performance tests:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1904](https://jira.fd.io/browse/CSIT-1904) | DPDK 23.03 testpmd starup fails on some testbeds. Different cause but the same consequences as CSIT-1848.

## Previous

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    |                                                  |

## Fixed

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1848](https://jira.fd.io/browse/CSIT-1848) | 3n-alt: testpmd tests fail due DUT-DUT link taking long to come up. Fixed for 3n-alt on infra level, but reapeared after DPDK bump as CSIT-1904 on multiple more platforms.

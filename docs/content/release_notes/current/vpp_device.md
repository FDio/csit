---
title: "VPP Device"
weight: 4
---

# CSIT 24.06 - VPP Device

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 15, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
2. DEVICE TESTS
   - Added Intel-X710 to 1n-spr and Mellanox-CX6DX to 1n-alt testbed.
   - Migrated some test to the new NICs to avoid spurious failures.

# Known Issues

List of known issues in CSIT 24.06 for VPP functional tests in VPP Device:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1931](https://jira.fd.io/browse/CSIT-1931) | Vhost test not running in device jobs
 2    | [CSIT-1932](https://jira.fd.io/browse/CSIT-1932) | 1n-spr: Occasional packet loss in L2 tests

## New

List of new issues in CSIT 24.06 for VPP functional tests in VPP Device:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    |                                                  |

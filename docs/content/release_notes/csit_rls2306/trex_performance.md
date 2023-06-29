---
title: "TRex Performance"
weight: 3
---

# CSIT 23.06 - TRex Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 12, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
2. TREX TESTS
   - No longer testing scale2m, testing scale20k instead (for AWS reasons).
3. TREX VERSION
   - Currently using v3.03 of TRex.

# Known Issues

## New

List of new issues in CSIT 23.06 for TRex performance tests:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    |                                                  |

## Previous

List of known issues in CSIT 23.06 for TRex performance tests

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    |                                                  |

## Fixed

List of known issues in CSIT 23.02 for TRex performance tests

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
 1    | [CSIT-1876](https://jira.fd.io/browse/CSIT-1876) | 1n-aws: TRex NDR PDR ALL IP4 scale and L2 scale tests failing with 50% packet loss. Fixed for most scales. Only ip4scale2m still fails, but we removed that from jobspecs.

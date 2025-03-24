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
    - The testbeds 2n-alt and 3n-emr are out-of-service for 25.02 release.
    - HW related parts that are out-of-service for 25.02 release:
        - DSA.
    - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
2. VPP PERFORMANCE TESTS
    - Migrated AVF tests to use plugins/dev_iavf instead of plugins/avf.
    - Stopped running some tests where CSIT support got broken (various reasons).

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

The following tables are temporarily left empty until all results are analyzed.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.

**#** | **Github issue number**                          | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

## Previous

Issues reported in previous releases which still affect the current results.

**#** | **Github issue number**                          | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **Github issue number**                          | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

Not listing issues that became unreproducible, e.g. by CSIT decomissioning older testbeds.

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

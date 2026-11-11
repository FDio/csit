---
title: "VPP Performance"
weight: 1
---

# CSIT 26.10 - VPP Performance

1. TEST FRAMEWORK
    - **CSIT test environment** version is ver. 20, see
      [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
    - **Platform specific builds**: Now used for every testbed.
    - **Buffer layout**: Explicitly apply natural layout as we use hugepages.
    - **General Code Housekeeping**: Ongoing code optimizations and bug fixes,
      including tweaks to job specifications.
2. VPP PERFORMANCE TESTS
    - **SFDP suites**: Added suites for NAT SFDP service.
    - **Added RDMA tests**: For CX6 and CX7.
    - **Hoststack**: Use vperf instead of vpp_echo.

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
  1   |                                                              |

## Fixed

Issues reported in previous releases which were fixed (or stopped being tested
forever) in this release:

**#** | **Github issue number**                                      | **Issue Description**
------|--------------------------------------------------------------|--------------------------------------------------
  1   |                                                              |

# Root Cause Analysis for Regressions

List of RCAs in CSIT 26.10 for VPP performance regressions.
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

---
title: "VPP Performance"
weight: 1
---

# CSIT 24.06 - VPP Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version 14 used, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
   - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
2. VPP PERFORMANCE TESTS
   - Added tests:
     - Added memif+DMA tests; added 1518B and 4c memif testcases.
     - Added nginx+DMA tests; added 2048B testcases.
     - Added IPsec hwasync tests to 3n-icxd and 3n-snr.
     - Added IPsec tests to cover more encryption algorithms and other settings. (TODO: Not merged yet.)
     - Added more SOAK tests. (TODO: Add even more for release.)
   - Edited tests:
     - Selected single-flow tests now use single worker even if SMT is on.
     - IPsecHW tests now use rxq ratio of 2 (less queues, to improve performance).
     - 1518B tests with encapsulation overhead now properly use no-multi-seg.
     - Added TX checksum offload to hoststack tests missing it.
   - TODO: Peter did something so 3na-spr runs 6p tests instead of 2p tests?
3. PRESENTATION AND ANALYTICS LAYER
   - Detailed views added to comparison tables.

# Known Issues

These are issues that cause test failures or otherwise limit usefulness of CSIT
testing.

## New

Any issue listed here may have been present also in a previous release,
but was not detected/recognized/reported enough back then.
Also, issues previously thought fixed but now reopened are listed here.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

## Previous

Issues reported in previous releases which still affect the current results.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

## Fixed

Issues reported in previous releases which were fixed in this release:

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

# Root Cause Analysis for Regressions

List of RCAs in CSIT 24.06 for VPP performance regressions.
Not listing differences caused by known issues (uneven worker load
due to randomized RSS or other per-worker issues).
Also not listing tests which historically show large performance variance.

Contrary to issues, these genuine regressions do not limit usefulness
of CSIT testing. So even if they are not fixed
(e.g. when the regression is an expected consequence of added functionality),
they will not be re-listed in the next release report.

**#** | **JiraID**                                       | **Issue Description**
------|--------------------------------------------------|--------------------------------------------------------------
  1   |                                                  |

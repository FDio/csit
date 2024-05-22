---
title: "VPP Performance"
weight: 1
---

# CSIT 24.06 - VPP Performance

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 14, see
     [Environment Versioning]({{< ref "../../../infrastructure/fdio_csit_testbed_versioning" >}}).
   - **General Code Housekeeping**: Ongoing code optimizations and bug fixes.
   - **Trending and release testing**: Ndrpdr tests use newer code
     (MLRsearch 1.2.1) and configuration, gaining more stability and speed.
1. VPP PERFORMANCE TESTS
   - Added 2n-c7gn and 3n-icxd testbeds.
2. PRESENTATION AND ANALYTICS LAYER
   - [Performance dashboard](https://csit.fd.io/) got updated with the
     possibility to [search in tests](https://csit.fd.io/search/).
   - [Per Release Performance Comparisons](https://csit.fd.io/comparisons/) got
     updated with the function removing extreme outliers from data presented in
     the comparison table.

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

---
title: "DPDK Performance"
weight: 2
---

# Changes in {{< release_csit >}}

1. TEST FRAMEWORK
   - **CSIT test environment** version has been updated to ver. 11, see
     [Environment Versioning]({{< ref "infrastructure#Release Notes" >}}).
2. DPDK PERFORMANCE TESTS
   - No updates
3. DPDK RELEASE VERSION CHANGE
   - {{< release_csit >}} tested {{< release_dpdk >}}, as used by
     {{< release_vpp >}}.

# Known Issues

List of known issues in {{< release_csit >}} for DPDK performance tests:

 **#** | **JiraID**                                       | **Issue Description**
-------|--------------------------------------------------|---------------------------------------------------------------------------
 1     | [CSIT-1848](https://jira.fd.io/browse/CSIT-1848) | 2n-clx, 3n-alt: sporadic testpmd/l3fwd tests fail with no or low traffic.


## New

List of new issues in {{< release_csit >}} for DPDK performance tests:

 **#** | **JiraID**                                       | **Issue Description**
-------|--------------------------------------------------|---------------------------------------------------------------------------
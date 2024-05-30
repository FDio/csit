---
title: "FD.io CSIT"
type: "docs"
---

# Documentation Structure

1. OVERVIEW: General introduction to CSIT Performance Dashboard and CSIT itself.
   - **[CSIT-Dash]({{< relref "/overview/c_dash/design" >}})**: The design and
     the structure of CSIT-Dash dashboard.
   - **[CSIT]({{< relref "/overview/csit/" >}})**: The design of the
     [FD.io](https://fd.io/) CSIT system, and the description of the test
     scenarios, test naming and test tags.
2. METHODOLOGY
   - **[Overview]({{< relref "/methodology/overview/" >}})**: Terminology,
     per-thread resources, multi-core speedup, VPP forwarding modes and DUT
     state considerations.
   - **[Measurement]({{< relref "/methodology/measurements/" >}})**: Data plane
     throughput, packet latency and the telemetry.
   - **[Test]({{< relref "/methodology/test/" >}})**: Methodology of all tests
     used in CSIT.
   - **[Trending]({{< relref "/methodology/trending/" >}})**: A high-level
     design of a system for continuous performance measuring, trending and
     change detection for FD.io VPP SW data plane (and other performance tests
     run within CSIT sub-project).
   - **[Per-patch Testing]({{< relref "/methodology/per_patch_testing" >}})**:
     A methodology similar to trending analysis is used for comparing
     performance before a DUT code change is merged.
3. RELEASE NOTES: Performance tests executed in physical FD.io testbeds.
   - **[{{< release_csit >}}]({{< relref "/release_notes/current/" >}})**: The
     release notes of the current CSIT release.
   - **[Previous]({{< relref "/release_notes/previous/" >}})**: Archived release
     notes for the past releases.
4. INFRASTRUCTURE
   - **[FD.io DC Vexxhost Inventory]({{< relref "/infrastructure/fdio_dc_vexxhost_inventory" >}})**:
     Physical testbeds location.
   - **[FD.io DC Testbed Specifications]({{< relref "/infrastructure/fdio_dc_testbed_specifications" >}})**:
     Specification of the physical testbed infrastructure.
   - **[FD.io DC Testbed Configuration]({{< relref "/infrastructure/testbed_configuration/" >}})**:
     Configuration of the physical testbed infrastructure.
   - **[FD.io CSIT Testbed Versioning]({{< relref "/infrastructure/fdio_csit_testbed_versioning" >}})**:
     CSIT test environment versioning to track modifications of the test
     environment.
   - **[FD.io CSIT Logical Topologies]({{< relref "/infrastructure/fdio_csit_logical_topologies" >}})**:
     CSIT performance tests are executed on physical testbeds. Based on the
     packet path thru server SUTs, three distinct logical topology types are
     used for VPP DUT data plane testing.
   - **[VPP Startup Settings]({{< relref "/infrastructure/vpp_startup_settings" >}})**:
     List of common settings applied to all tests and test dependent settings.
5. [PERFORMANCE DASHBOARD]({{< dashboard_url >}})
   - **[Performance Trending]({{< dashboard_url >}}trending)**
   - **[Per Release Performance]({{< dashboard_url >}}report)**
   - **[Per Release Performance Comparisons]({{< dashboard_url >}}comparisons)**
   - **[Per Release Coverage Data]({{< dashboard_url >}}coverage)**
   - **[Test Jobs Statistics]({{< dashboard_url >}}stats)**
   - **[Failures and Anomalies]({{< dashboard_url >}}news)**
   - **[Search Tests]({{< dashboard_url >}}search)**
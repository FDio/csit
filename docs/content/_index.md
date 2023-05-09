---
title: "FD.io CSIT"
type: "docs"
---

# Documentation Structure

1. OVERVIEW: General introduction to CSIT Performance Dashboard and CSIT itself.
   - **C-Dash**: The design and the structure of C-Dash dashboard.
   - **CSIT**: The design of the [FD.io](https://fd.io/) CSIT system, and the
     description of the test scenarios, test naming and test tags.
2. METHODOLOGY
   - **Overview**: Terminology, per-thread resources, multi-core speedup, VPP
     forwarding modes and DUT state considerations.
   - **Measurement**: Data plane throughput, packet latency and the telemetry.
   - **Test**: Methodology of all tests used in CSIT.
   - **Trending**: A high-level design of a system for continuous performance
     measuring, trending and change detection for FD.io VPP SW data plane (and
     other performance tests run within CSIT sub-project).
   - **Per-patch Testing**: A methodology similar to trending analysis is used
     for comparing performance before a DUT code change is merged.
3. RELEASE NOTES: Performance tests executed in physical FD.io testbeds.
   - **CSIT rls2306**: The release notes of the current CSIT release.
   - **Previous**: Archived release notes for the past releases.
4. INFRASTRUCTURE
   - **FD.io DC Vexxhost Inventory**: Physical testbeds location.
   - **FD.io DC Testbed Specifications**: Specification of the physical
     testbed infrastructure.
   - **FD.io DC Testbed Configuration**: Configuration of the physical
     testbed infrastructure.
   - **FD.io CSIT Testbed Versioning**: CSIT test environment versioning to
     track modifications of the test environment.
   - **FD.io CSIT Logical Topologies**: CSIT performance tests are executed on
     physical testbeds. Based on the packet path thru server SUTs, three
     distinct logical topology types are used for VPP DUT data plane testing.
   - **VPP Startup Settings**: List of common settings applied to all tests and
     test dependent settings.
   - **TRex Traffic Generator**: Usage of TRex traffic generator and its traffic
     modes, profiles etc.

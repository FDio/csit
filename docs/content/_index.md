---
title: "FD.io CSIT"
type: "docs"
---

# Documentation Structure

1. OVERVIEW: General introduction to CSIT Performance Dashboard and CSIT itself.
   - **[CSIT-Dash](overview/c_dash)**: The design and the structure of
     CSIT-Dash dashboard.
   - **[CSIT](overview/csit)**: The design of the [FD.io](https://fd.io/)
     CSIT system, and the description of the test scenarios, test naming and
     test tags.
2. METHODOLOGY
   - **[Overview](methodology/overview)**: Terminology, per-thread
     resources, multi-core speedup, VPP forwarding modes and DUT state
     considerations.
   - **[Measurement](methodology/measurements)**: Data plane throughput, packet
     latency and the telemetry.
   - **[Test](methodology/test)**: Methodology of all tests used in CSIT.
   - **[Trending](methodology/trending)**: A high-level design of a system for
     continuous performance measuring, trending and change detection for FD.io
     VPP SW data plane (and other performance tests run within CSIT
     sub-project).
   - **[Per-patch Testing](methodology/per_patch_testing)**: A methodology
     similar to trending analysis is used for comparing performance before a DUT
     code change is merged.
3. RELEASE NOTES: Performance tests executed in physical FD.io testbeds.
   - **[CSIT rls2306](release_notes/csit_rls2306)**: The release notes of the
     current CSIT release.
   - **[Previous](release_notes/previous)**: Archived release notes for the past
     releases.
4. INFRASTRUCTURE
   - **[FD.io DC Vexxhost Inventory](infrastructure/fdio_dc_vexxhost_inventory)**:
     Physical testbeds location.
   - **[FD.io DC Testbed Specifications](infrastructure/fdio_dc_testbed_specifications)**:
     Specification of the physical testbed infrastructure.
   - **[FD.io DC Testbed Configuration](infrastructure/testbed_configuration)**:
     Configuration of the physical testbed infrastructure.
   - **[FD.io CSIT Testbed Versioning](infrastructure/fdio_csit_testbed_versioning)**:
     CSIT test environment versioning to track modifications of the test
     environment.
   - **[FD.io CSIT Logical Topologies](infrastructure/fdio_csit_logical_topologies)**:
     CSIT performance tests are executed on physical testbeds. Based on the
     packet path thru server SUTs, three distinct logical topology types are
     used for VPP DUT data plane testing.
   - **[VPP Startup Settings](infrastructure/vpp_startup_settings)**: List of
     common settings applied to all tests and test dependent settings.
   - **[TRex Traffic Generator](infrastructure/trex_traffic_generator)**: Usage
     of TRex traffic generator and its traffic modes, profiles etc.

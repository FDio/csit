---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT"
weight: 2
---

# Continuous System Integration and Testing

## CSIT Description

1. Development of software code for fully automated VPP code testing,
   functionality, performance, regression and new functions.
2. Execution of CSIT test suites on VPP code running on LF FD.io virtual and
   physical compute environments.
3. Integration with FD.io continuous integration systems (Gerrit, Jenkins and
   such).
4. Identified existing FD.io project dependencies and interactions:
   - vpp - Vector Packet Processing.
   - ci-management - Management repo for Jenkins Job Builder, script and
     management related to the Jenkins CI configuration.

## Project Scope

1. Automated regression testing of VPP code changes
   - Functionality of VPP data plane, network control plane, management plane
     against functional specifications.
   - Performance of VPP data plane including non-drop-rate packet throughput
     and delay, against established reference benchmarks.
   - Performance of network control plane against established reference
     benchmarks.
   - Performance of management plane against established reference benchmarks.
2. Test case definitions driven by supported and planned VPP functionality,
   interfaces and performance:
   - Uni-dimensional tests: Data plane, (Network) Control plane, Management
     plane.
   - Multi-dimensional tests: Use case driven.
3. Integration with FD.io Continuous Integration system including FD.io Gerrit
   and Jenkins
   - Automated test execution triggered by VPP-VERIFY jobs other VPP and CSIT
     project jobs.
4. Integration with LF VPP test execution environment
   - Functional tests execution on LF hosted VM environment.
   - Performance and functional tests execution on LF hosted physical compute
     environment.

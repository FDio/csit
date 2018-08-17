Introduction
============

This is FD.io CSIT (Fast Data i/o Continuous System Integration and
Testing) project report for |csit-release| system performance and
functional testing of |vpp-release|.

There is also a downloadable `PDF version of this report`_.

This report describes CSIT performance and functional tests delivered in
|csit-release|. A high-level overview is provided for each CSIT test
environment running in :abbr:`LF (Linux Foundation)` FD.io Continuous
Performance Labs. This is followed by summary of all executed tests
against the |vpp-release| and associated FD.io projects and sub-systems
(Honeycomb, DPDK, NSH_SFC, DMM), |csit-release| release notes, result
highlights and known issues discovered in CSIT. More detailed
description of each environment, pointers to CSIT test code
documentation and detailed test resuls with links to the source data
files are also provided.

|csit-release| report contains following main sections and sub-sections:

#. **Introduction**: General introduction to CSIT project.

   - **Introduction**: This section.
   - **Test Scenarios Overview**: A brief overview of test scenarios
     covered in this report.
   - **Physical Testbeds**: Description of physical testbeds.
   - **Performance Test Methodology**: Benchmarking methodologies.

#. **VPP Performance**: VPP performance tests executed in physical
   FD.io testbeds.

   - **Overview**: Tested logical topologies, test coverage and naming
     specifics.
   - **Release Notes**: Changes in |csit-release|, added tests,
     environment or methodology changes, known issues.
   - **Packet Throughput**: NDR, PDR throughput graphs based on results
     from repeated same test job executions to verify repeatibility of
     measurements.
   - **Packet Latency**: Latency graphs based on results from test job
     executions.
   - **Speedup Multi-Core**: NDR, PDR throughput multi-core speedup
     graphs based on results from test job executions.
   - **HTTP/TCP Performance**: HTTP/TCP VPP test server performance
     graphs.
   - **Comparisons**: Performance comparisons between VPP releases and
     between different testbed types.
   - **Throughput Trending**: References to continuous VPP performance
     trending.
   - **Test Environment**: Performance test environment configuration.
   - **Documentation**: Documentation of K8s Pod/Container orchestration
     in CSIT and pointers to CSIT source code documentation for VPP
     performance tests.

#. **DPDK Performance**: DPDK performance tests executed in physical
   FD.io testbeds.

   - **Overview**: Tested logical topologies, test coverage.
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Packet Throughput**: NDR, PDR throughput graphs based on results
     from repeated same test job executions to verify repeatibility of
     measurements.
   - **Packet Latency**: Latency graphs based on results from test job
     executions.
   - **Comparisons**: Performance comparisons between DPDK releases and
     between different testbed types.
   - **Throughput Trending**: References to regular DPDK performance
     trending.
   - **Test Environment**: Performance test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     DPDK performance tests.

#. **VPP Functional**: VPP functional tests executed in virtual FD.io
   testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, added tests,
     environment or methodology changes, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     VPP functional tests.

#. **Honeycomb Functional**: Honeycomb functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     Honeycomb functional tests.

#. **NSH_SFC Functional**: NSH_SFC functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     NSH_SFC functional tests.

#. **DMM Functional**: DMM functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     DMM functional tests.

#. **Detailed Results**: Detailed result tables auto-generated from CSIT
   test job executions using RF (Robot Framework) output files as
   sources.

   - **VPP Performance NDR/PDR**: VPP NDR/PDR throughput and latency.
   - **VPP Performance MRR**: VPP MRR throughput.
   - **VPP K8s Container Memif**: VPP K8s Container/Pod topologies
     NDR/PDR throughput.
   - **DPDK Performance**: DPDK Testpmd and L3fwd NDR/PDR throughput
     and latency.
   - **VPP Functional**: Detailed VPP functional results.
   - **Honeycomb Functional**: Detailed HoneyComb functional results.
   - **NSH_SFC Functional**: Detailed nsh-plugin functional results.
   - **DMM Functional**: Detailed DMM functional results.

#. **Test Configuration**: VPP DUT configuration data based on VPP API
   Test (VAT) Commands History auto-generated from CSIT test job
   executions using RF output files as sources.

   - **VPP Performance NDR/PDR**: Configuration data.
   - **VPP Performance MRR**: Configuration data.
   - **VPP K8s Container Memif**: Configuration data.
   - **VPP Functional**: Configuration data.

#. **Test Operational Data**: VPP DUT operational data auto-generated
   from CSIT test job executions using RFoutput files as sources.

   - **VPP Performance NDR/PDR**: VPP `show run` outputs under test
     load.

#. **CSIT Framework Documentation**: Description of the overall FD.io
   CSIT framework.

   - **Design**: Framework modular design hierarchy.
   - **Test naming**: Test naming convention.
   - **Presentation and Analytics Layer**: Description of PAL CSIT
     analytics module.
   - **CSIT RF Tags Descriptions**: CSIT RF Tags used for test suite and
     test case grouping and selection.

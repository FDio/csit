Report Structure
================

FD.io |csit-release| report contains system performance and functional
testing data of |vpp-release|. `PDF version of this report`_ is
available for download.

|csit-release| report is structured as follows:

#. INTRODUCTION: General introduction to FD.io |csit-release|.

   - **Introduction**: This section.
   - **Test Scenarios Overview**: A brief overview of test scenarios
     covered in this report.
   - **Physical Testbeds**: Description of physical testbeds.
   - **Test Methodology**: Performance benchmarking and functional test
     methodologies.

#. VPP PERFORMANCE: VPP performance tests executed in physical
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

#. DPDK PERFORMANCE: DPDK performance tests executed in physical
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

#. VPP FUNCTIONAL: VPP functional tests executed in virtual FD.io
   testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, added tests,
     environment or methodology changes, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     VPP functional tests.

#. HONEYCOMBE FUNCTIONAL: Honeycomb functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     Honeycomb functional tests.

#. NSH_SFC FUNCTIONAL: NSH_SFC functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     NSH_SFC functional tests.

#. DMM FUNCTIONAL: DMM functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: Tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes**: Changes in |csit-release|, known issues.
   - **Test Environment**: Functional test environment configuration.
   - **Documentation**: Pointers to CSIT source code documentation for
     DMM functional tests.

#. DETAILED RESULTS: Detailed result tables auto-generated from CSIT
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

#. TEST CONFIGURATION: VPP DUT configuration data based on VPP API
   Test (VAT) Commands History auto-generated from CSIT test job
   executions using RF output files as sources.

   - **VPP Performance NDR/PDR**: Configuration data.
   - **VPP Performance MRR**: Configuration data.
   - **VPP K8s Container Memif**: Configuration data.
   - **VPP Functional**: Configuration data.

#. TEST OPERATIONAL DATA: VPP DUT operational data auto-generated
   from CSIT test job executions using RFoutput files as sources.

   - **VPP Performance NDR/PDR**: VPP `show run` outputs under test
     load.

#. CSIT FRAMEWORK DOCUMENTATION: Description of the overall FD.io
   CSIT framework.

   - **Design**: Framework modular design hierarchy.
   - **Test naming**: Test naming convention.
   - **Presentation and Analytics Layer**: Description of PAL CSIT
     analytics module.
   - **CSIT RF Tags Descriptions**: CSIT RF Tags used for test suite and
     test case grouping and selection.

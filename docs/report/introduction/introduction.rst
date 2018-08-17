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

#. **Introduction**: general introduction to CSIT project.

   - **Introduction**: this section.
   - **Test Scenarios Overview**: a brief overview of test scenarios
     covered in this report.
   - **Physical Testbeds**: description of physical testbeds.
   - **Performance Test Methodology**: benchmarking methodologies.

#. **VPP Performance**: VPP performance tests executed in physical
   FD.io testbeds.

   - **Overview**: tested logical topologies, test coverage and naming
     specifics.
   - **Release Notes**: changes in |csit-release|, added tests,
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
   - **Throughput Trending**: references to continuous VPP performance
     trending.
   - **Test Environment**: performance test environment configuration.
   - **Documentation**: documentation of K8s Pod/Container orchestration
     in CSIT and pointers to CSIT source code documentation for VPP
     performance tests.

#. **DPDK Performance**: DPDK performance tests executed in physical
   FD.io testbeds.

   - **Overview**: tested logical topologies, test coverage.
   - **Release Notes**: changes in |csit-release|, known issues.
   - **Packet Throughput**: NDR, PDR throughput graphs based on results
     from repeated same test job executions to verify repeatibility of
     measurements.
   - **Packet Latency**: Latency graphs based on results from test job
     executions.
   - **Comparisons**: Performance comparisons between VPP releases and
     between different testbed types.
   - **Test Environment**: performance test environment configuration.
   - **Documentation**: pointers to CSIT source code documentation for
     DPDK performance tests.

#. **VPP Functional**: VPP functional tests executed in virtual FD.io
   testbeds.

   - **Overview**: tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes** - changes in |csit-release|, added tests,
     environment or methodology changes, known issues.
   - **Test Environment**: functional test environment configuration.
   - **Documentation**: pointers to CSIT source code documentation for
     VPP functional tests.

#. **Honeycomb Functional**: Honeycomb functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes** - changes in |csit-release|, known issues.
   - **Test Environment**: functional test environment configuration.
   - **Documentation**: pointers to CSIT source code documentation for
     Honeycomb functional tests.

#. **NSH_SFC Functional**: NSH_SFC functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes** - changes in |csit-release|, known issues.
   - **Test Environment**: functional test environment configuration.
   - **Documentation**: pointers to CSIT source code documentation for
     NSH_SFC functional tests.

#. **DMM Functional**: DMM functional tests executed in
   virtual FD.io testbeds.

   - **Overview**: tested virtual topologies, test coverage and naming
     specifics;
   - **Release Notes** - changes in |csit-release|, known issues.
   - **Test Environment**: functional test environment configuration.
   - **Documentation**: pointers to CSIT source code documentation for
     DMM functional tests.

#. **Detailed Results**: detailed result tables auto-generated from CSIT
   test job executions using RF (Robot Framework) output files as
   sources.

   - **VPP Performance NDR/PDR**: VPP NDR/PDR throughput and latency.
   - **VPP Performance MRR**: VPP MRR throughput.
   - **VPP K8s Container Memif**: VPP K8s Container/Pod topologies
     NDR/PDR throughput.
   - **DPDK Performance**: DPDK Testpmd and L3fwd NDR/PDR throughput
     and latency.
   - **VPP Functional**: detailed VPP functional results.
   - **Honeycomb Functional**: detailed HoneyComb functional results.
   - **NSH_SFC Functional**: detailed nsh-plugin functional results.
   - **DMM Functional**: detailed DMM functional results.

#. **Test Configuration**: VPP DUT configuration data based on VPP API
   Test (VAT) Commands History auto-generated from CSIT test job
   executions using RF output files as sources.

   - **VPP Performance NDR/PDR**: configuration data.
   - **VPP Performance MRR**: configuration data.
   - **VPP K8s Container Memif**: configuration data.
   - **VPP Functional**: configuration data.

#. **Test Operational Data**: VPP DUT operational data auto-generated
   from CSIT test job executions using RFoutput files as sources.

   - **VPP Performance NDR/PDR**: VPP `show run` outputs under test
     load.

#. **CSIT Framework Documentation**: description of the overall FD.io
   CSIT framework.

   - **Design**: framework modular design hierarchy.
   - **Test naming**: test naming convention.
   - **Presentation and Analytics Layer**: description of PAL CSIT
     analytics module.
   - **CSIT RF Tags Descriptions**: CSIT RF Tags used for test suite and
     test case grouping and selection.

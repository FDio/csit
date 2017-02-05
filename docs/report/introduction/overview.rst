Overview
========

This is the **F**\ast **D**\ata **I**/**O** Project (**FD.io**) **C**\ontinuous
**S**\ystem **I**\ntegration and **T**\esting (**CSIT**) project report for CSIT
|release| system testing of VPP-17.01 release.

The report describes CSIT functional and performance tests and their
continuous execution delivered in CSIT |release|. A high-level overview is
provided for each CSIT test environment running in Linux Foundation (LF) FD.io
Continuous Performance Labs. This is followed by summary of all executed tests
against the VPP-17.01 release and associated sub-systems (HoneyComb, DPDK),
CSIT |release| release notes, result highlights and known issues. More
detailed description of each environment, pointers to CSIT test code
documentation and detailed test resuls with links to the source data files are
also provided.

CSIT |release| report contains following main sections and sub-sections:

#. **Introduction** - general introduction to CSIT project; *Overview* -
   this section; *CSIT Test Naming* - CSIT general naming convention for test
   suites and test cases, important to recognize the high-level test content
   and interpret reported results; *General Notes* - general notes related to
   this report.

#. **VPP Performance Tests** - VPP performance tests executed in physical
   FD.io testbeds; *Overview* - tested topologies, test coverage and naming
   specifics, methodology for multi-core, packet throughput and latency, and
   KVM VM vhost tests; *CSIT Release Notes* - changes in CSIT |release|, added
   tests, performance changes, environment or methodology changes, known CSIT
   issues, tests to be added; *Packet Throughput Graphs* and *Packet Latency
   Graphs* - plotted NDR, PDR throughput and latency results from multiple
   test job executions; *Test Environment* - environment description ;
   *Documentation* - source code documentation for VPP performance tests.

#. **Testpmd Performance Tests** - Testpmd performance tests executed in
   physical FD.io testbeds; *Overview* - tested topologies, test coverage;
   *CSIT Release Notes* - changes in CSIT |release|, any known CSIT issues;
   *Tests to Be Added* - performance tests to be added in the next revision of
   CSIT |release| report; *Packet Throughput Graphs* and *Packet Latency Graphs*
   - plotted NDR, PDR throughput and latency results from multiple test job
   executions; *Test Environment* - environment description; *Documentation* -
   source code documentation for Testpmd performance tests.

#. **VPP Functional Tests** - VPP functional tests executed in virtual
   FD.io testbeds; *Overview* - tested virtual topologies, test coverage and
   naming specifics; *CSIT Release Notes* - changes in CSIT |release|, added
   tests, environment or methodology changes, known CSIT issues, tests to be
   added; *Test Environment* - environment description ; *Documentation* -
   source code documentation for VPP functional tests.

#. **HoneyComb Functional Tests** - HoneyComb functional tests executed in
   virtual FD.io testbeds; *Overview* - tested virtual topologies, test
   coverage and naming specifics; *CSIT Release Notes* - changes in CSIT
   |release|, added tests, environment or methodology changes, known CSIT issues,
   tests to be added; *Test Environment* - environment description ;
   *Documentation* - source code documentation for Honeycomb functional tests.

#. **VPP Unit Tests** - refers to VPP functional unit tests executed as
   part of vpp make test verify option within the FD.io VPP project; listed in
   this report to give a more complete view about executed VPP functional tests;
   *Overview* - short overview of unit test framework and executed tests;
   *Documentation* - source code documentation of VPP unit tests.

#. **Detailed Test Results** - auto-generated results from CSIT jobs
   executions using CSIT Robot Framework output files as source data; *VPP
   Performance Results*, *Testpmd Performance Results*, *VPP Functional
   Results*, *HoneyComb Functional Results*, *VPPtest Functional Results*.

Overview
========

This is the **F**\ast **D**\ata **I**/**O** Project (**FD.io**) **C**\ontinuous
**S**\ystem **I**\ntegration and **T**\esting (**CSIT**) project report for
CSIT-|release| system testing of |vpp-release|.

This is the full html version, there is also a reduced
`PDF version of this report`_.

The report describes CSIT functional and performance tests and their
continuous execution delivered in CSIT-|release|. A high-level overview is
provided for each CSIT test environment running in :abbr:`LF (Linux Foundation)`
FD.io Continuous Performance Labs. This is followed by summary of all executed
tests against the |vpp-release| and associated FD.io projects and sub-systems
(Honeycomb, DPDK, NSH_SFC), CSIT-|release| release notes, result highlights and
known issues discovered in CSIT. More detailed description of each environment,
pointers to CSIT test code documentation and detailed test resuls with links to
the source data files are also provided.

CSIT-|release| report contains following main sections and sub-sections:

#. **Introduction** - general introduction to CSIT project; *Overview* -
   this section; *CSIT Test Naming* - CSIT general naming convention for test
   suites and test cases, important to recognize the high-level test content
   and interpret reported results; *General Notes* - general notes related to
   this report.

#. **VPP Performance Tests** - VPP performance tests executed in physical
   FD.io testbeds; *Overview* - tested topologies, test coverage and naming
   specifics, methodology for multi-core, packet throughput and latency, and
   KVM VM vhost tests; *CSIT Release Notes* - changes in CSIT-|release|, added
   tests, performance changes, environment or methodology changes, known CSIT
   issues; *Packet Throughput Graphs* and *Packet Latency
   Graphs* - plotted NDR, PDR throughput and latency results from multiple
   test job executions; *Throughput Speedup Multi-Core* - plotted core
   configuration speedup comparision; *Test Environment* - environment
   description; *VPP HTTP Server Performance Results* - plotted HTTP Server
   performance; *Documentation* - CSIT source code documentation for VPP
   performance tests.

#. **DPDK Performance Tests** - DPDK performance tests executed in
   physical FD.io testbeds; *Overview* - tested topologies, test coverage;
   *CSIT Release Notes* - changes in CSIT-|release|, any known CSIT issues;
   *Packet Throughput Graphs* and *Packet Latency Graphs*
   - plotted NDR, PDR throughput and latency results from multiple test job
   executions; *Test Environment* - environment description; *Documentation* -
   CSIT source code documentation for DPDK performance tests.

#. **VPP Functional Tests** - VPP functional tests executed in virtual
   FD.io testbeds; *Overview* - tested virtual topologies, test coverage and
   naming specifics; *CSIT Release Notes* - changes in CSIT-|release|, added
   tests, environment or methodology changes, known CSIT issues, tests to be
   added; *Test Environment* - environment description ; *Documentation* -
   source code documentation for VPP functional tests.

#. **Honeycomb Functional Tests** - Honeycomb functional tests executed in
   virtual FD.io testbeds; *Overview* - tested virtual topologies, test
   coverage and naming specifics; *CSIT Release Notes* - changes in CSIT
   |release|, added tests, environment or methodology changes, known CSIT issues;
   *Test Environment* - environment description ;
   *Documentation* - source code documentation for Honeycomb functional tests.

#. **NSH_SFC Functional Tests** - NSH_SFC functional tests executed in
   virtual FD.io testbeds; *Overview* - tested virtual topologies, test
   coverage and naming specifics; *CSIT Release Notes* - changes in CSIT
   |release|, added tests, environment or methodology changes, known CSIT issues;
   *Test Environment* - environment description ;
   *Documentation* - source code documentation for NSH_SFC functional tests.

#. **Detailed Test Results** - auto-generated results from CSIT jobs
   executions using CSIT Robot Framework output files as source data; *VPP
   Performance Results*, *DPDK Performance Results*, *VPP Functional
   Results*, *Honeycomb Functional Results*, *VPPtest Functional Results*.

#. **Test Configuration** - auto-generated DUT configuration data from CSIT jobs
   executions using CSIT Robot Framework output files as source data; *VPP
   Performance Test Configs*, *VPP Functional Test Configs*.

#. **Test Operational Data** - auto-generated DUT operational data from CSIT jobs
   executions using CSIT Robot Framework output files as source data; *VPP
   Performance Operational Data*.

#. **CSIT Framework Documentation** - description of the overall CSIT
   framework design hierarchy, CSIT test naming convention, followed by
   description of Presentation and Analytics Layer (PAL) introduced in
   CSIT-|release|.
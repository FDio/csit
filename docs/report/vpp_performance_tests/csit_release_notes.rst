CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added VPP performance tests

   - **L2BD MAC scale tests**

     - VPP L2 Bridge-Domain with MAC learning and large size L2FIB (10k,
       100k, 1M MACs), tested in NIC-to-NIC and VM vhost topologies.

   - **Linux Container VPP memif tests**

     - Tests with VPP in L2 Bridge-Domain configuration connecting over
       memif virtual interfaces to VPPs running in LXCs;

   - **Docker Container VPP memif tests**

     - Tests with VPP in L2 Cross-Connect configuration connecting over
       memif virtual interfaces VPPs running in Docker containers;

   - **Container Topologies Orchestrated by K8s with VPP memif tests**

     - Tests with VPP in L2 Cross-Connect and Bridge-Domain configurations
       connecting over memif virtual interfaces VPPs running in Docker
       containers, with service chain topologies orchestrated by Kubernetes;

   - **Stateful Security Groups**

     - m-thread m-core VPP stateful and stateless security-groups tests;

   - **MAC-IP binding**

     - MACIP input access-lists, single-thread single-core and m-thread
       m-core tests;

#. Presentation and Analytics Layer

     - New Presentation and Analytics Layer (PAL) for automated CSIT test
       results analysis and presentation, including statistical analysis
       of results repeatibility and test report auto-generation;

Performance Improvements
------------------------

Substantial improvements in measured packet throughput have been observed in a
number of CSIT |release| tests listed below, with relative increase of
double-digit percentage points. Relative improvements for this release are
calculated against the test results listed in CSIT |release-1| report. The
comparison is calculated between the mean values based on collected and
archived test results' samples for involved VPP releases. Standard deviation
has been also listed for CSIT |release|. Performance numbers since release
VPP-16.09 are provided for reference.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_improvements/performance_improvements_ndr_top.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{ m{1.5cm} m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/performance_improvements_ndr_top.csv}
      }


PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_improvements/performance_improvements_pdr_top.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{ m{1.5cm} m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/performance_improvements_pdr_top.csv}
      }


Measured improvements are in line with VPP code optimizations listed in
`VPP-17.10 release notes
<https://docs.fd.io/vpp/17.10/release_notes_1710.html>`_.

Other Performance Changes
-------------------------

Other changes in measured packet throughput, with either minor relative increase
or decrease, have been observed in a number of CSIT |release| tests listed
below. Relative changes are calculated against the test results listed in CSIT
|release-1| report.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_improvements/performance_improvements_ndr_low.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{ m{1.5cm} m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/performance_improvements_ndr_low.csv}
      }


PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

.. only:: html

   .. csv-table::
      :align: center
      :file: performance_improvements/performance_improvements_pdr_low.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{ m{1.5cm} m{4cm} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_tmp/src/vpp_performance_tests/performance_improvements/performance_improvements_pdr_low.csv}
      }


Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP performance tests:

+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                           | Jira ID    | Description                                                     |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | Vic1385 and Vic1227 low performance.            | VPP-664    | Low NDR performance.                                            |
|   |                                                 |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | Sporadic NDR discovery test failures on x520.   | CSIT-750   | Suspected issue with HW settings (BIOS, FW) in LF               |
|   |                                                 |            | infrastructure. Issue can't be replicated outside LF.           |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 3 | VPP in 2t2c setups - large variation            | CSIT-568   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across      |            | throughput. Applies to XL710 and X710 NICs, x520 NICs are fine. |
|   | multiple test runs with xl710 and x710 NICs.    |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 4 | Lower than expected NDR throughput with         | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+


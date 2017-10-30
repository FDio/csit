CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Test environment changes in VPP data plane performance tests:

   - Further characterization and optimizations of VPP vhost-user and VM test
     methodology and test environment;

     - Tests with varying Qemu virtio queue (a.k.a. vring) sizes:
       [vr256] default 256 descriptors, [vr1024] 1024 descriptors to
       optimize for packet throughput;

     - Tests with varying Linux :abbr:`CFS (Completely Fair Scheduler)`
       settings: [cfs] default settings, [cfsrr1] :abbr:`CFS (Completely Fair
       Scheduler)` RoundRobin(1) policy applied to all data plane threads
       handling test packet path including all VPP worker threads and all Qemu
       testpmd poll-mode threads;

     - Resulting test cases are all combinations with [vr256,vr1024] and
       [cfs,cfsrr1] settings;

     - For more detail see performance results observations section in
       this report;

#. Code updates and optimizations in CSIT performance framework:

   - Complete CSIT framework code revision and optimizations as descried
     on CSIT wiki page `Design_Optimizations
     <https://wiki.fd.io/view/CSIT/Design_Optimizations>`_.

   - For more detail see the :ref:`CSIT Framework Design <csit-design>` section
     in this report;

#. Changes to CSIT driver for TRex Traffic Generator:

   - Complete refactor of TRex CSIT driver;

   - Introduction of packet traffic profiles to improve usability and
     manageability of traffic profiles for a growing number of test
     scenarios.

   - Support for packet traffic profiles to test IPv4/IPv6 stateful and
     stateless DUT data plane features;

#. Added VPP performance tests

   - **Linux Container VPP memif virtual interface tests**

     - New VPP Memif virtual interface (shared memory interface) tests
       with L2 Bridge-Domain switched-forwarding;

   - **Stateful Security Groups**

     - New m-thread m-core VPP stateful security-groups tests;

   - **MAC-IP binding**

     - New MACIP iACL single-thread single-core and m-thread m-core tests;

     - Statistical analysis of repeatibility of results;

Performance Improvements
------------------------

Substantial improvements in measured packet throughput have been observed in a
number of CSIT |release| tests listed below, with relative increase of
double-digit percentage points. Relative improvements for this release are
calculated against the test results listed in CSIT |release-1| report. The
comparison is calculated between the mean values based on collected and
archived test results' samples for involved VPP releases. Standard deviation
has been also listed for CSIT |release|. VPP-16.09 and VPP-17.01 numbers are
provided for reference.

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
| 4 | Lower than expected NDR and PDR throughput with | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+


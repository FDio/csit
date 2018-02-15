CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added VPP performance tests

   - **Container Topologies Orchestrated by K8s with VPP memif tests**

   - Added tests with VPP in L2 Cross-Connect and Bridge-Domain
     configurations containers, with service chain topologies orchestrated by
     Kubernetes. Added following forwarding topologies: i) "Parallel" with
     packets flowing from NIC via VPP to container and back to VPP and NIC;
     ii) "Chained" a.k.a. "Snake" with packets flowing via VPP to container,
     back to VPP, to next container, back to VPP and so on until the last
     container in chain, then back to VPP and NIC; iii) "Horizontal" with
     packets flowing via VPP to container, then via "horizontal" memif to
     next container, and so on until the last container, then back to VPP and
     NIC;.

   - **VPP TCP/IP stack**

     - Added tests for VPP TCP/IP stack using VPP built-in HTTP server.
       WRK traffic generator is used as a client-side;

   - **SRv6 tests**

     - Initial SRv6 (Segment Routing IPv6) tests verifying performance of
       IPv6 and SRH (Segment Routing Header) encapsulation, decapsulation,
       lookups and rewrites based on configured End and End.DX6 SRv6 egress
       functions;

   - **IPSecSW tests**

     - SW computed IPSec encryption with AES-GCM, CBC-SHA1 ciphers, in
       combination with IPv4 routed-forwarding;

#. Presentation and Analytics Layer

     - Added throughput speedup analysis for multi-core and multi-thread
       VPP tests into Presentation and Analytics Layer (PAL) for automated
       CSIT test results analysis;

#. Other improvements

     - **Framework optimizations**

       - Ability to run CSIT framework on ARM architecture;

       - Overall stability improvements;

Performance Changes
-------------------

Substantial changes in measured packet throughput have been observed in a
number of CSIT |release| tests listed below. Relative changes for this release
are calculated against the test results listed in CSIT |release-1| report. The
comparison is calculated between the mean values based on collected and
archived test results' samples for involved VPP releases. Standard deviation
has been also listed for CSIT |release|.

NDR Throughput: Best 20 Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../../_build/_static/vpp/performance-changes-ndr-1t1c-top.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{5cm} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_build/_static/vpp/performance-changes-ndr-1t1c-top.csv}
      }

NDR Throughput: Worst 20 Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~l

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../../_build/_static/vpp/performance-changes-ndr-1t1c-bottom.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{6cm} m{#1} m{#1} m{#1} m{#1} m{#1}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_build/_static/vpp/performance-changes-ndr-1t1c-bottom.csv}
      }

.. only:: html

      NDR Throughput: All Changes
      ~~~~~~~~~~~~~~~~~~~~~~~~~~~

      Complete results for all NDR tests are available in a CSV and pretty
      ASCII formats:

        - `csv format for 1t1c <../_static/vpp/performance-changes-ndr-1t1c-full.csv>`_,
        - `csv format for 2t2c <../_static/vpp/performance-changes-ndr-2t2c-full.csv>`_,
        - `csv format for 4t4c <../_static/vpp/performance-changes-ndr-4t4c-full.csv>`_,
        - `pretty ASCII format for 1t1c <../_static/vpp/performance-changes-ndr-1t1c-full.txt>`_,
        - `pretty ASCII format for 2t2c <../_static/vpp/performance-changes-ndr-2t2c-full.txt>`_,
        - `pretty ASCII format for 4t4c <../_static/vpp/performance-changes-ndr-4t4c-full.txt>`_.

PDR Throughput: Best 20 Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../../_build/_static/vpp/performance-changes-pdr-1t1c-top.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{5cm} m{#2} m{#2} m{#2} m{#2} m{#2}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_build/_static/vpp/performance-changes-pdr-1t1c-top.csv}
      }

PDR Throughput: Worst 20 Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. only:: html

   .. csv-table::
      :align: center
      :file: ../../../_build/_static/vpp/performance-changes-pdr-1t1c-bottom.csv

.. only:: latex

   .. raw:: latex

      \makeatletter
      \csvset{
        perfimprovements column width/.style={after head=\csv@pretable\begin{longtable}{m{6cm} m{#2} m{#2} m{#2} m{#2} m{#2}}\csv@tablehead},
      }
      \makeatother

      {\tiny
      \csvautobooklongtable[separator=comma,
        respect all,
        no check column count,
        perfimprovements column width=1cm,
        late after line={\\\hline},
        late after last line={\end{longtable}}
        ]{../_build/_static/vpp/performance-changes-pdr-1t1c-bottom.csv}
      }

.. only:: html

      PDR Throughput: All Changes
      ~~~~~~~~~~~~~~~~~~~~~~~~~~~

            Complete results for all PDR tests are available in a CSV and pretty
            ASCII formats:

              - `csv format for 1t1c <../_static/vpp/performance-changes-pdr-1t1c-full.csv>`_,
              - `csv format for 2t2c <../_static/vpp/performance-changes-pdr-2t2c-full.csv>`_,
              - `csv format for 4t4c <../_static/vpp/performance-changes-pdr-4t4c-full.csv>`_,
              - `pretty ASCII format for 1t1c <../_static/vpp/performance-changes-pdr-1t1c-full.txt>`_,
              - `pretty ASCII format for 2t2c <../_static/vpp/performance-changes-pdr-2t2c-full.txt>`_,
              - `pretty ASCII format for 4t4c <../_static/vpp/performance-changes-pdr-4t4c-full.txt>`_.

Measured improvements are in line with VPP code optimizations listed in
`VPP-17.10 release notes
<https://docs.fd.io/vpp/17.10/release_notes_1710.html>`_.

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP performance tests:

+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                           | Jira ID    | Description                                                     |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | Vic1385 and Vic1227 low performance.            | VPP-664    | Low NDR performance.                                            |
|   |                                                 |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | Sporadic NDR discovery test failures on x520.   | CSIT-750   | Suspected issue with HW combination of X710-X520 in LF          |
|   |                                                 |            | infrastructure. Issue can't be replicated outside LF.           |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 3 | VPP in 2t2c setups - large variation            | CSIT-568   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across      |            | throughput. Applies to XL710 and X710 NICs, x520 NICs are fine. |
|   | multiple test runs with xl710 and x710 NICs.    |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 4 | Lower than expected NDR throughput with         | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+

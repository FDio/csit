CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. VPP performance test environment changes:

   - Further characterization and optimizations of VM and vhost-user
     test methodology and test environment;

     - Tests with varying Qemu virtio queue sizes (vring qsz): 256
       descriptors Qemu default (vr256), 1024 descriptors Qemu more
       optimal for performance (vr1024);

     - Tests with varying Linux CFS (Completely Fair Scheduler)
       settings: default settings (cfs), RoundRobin(1) policy applied
       to all data plane threads handling test packet path including all
       VPP worker threads and all Qemu testpmd poll-mode threads
       (cfsrr1);

     - Resulting test cases are combinations of [vr256,vr1024] and
       [cfs,cfsrr1];

     - Refer performance test results observations section in this
       report;

#. CSIT performance framework updates and optimizations:

   - Complete CSIT framework code review, optimizations and automation
     KeyWords refactoring.

   - Refer to CSIT Framework Design section in this report;

#. TRex Traffic Generator changes

   - Complete refactor of TRex CSIT driver;

   - Introduction of packet traffic profiles to improve usability and
     manageability of traffic profiles for a growing number of test
     scenarios.

   - Support for packet traffic profiles to test IPv4/IPv6 stateful and
     stateless DUT data plane features;

#. Added VPP performance tests

   - **Linux Container VPP memif virtual interface tests**

     - VPP Memif virtual interface (shared memory interface) tests
       interconnecting two VPP instances over memif. VPP vswitch
       instance runs in bare-metal user-mode handling Intel x520 NIC
       10GbE interfaces and connecting over memif (Master side) virtual
       interfaces to another instance of VPP running in bare-metal Linux
       Container (LXC) with memif virtual interfaces (Slave side). LXC
       runs in priviliged mode with VPP data plane worker threads pinned
       to dedicated physical CPU cores per usual CSIT practice. Both VPP
       run the same version of software.

   - **Stateful Security Groups**

   - **VM vhost use cases**

Performance Improvements
------------------------

Substantial improvements in measured packet throughput have been
observed in a number of CSIT |release| tests listed below, with relative
increase  of double-digit percentage points. Relative improvements are
calculated against the test results listed in CSIT |release-1| report.
VPP-16.09 numbers are provided for reference.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

.. csv-table::
    :align: center
    :header-rows: 1
    :file: ../../../docs/report/vpp_performance_tests/performance_improvements/ndr_throughput.csv

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

.. csv-table::
    :align: center
    :header-rows: 1
    :file: ../../../docs/report/vpp_performance_tests/performance_improvements/pdr_throughput.csv

Measured improvements are in line with VPP code optimizations listed in
`VPP-17.07 release notes
<https://docs.fd.io/vpp/17.07/release_notes_1707.html>`_.

Other Performance Changes
-------------------------

Other changes in measured packet throughput, with either minor relative
increase or decrease, have been observed in a number of CSIT |release|
tests listed below. Relative changes are calculated against the test
results listed in CSIT |release-1| report.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

.. csv-table::
    :align: center
    :header-rows: 1
    :file: ../../../docs/report/vpp_performance_tests/performance_improvements/ndr_throughput_others.csv

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

.. csv-table::
    :align: center
    :header-rows: 1
    :file: ../../../docs/report/vpp_performance_tests/performance_improvements/pdr_throughput_others.csv


Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP performance tests:

+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                           | Jira ID    | Description                                                     |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | NDR discovery test failures 1518B frame size    | VPP-663    | VPP reporting errors: dpdk-input Rx ip checksum errors.         |
|   | for ip4scale200k, ip4scale2m scale IPv4 routed- |            | Observed frequency: all test runs.                              |
|   | forwarding tests. ip4scale20k tests are fine.   |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | Vic1385 and Vic1227 low performance.            | VPP-664    | Low NDR performance.                                            |
|   |                                                 |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 3 | Sporadic NDR discovery test failures on x520.   | CSIT-750   | Suspected issue with HW settings (BIOS, FW) in LF               |
|   |                                                 |            | infrastructure. Issue can't be replicated outside LF.           |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 4 | VPP in 2t2c setups - large variation            | CSIT-568   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across      |            | throughput. Applies to XL710 and X710 NICs, x520 NICs are fine. |
|   | multiple test runs with xl710 and x710 NICs.    |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 5 | Lower than expected NDR and PDR throughput with | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+


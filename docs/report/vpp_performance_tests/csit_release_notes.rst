CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. VPP performance test environment changes

   - Further optimizations of VM and vhost-user test environment - various
     Qemu virtio queue size testing with value of 256 and 1024. Applied
     Linux CFS optimization to run VPP worker threads and Qemu worker threads
     with highest priority.

#. VPP performance test framework changes

   - Full code review, optimization and refactor.

#. T-rex changes

   - Full refactor of T-rex driver and introduce of traffic profiles that
     improves readability, manageability of traffic profiles for various
     test scenarios.

#. Added VPP performance tests

   - **LXC memif**

     - Memif interface tests interconnecting two VPP instances on single SUT.
       Master VPP instance running on native OS with Intel x520 NIC and guest
       VPP instance running in Linux Container (LXC) doing the L2 cross
       connect loop. LXC running in privileged mode is pinned to dedicated
       cores. All VPP instances are same version.

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
    :header: VPP Functionality,Test Name,VPP-16.09 [Mpps],VPP-17.01 [Mpps],VPP-17.04 [Mpps],VPP-17.07 mean [Mpps],VPP-17.07 stdev [Mpps],17.04 to 17.07 change
    :file: ../../../docs/report/vpp_performance_tests/performance_improvements/ndr_throughput.csv

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

.. csv-table::
    :align: center
    :header: VPP Functionality,Test Name,VPP-16.09 [Mpps],VPP-17.01 [Mpps],VPP-17.04 [Mpps],VPP-17.07 mean [Mpps],VPP-17.07 stdev [Mpps],17.04 to 17.07 change
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
    :header: VPP Functionality,Test Name,VPP-16.09 [Mpps],VPP-17.01 [Mpps],VPP-17.04 [Mpps],VPP-17.07 mean [Mpps],VPP-17.07 stdev [Mpps],17.04 to 17.07 change
    :file: ../../../docs/report/vpp_performance_tests/performance_improvements/ndr_throughput_others.csv

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

.. csv-table::
    :align: center
    :header: VPP Functionality,Test Name,VPP-16.09 [Mpps],VPP-17.01 [Mpps],VPP-17.04 [Mpps],VPP-17.07 mean [Mpps],VPP-17.07 stdev [Mpps],17.04 to 17.07 change
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


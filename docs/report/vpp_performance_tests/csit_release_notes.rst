CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Test environment changes in VPP data plane performance tests:

   - Further characterization and optimizations of VPP vhost-user and VM
     test methodology and test environment;

     - Tests with varying Qemu virtio queue (a.k.a. vring) sizes:
       [vr256] default 256 descriptors, [vr1024] 1024 descriptors to
       optimize for packet throughput;

     - Tests with varying Linux CFS (Completely Fair Scheduler)
       settings: [cfs] default settings, [cfsrr1] CFS RoundRobin(1)
       policy applied to all data plane threads handling test packet
       path including all VPP worker threads and all Qemu testpmd
       poll-mode threads;

     - Resulting test cases are all combinations with [vr256,vr1024] and
       [cfs,cfsrr1] settings;

     - For more detail see performance results observations section in
       this report;

#. Code updates and optimizations in CSIT performance framework:

   - Complete CSIT framework code revision and optimizations as descried
     on CSIT wiki page
     `Design_Optimizations <https://wiki.fd.io/view/CSIT/Design_Optimizations>`_.

   - For more detail see the CSIT Framework Design section in this
     report;

#. Changes to CSIT driver for TRex Traffic Generator:

   - Complete refactor of TRex CSIT driver;

   - Introduction of packet traffic profiles to improve usability and
     manageability of traffic profiles for a growing number of test
     scenarios.

   - Support for packet traffic profiles to test IPv4/IPv6 stateful and
     stateless DUT data plane features;

#. Added VPP performance tests

   - **Linux Container VPP memif virtual interface tests**

     - VPP Memif virtual interface (shared memory interface) tests
       interconnecting VPP instances over memif. VPP vswitch
       instance runs in bare-metal user-mode handling Intel x520 NIC
       10GbE interfaces and connecting over memif (Master side) virtual
       interfaces to another instance of VPP running in bare-metal Linux
       Container (LXC) with memif virtual interfaces (Slave side). LXC
       runs in a priviliged mode with VPP data plane worker threads
       pinned to dedicated physical CPU cores per usual CSIT practice.
       Both VPP run the same version of software. This test topology is
       equivalent to existing tests with vhost-user and VMs.

   - **Stateful Security Groups**

     - New tests of VPP stateful security-groups a.k.a. acl-plugin
       functionally compatible with networking-vpp OpenStack;

     - New tested security-groups access-control-lists (acl)
       configuration variants include: [iaclNsl] input acl stateless,
       [oaclNsl] output acl stateless, [iaclNsf] input acl stateful
       a.k.a. reflect, [oaclNsf] output acl stateful a.k.a. reflect,
       where N is number of access-control-entries (ace) in the acl.

     - Testing packet flows transmitted by TG: 100, 10k, 100k, always
       hitting the last permit entry in acl.

   - **VPP vhost and VM tests**

     - New VPP vhost-user and VM test cases to benchmark performance of
       VPP and VM topologies with Qemu and CFS policy combinations of
       [vr256,vr1024] x [cfs,cfsrr1];

     - Statistical analysis of repeatibility of results;

Performance Improvements
------------------------

Substantial improvements in measured packet throughput have been
observed in a number of CSIT |release| tests listed below, with relative
increase  of double-digit percentage points. Relative improvements for
this release are calculated against the test results listed in CSIT
|release-1| report. The comparison is calculated between the mean values
based on collected and archived test results' samples for involved VPP
releases. Standard deviation has been also listed for |release|.
VPP-16.09 and VPP-17.01 numbers are provided for reference.

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
| 1 | Security-groups acl-plugin scale tests failure  | CSIT-xxx   | VPP with 2 worker threads crashes during security-groups        |
|   | with stateful acls if VPP with 2 worker threads | VPP-912    | iaclNsf and oaclNsf tests with 100k flows.                      |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | VPP fails memif tests in 4 worker 2 core setup  | CSIT-xxx   | VPP with 4 worker threads running on 2 physical cores crashes   |
|   |                                                 | VPP-xxx    | during memif tests. Initial debugging points to DPDK code       |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| X | NDR discovery test failures 1518B frame size    | VPP-663    | VPP reporting errors: dpdk-input Rx ip checksum errors.         |
|   | for ip4scale200k, ip4scale2m scale IPv4 routed- |            | Observed frequency: all test runs.                              |
|   | forwarding tests. ip4scale20k tests are fine.   |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| X | Vic1385 and Vic1227 low performance.            | VPP-664    | Low NDR performance.                                            |
|   |                                                 |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| X | Sporadic NDR discovery test failures on x520.   | CSIT-750   | Suspected issue with HW settings (BIOS, FW) in LF               |
|   |                                                 |            | infrastructure. Issue can't be replicated outside LF.           |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| X | VPP in 2t2c setups - large variation            | CSIT-568   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across      |            | throughput. Applies to XL710 and X710 NICs, x520 NICs are fine. |
|   | multiple test runs with xl710 and x710 NICs.    |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| X | Lower than expected NDR and PDR throughput with | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+


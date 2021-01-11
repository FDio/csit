Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - CSIT test environment is versioned, see
     :ref:`test_environment_versioning`.

   - To identify performance changes due to VPP code changes from
     v20.05.0 to v20.09.0, both have been tested in CSIT environment
     ver. 5 and compared against each other. All substantial
     progressions has been marked up with RCA analysis. See
     :ref:`vpp_compare_current_vs_previous_release` and
     :ref:`vpp_known_issues`.

   - **GENEVE tests**: Added VPP performance tests for GENEVE tunnels.

     - See :ref:`geneve_methodology` for more details.

   - **NAT44 tests**: Adapted existing and added new tests.

     - Refactored NAT44 deterministic mode (nat44det) tests to use separate
       det44 vpp plugin and to use the same scheme of inside and outside
       addresses and ports, as used in new NAT44 endpoint-dependent mode tests.

     - Added new NAT44 endpoint-depended mode uni-directional (nat44ed-udir)
       tests that measure packet throughput in one direction with usage of TRex
       in stateless mode.

     - Added new NAT44 endpoint-dependent mode CPS tests that measure
       connections per second with usage of TRex in stateful mode.
       UPD packet size is 64 bytes. Size of TCP control packets
       is not configurable, please ignore the -64b- part of test names.

     - Added new NAT44 endpoint-dependent mode PPS tests that measure
       packets per second (control and data together) with usage of TRex
       in stateful mode. UPD packet size is 64 bytes. Size of TCP
       data packets is governed by the default MSS value, so most data packets
       are 1460 bytes long, please ignore the -64b- part of test names.

     - See :ref:`nat44_methodology` for more details.

   - **IPSec async mode tests**: Added VPP performance tests for async crypto
     engine.

   - **AMD 2n-zn2 testbed**: New physical testbed type installed in
     FD.io CSIT, with VPP and DPDK performance data added to CSIT
     trending and this report.

   - **AMD 2n-tx2 testbed**: New physical testbed type installed in
     FD.io CSIT, with VPP and DPDK performance data added to CSIT
     trending and this report.

#. TEST FRAMEWORK

   - **TRex ASTF**: Added capability to run TRex in advanced stateful mode.

   - **CSIT PAPI support**: Due to issues with PAPI performance, VAT is
     still used in CSIT for all VPP scale tests. See known issues below.

   - **General Code Housekeeping**: Ongoing RF keywords optimizations,
     removal of redundant RF keywords and aligning of suite/test
     setup/teardowns.

   - **Intel E810CQ 100G NIC**: Added configuration for Intel E810CQ 100G NIC.
     No tests run for this NIC as it is not present in FD.io CSIT lab yet.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs improvements**: Added possibility to use Gbps on Y-axis in
     Packet Throughput and Speedup Multi-Core graphs, added unidirectional
     mode to the Latency graphs.

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

List of known issues in |csit-release| for VPP performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-570                               | Sporadic (1 in 200) NDR discovery test failures on x520. DPDK reporting rx-errors, indicating L1 issue.   |
|    | <https://jira.fd.io/browse/CSIT-570>`_  | Suspected issue with HW combination of X710-X520 in LF testbeds. Not observed outside of LF testbeds.     |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `VPP-662                                | 9000B packets not supported by NICs VIC1227 and VIC1387.                                                  |
|    | <https://jira.fd.io/browse/VPP-662>`_   |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1763                              | Adapt ramp-up phase of nat44 tests for different frame sizes.                                             |
|    | <https://jira.fd.io/browse/CSIT-1763>`_ | Currently ramp-up phase rate and duration values are correctly set for tests with 64B frame size.         |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1671                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1671>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+ The usual PAPI library spends too much time parsing arguments, so even with async processing (hundreds of |
|    | `VPP-1763                               | commands in flight over socket), the VPP configuration for large scale tests (millions of messages) takes |
|    | <https://jira.fd.io/browse/VPP-1763>`_  | too long.                                                                                                 |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1771                              | IPv4 IPSEC 9000B packet tests had been failing when chained buffers were not supported.                   |
|    | <https://jira.fd.io/browse/CSIT-1771>`_ | This has been fixed on VPP side, but CSIT still needs to re-enable jumbo tests.                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `VPP-1934                               | [i40e] Interfaces are not brought up from carrier-down.                                                   |
|    | <https://jira.fd.io/browse/VPP-1934>`_  | In case of i40e -based interface (e.g Intel x700 series NIC) is bound to kernel driver (i40e) and is in   |
|    |                                         | state "no-carrier" (<NO-CARRIER,BROADCAST,MULTICAST,UP>) because previously it was disabled via           |
|    |                                         | "I40E_AQ_PHY_LINK_ENABLED" call, then VPP during initialization of AVF interface is not re-enabling       |
|    |                                         | interface link via i40e driver to up.                                                                     |
|    |                                         | CSIT implemented `workaround for AVF interface <https://gerrit.fd.io/r/c/csit/+/29086>`_ until fixed.     |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1760                              | All Mellanox / rdma driver tests are failing on LF testbed28 while successfully run on other LF testbeds. |
|    | <https://jira.fd.io/browse/CSIT-1760>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 |                                         |                                                                                                           |
|    |                                         |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

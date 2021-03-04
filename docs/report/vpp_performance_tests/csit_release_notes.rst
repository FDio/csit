Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - CSIT test environment is versioned, see
     :ref:`test_environment_versioning`.

   - **GENEVE tests**: Added VPP performance tests for GENEVE tunnels.
     See :ref:`geneve_methodology` for more details.


   - **GSO tests**: Added VPP performance tests for GSOtap and GSOvirtio.
     All tested topologies are compared with GSO enabled and disabled.
     In |csit-release| there is only 1t1c tests running.
     See :ref:`gso_methodology` for more details.


   - **NAT44 tests**: Added new test type, pure throughput tests.
     They are similar to PPS tests, but they employ ramp-up trials
     to ensure all sessions are created (and not timing out)
     for performance trials.

   - **Jumbo for ipsec**: Test cases with 9000 byte frames are re-enabled
     in ipsec suites.

   - **Randomized profiles**: Improved repeatability and cycle length.
     For details, see :ref:`packet_flow_ordering`.

   - **Arm 2n-tx2 testbed**: New physical testbed type installed in
     FD.io CSIT, with VPP and DPDK performance data added to CSIT
     trending and this report.

   - **Framework speedup**: Shortened overall test job duration
     by using a different test selection mechanism (using --test
     instead of --include) and by avoiding unnecessary PAPI reconnects.

#. TEST FRAMEWORK

   - **TRex ASTF**: Improved capability to run TRex in advanced stateful mode.

   - **CSIT PAPI support**: Due to issues with PAPI performance, VAT is
     still used in CSIT for all VPP scale tests. See known issues below.

   - **General Code Housekeeping**: Ongoing code optimizations,
     speed ups and bug fixes.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs improvements**: Updated Packet Latency graphs,
     see :ref:`latency_methodology`.

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
|  5 | `VPP-1934                               | [i40e] Interfaces are not brought up from carrier-down.                                                   |
|    | <https://jira.fd.io/browse/VPP-1934>`_  | In case of i40e -based interface (e.g Intel x700 series NIC) is bound to kernel driver (i40e) and is in   |
|    |                                         | state "no-carrier" (<NO-CARRIER,BROADCAST,MULTICAST,UP>) because previously it was disabled via           |
|    |                                         | "I40E_AQ_PHY_LINK_ENABLED" call, then VPP during initialization of AVF interface is not re-enabling       |
|    |                                         | interface link via i40e driver to up.                                                                     |
|    |                                         | CSIT implemented `workaround for AVF interface <https://gerrit.fd.io/r/c/csit/+/29086>`_ until fixed.     |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `VPP-1972                               | One VPP change has decreased performance of NAT44ed processing, both slow path and fast path.             |
|    | <https://jira.fd.io/browse/VPP-1972>`   |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

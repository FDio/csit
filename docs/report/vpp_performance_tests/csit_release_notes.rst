Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Intel Xeon 2n-skx, 3n-skx testbeds**: VPP performance test data
     is provided using a different CSIT test environment compared to
     CSIT-1908.1 and CSIT-1908. The changes were applied during the
     CSIT-2001 development cycle.

     - CSIT test environment is now versioned, with ver. 1 associated
       with CSIT rls1908 git branch as of 2019-08-21, and ver. 2
       associated with CSIT rls2001 git branch as of 2020-03-27.

     - To identify performance changes due to VPP code changes from
       v19.08.1 to v19.08.2, both have been tested in CSIT
       environment ver. 2. See
       :ref:`vpp_compare_current_vs_previous_release` and
       :ref:`vpp_known_issues`.

   - **Intel Xeon 2n-clx testbeds**: VPP performance test data is now
     included in this report. See :ref:`vpp_known_issues`.

   - **Service density 2n-skx tests**: Added higher NF density tests with
     802.1q (vlan) and VXLAN encapsulation from Traffic Generator.

   - **GBP tests**: Added GBP (Group Based Policy) routing test cases
     with 802.1q (vlan) external traffic.

   - **AVF IPv4 scale tests**: Increased coverage of AVF IPv4 base and
     scale test cases (Fortville NICs only).

   - **2n-skx tests**: Increased coverage of selected (COP, iACL,
     Policer) test cases.

   - **IPsec scale tests**: Added IPsec interface mode scale tests with
     1, 40, 400, 1000, 5000, 10000, 20000, 40000, 60000 IPsec tunnels.
     Removed DPDK backend dependency. Major IPsec test code
     refactoring.

   - **Hoststack TCP/IP tests**: Major refactor of Hoststack TCP
     performance tests using WRK generator talking to the VPP HTTP
     static server plugin measuring connections per second and
     requests per second.

   - **Changed methodology of dot1q tests in 2-Node testbeds**: dot1q
     encapsulation is now used on both links of SUT. Previously dot1q
     was used only on a single link with the other link carrying
     untagged Ethernet frames. This change results in slightly lower
     throughput in CSIT-1908 for all dot1q tests in all 2-Node
     testbeds.

   - **KVM VM vhost-user tests**: completed move to Kernel-VM for all
     tests. In addition to running DPDK Testpmd as VM workload, new
     tests created with VPP as VM workload. VPP in VM is the same
     version as the DUT VPP (acting as vSwitch) and its configuration
     depends on the test type. For all L2 Ethernet Switching tests
     it's vpp-l2xc (L2 cross-connect), for all IPv4 Routing tests it's
     vpp-ip4 (VPP IPv4 routing).

#. TEST FRAMEWORK

   - **CSIT PAPI Support**: Finished conversion of CSIT VAT L1 keywords
     to PAPI L1 KWs in CSIT using VPP Python bindings (VPP PAPI).
     Redesign of key components of PAPI Socket Executor and PAPI
     history. Due to issues with PAPI performance, VAT is still used
     in CSIT for all VPP scale tests. See known issues below.

   - **General Code Housekeeping**: Ongoing RF keywords optimizations,
     removal of redundant RF keywords and aligning of suite/test
     setup/teardowns.


#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs Layout Improvements**: Improved performance graphs layout
     for better readibility and maintenance: test grouping, axis
     labels, descriptions, other informative decoration.

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

List of known issues in |csit-release| for VPP performance tests:

+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                        |
+====+=========================================+==========================================================================================================+
| 1  | `CSIT-570                               | Sporadic (1 in 200) NDR discovery test failures on x520. DPDK reporting rx-errors, indicating L1 issue.  |
|    | <https://jira.fd.io/browse/CSIT-570>`_  | Suspected issue with HW combination of X710-X520 in LF testbeds. Not observed outside of LF testbeds.    |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 2  | `VPP-662                                | 9000B packets not supported by NICs VIC1227 and VIC1387.                                                 |
|    | <https://jira.fd.io/browse/VPP-662>`_   |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 3  | `CSIT-1498                              | Memif tests are sporadically failing on initialization of memif connection.                              |
|    | <https://jira.fd.io/browse/CSIT-1498>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 4  | `VPP-1676                               | 9000B ip4 memif errors - ip4-input: ip4 length > l2 length.                                              |
|    | <https://jira.fd.io/browse/VPP-1676>`_  | IP4 jumbo frames (9000B) are dropped in case of tests with memif.                                        |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 5  | `VPP-1677                               | 9000B ip4 nat44: VPP crash + coredump.                                                                   |
|    | <https://jira.fd.io/browse/VPP-1677>`_  | VPP crashes very often in case that NAT44 is configured and it has to process IP4 jumbo frames (9000B).  |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 6  | `CSIT-1591                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much  |
|    | <https://jira.fd.io/browse/CSIT-1591>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                     |
|    +-----------------------------------------+                                                                                                          |
|    | `VPP-1763                               |                                                                                                          |
|    | <https://jira.fd.io/browse/VPP-1763>`_  |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 7  | `CSIT-1593                              | IPv4 AVF 9000B packet tests are failing on 3n-skx while passing on 2n-skx.                               |
|    | <https://jira.fd.io/browse/CSIT-1593>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
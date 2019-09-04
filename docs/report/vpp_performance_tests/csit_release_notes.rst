Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

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
| 3  | `CSIT-1503                              | [`TRex-519 <https://trex-tgn.cisco.com/youtrack/issue/trex-519>`_] XL710/XXV710 with FW 6.0.1 will have  |
|    | <https://jira.fd.io/browse/CSIT-1503>`_ | Rx drop rate of 27MPPS.                                                                                  |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 4  | `CSIT-1498                              | Memif tests are sporadically failing on initialization of memif connection.                              |
|    | <https://jira.fd.io/browse/CSIT-1498>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 5  | `CSIT-1499                              | AVF tests are sporadically failing on initialization of AVF interface.                                   |
|    | <https://jira.fd.io/browse/CSIT-1499>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 6  | `VPP-1676                               | 9000B ip4 memif errors - ip4-input: ip4 length > l2 length.                                              |
|    | <https://jira.fd.io/browse/VPP-1676>`_  | IP4 jumbo frames (9000B) are dropped in case of tests with memif.                                        |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 7  | `VPP-1677                               | 9000B ip4 nat44: VPP crash + coredump.                                                                   |
|    | <https://jira.fd.io/browse/VPP-1677>`_  | VPP crashes very often in case that NAT44 is configured and it has to process IP4 jumbo frames (9000B).  |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 8  | `CSIT-1591                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much  |
|    | <https://jira.fd.io/browse/CSIT-1499>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                     |
|    |                                         |                                                                                                          |
|    | `VPP-1763                               |                                                                                                          |
|    | <https://jira.fd.io/browse/VPP-1763>`_  |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 9  | `CSIT-1592                              | VPP memif API does not enable memif zero-copy, resulting in different memif configuration vs. previously |
|    | <https://jira.fd.io/browse/CSIT-1592>`_ | tested VAT/CLI where memif zero-copy was enabled by default. Needs to be fixed in VPP.                   |
|    |                                         |                                                                                                          |
|    | `VPP-1764                               |                                                                                                          |
|    | <https://jira.fd.io/browse/VPP-1764>`_  |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 10 | `VPP-1675                               | IPv4 IPSEC 9000B packet tests are failing as no packet is forwarded.                                     |
|    | <https://jira.fd.io/browse/VPP-1675>`_  | Reason: chained buffers are not supported.                                                               |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 12 | `CSIT-1593                              | IPv4 AVF 9000B packet tests are failing on 3n-skx while passing on 2n-skx.                               |
|    | <https://jira.fd.io/browse/CSIT-1593>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+


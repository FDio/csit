Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Service density 2n-skx tests**: Added higher NF density tests with
     802.1q (vlan) and 802.1ad (vxlan) encapsulation from Traffic Generator.

   - **GBP tests**: Added GBP routing test cases with 802.1q (vlan) external
     traffic.

   - **AVF IPv4 scale tests**: Increased coverage of AVF IPv4 base and scale
     test cases.

   - **2n-skx tests**: Increased coverage of selected (COP, iACL, Policer)
     test cases.

   - **IPsec scale tests**: Added IPsec interface mode scale tests with
     1, 40, 400, 1000, 5000, 10000, 20000, 40000, 60000 tunnels. Removed DPDK
     backend dependency.

   - **Hoststack TCP tests**: Added Hoststack TCP performance tests
     using WRK to the HTTP static server plugin measuring connections
     per second and requests per second.

   - **Changed methodology of dot1q 2n tests**: dot1q encapsulation is now used
     on both links of SUT. Previously dot1q was used only on a single link with
     the other link carrying untagged Ethernet frames. This change results in
     slightly lower throughput in CSIT-1908 for these tests.

#. TEST FRAMEWORK

   - **CSIT PAPI Support**: Finished conversion of CSIT VAT L1 keywords to
     PAPI L1 KWs in CSIT using VPP Python bindings. Redesign of key components
     of PAPI Executor and PAPI history. Currently the only exception is
     usage of VAT command for scale configuration.

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
| 2  | `CSIT-1503                              | [`TRex-519 <https://trex-tgn.cisco.com/youtrack/issue/trex-519>`_] XL710/XXV710 with FW 6.0.1 will have  |
|    | <https://jira.fd.io/browse/CSIT-1503>`_ | Rx drop rate of 27MPPS.                                                                                  |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 3  | `CSIT-1499                              | AVF tests are sporadically failing on initialization of AVF interface.                                   |
|    | <https://jira.fd.io/browse/CSIT-1499>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 4  | `VPP-662                                | 9000B packets not supported by NICs VIC1227 and VIC1387.                                                 |
|    | <https://jira.fd.io/browse/VPP-662>`_   |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 5  | `VPP-1677                               | IP4 NAT44 9000B packet tests are failing as no packet is transferred.                                    |
|    | <https://jira.fd.io/browse/VPP-1677>`_  |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 6  | `VPP-1676                               | IP4 memif 9000B packet tests are failing as no packet is transferred.                                    |
|    | <https://jira.fd.io/browse/VPP-1676>`_  |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 7  | `VPP-1675                               | IP4 IPSEC 9000B packet tests are failing as no packet is transferred.                                    |
|    | <https://jira.fd.io/browse/VPP-1675>`_  | Reason: chained buffers are not supported.                                                               |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 8  | `CSIT-1593                              | IP4 AVF 9000B packet tests are failing on 3n-skx while passing on 2n-skx.                                |
|    | <https://jira.fd.io/browse/CSIT-1593>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+

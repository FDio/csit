Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Service density 2n-skx tests**: Added higher NF density tests with two
     NFs' data-plane threads sharing a physical core. VPP IPv4 routing is now
     used as a VNF payload similar to CNF tests.

   - **Soak Tests**: Optimized performamce soak tests framework
     code for extended time duration tests and throughput discovery
     at given PLR and at give total test time e.g. minutes, hours,
     days, weeks. See updated
     :ref:`test_methodology` section for more details.

#. TEST FRAMEWORK

   - **Qemu code refactor**: Complete code refactor of the key components of
     QemuUtil.py and QemuManager.py (L1 and L2 KW counterparts). Added
     implementation of kernel-image-kvm based VM replacing the previously used
     NestedVM images. Added ability to run VPP as a payload in VNF.

   - **CSIT PAPI Support**: Continued conversion of CSIT VAT L1 keywords to
     PAPI L1 KWs in CSIT using VPP Python bindings. Redesign of key components
     of PAPI Executor and PAPI history.

   - **General Code Housekeeping**: Ongoing RF keywords optimizations,
     removal of redundant RF keywords.

   - **Test suite generator**: Added capability to generate suites for
     different NIC models as well as throughput search algorithm types. Uses
     base tests suites as source.

   - **TOX verification**: Added verifications for test suite generator.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs Layout Improvements**: Improved performance graphs layout
     for better readibility and maintenance: test grouping, axis
     labels, descriptions, other informative decoration.

..
    #. MISCELLANEOUS

       - **2n-dnv Tests (3rd Party)**: Published performance tests for 2n-
         dnv (2-Node Atom Denverton) from 3rd party testbeds running FD.io
         |csit-release| automated testing code.
         Only graphs for Packet Throughput and Speedup Multi-core and not
         for Packet Latency were published as there are no results for Packet
         Latency available.

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
| 3  | `CSIT-1501                              | Sporadic crypto backend fails loading `VPP-1670 <https://jira.fd.io/browse/VPP-1670>`_                   |
|    | <https://jira.fd.io/browse/CSIT-1501>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 4  | `CSIT-1427                              | Sporadic HW aes-128-cbc-sha1 tunnel-interface tests are failing.                                         |
|    | <https://jira.fd.io/browse/CSIT-1427>`_ | `VPP-1671 <https://jira.fd.io/browse/VPP-1671>`_                                                         |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 5  | `CSIT-1498                              | Memif tests are sporadically failing on initialization of memif connection.                              |
|    | <https://jira.fd.io/browse/CSIT-1498>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 6  | `CSIT-1499                              | AVF tests are sporadically failing on initialization of AVF interface.                                   |
|    | <https://jira.fd.io/browse/CSIT-1499>`_ |                                                                                                          |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 7  | `VPP-1676                               | 9000B ip4 memif errors - ip4-input: ip4 length > l2 length.                                              |
|    | <https://jira.fd.io/browse/VPP-1676>`_  | IP4 jumbo frames (9000B) are dropped in case of tests with memif.                                        |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+
| 8  | `VPP-1677                               | 9000B ip4 nat44: VPP crash + coredump.                                                                   |
|    | <https://jira.fd.io/browse/VPP-1677>`_  | VPP crashes very often in case that NAT44 is configured and it has to process IP4 jumbo frames (9000B).  |
+----+-----------------------------------------+----------------------------------------------------------------------------------------------------------+

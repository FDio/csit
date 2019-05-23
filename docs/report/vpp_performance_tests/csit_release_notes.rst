Release Notes
=============

..
    Changes in |csit-release|
    -------------------------

    #. VPP PERFORMANCE TESTS

       - **Service density 2n-skx tests**: Network Function Virtualization (NFV)
         service density tests focus on measuring total per server throughput at
         varied NFV service *packing* densities with vswitch providing host
         dataplane. The goal is to compare and contrast performance of a shared
         vswitch for different network topologies and virtualization technologies,
         and their impact on vswitch performance and efficiency in a range of NFV
         service configurations.

       - **Experimental Soak Tests**: Added performamce soak tests framework
         code for extended time duration tests and throughput discovery
         at given PLR and at give total test time e.g. minutes, hours,
         days, weeks, months, years. See updated
         :ref:`test_methodology` section for more details.

    #. TEST FRAMEWORK

       - **Container code optimizations**: Optimized container library allows to
         run containre_memif tests faster.

       - **CSIT PAPI Support**: Continue converting existing VAT L1 keywords to
         PAPI L1 KWs in CSIT using VPP Python bindings. Required for migrating away
         from VAT.

       - **General Code Housekeeping**: Ongoing RF keywords optimizations,
         removal of redundant RF keywords.

    #. PRESENTATION AND ANALYTICS LAYER

       - **Graphs Layout Improvements**: Improved performance graphs layout
         for better readibility and maintenance: test grouping, axis
         labels, descriptions, other informative decoration.

    #. MISCELLANEOUS

       - **3n-dnv Tests (3rd Party)**: Published performance tests for 3n-
         dnv (3-Node Atom Denverton) from 3rd party testbeds running FD.io
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

+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                                               |
+====+=========================================+=================================================================================================================================+
| 1  | `CSIT-570                               | Sporadic (1 in 200) NDR discovery test failures on x520. DPDK reporting rx-errors, indicating L1 issue.                         |
|    | <https://jira.fd.io/browse/CSIT-570>`_  | Suspected issue with HW combination of X710-X520 in LF testbeds. Not observed outside of LF testbeds.                           |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 2  | `VPP-1562                               | Link bonding (mode LACP, transmit policy l34) test are failing due to VPP crashing producing core dump.                         |
|    | <https://jira.fd.io/browse/VPP-1562>`_  |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 3  | `CSIT-1427                              | Scale HW IPsec are failing due to issue with selecting ipsec backend in VPP.                                                    |
|    | <https://jira.fd.io/browse/CSIT-1427>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 4  | `VPP-1563                               | AVF L2patch tests are failing for all packet size and core combination. Reason: null-node blackholed packets in show error.     |
|    | <https://jira.fd.io/browse/VPP-1563>`_  |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 5  | `CSIT-1234                              | VPP IPSecHW/IPSecsW scale interface mode, low NDR and PDR 64B throughput in 3n-hsw testbeds, in CSIT-19.01 vs. CSIT-18.10.      |
|    | <https://jira.fd.io/browse/CSIT-1234>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 6  | `CSIT-1428                              | VM vhost tests with RXQ 2 and more are failing and reporting incorrect measurements due to RXQ configuration issue.             |
|    | <https://jira.fd.io/browse/CSIT-1428>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 7  | `CSIT-1431                              | AVF 4 cores tests are sporadically failing.                                                                                     |
|    | <https://jira.fd.io/browse/CSIT-1431>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+

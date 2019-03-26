Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

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

   - **2n-dnv Tests (3rd Party)**: Published performance tests for 2n-
     dnv (2-Node Atom Denverton) from 3rd party testbeds running FD.io
     |csit-release| automated testing code.
     Only graphs for Packet Throughput and Speedup Multi-core and not
     for Packet Latency were published as there are no results for Packet
     Latency available.

.. note::

    The Report rls1901.1 was generated with only 1 run of performance tests,
    ie. the data are not statistically significant.
    The NFV tests were not run so this section has been removed from the
    report.

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
| 2  | `VPP-1563                               | AVF L2patch tests are failing for all packet size and core combination. Reason: null-node blackholed packets in show error.     |
|    | <https://jira.fd.io/browse/VPP-1563>`_  |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 3  | `CSIT-1234                              | VPP IPSecHW/IPSecsW scale interface mode, low NDR and PDR 64B throughput in 3n-hsw testbeds, in CSIT-19.01 vs. CSIT-18.10.      |
|    | <https://jira.fd.io/browse/CSIT-1234>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 4  | `CSIT-1431                              | AVF 4 cores tests are sporadically failing. Under investigation.                                                                |
|    | <https://jira.fd.io/browse/CSIT-1431>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 5  | `CSIT-1465                              | 4c VPP VM vhost tests failing on 3n-skx. Under investigation.                                                                   |
|    | <https://jira.fd.io/browse/CSIT-1465>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 6  | `CSIT-1466                              | IPSecHW scale tests failing due to VPP reset. Fixed in one of subsequent VPP patches. Confirmed by  running tests with VPP      |
|    | <https://jira.fd.io/browse/CSIT-1466>`_ | build 19.01.1-8~g50a392f~b56.                                                                                                   |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+

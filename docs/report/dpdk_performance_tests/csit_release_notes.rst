Release Notes
=============

Changes in |csit-release|
-------------------------

#. DPDK PERFORMANCE TESTS

   - Refactor of initialization and compilation helper scripts for DPDK testpmd
     and l3fwd. Removing obsolete parameters from DPDK testpmd and l3fwd
     command line.

   - Fixed 9000B L2 packet size tests not passing for all NICs.

   - Fixed DPDK compilation and test initialization of Mellanox NICs using
     CONFIG_RTE_LIBRTE_MLX5_PMD=y in compile configuration.

#. DPDK RELEASE VERSION CHANGE

   - |csit-release| tested |dpdk-release|, as used by |vpp-release|.

.. _dpdk_known_issues:

Known Issues
------------

List of known issues in |csit-release| for DPDK performance tests:

+----+------------------------------------------+----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                   | Issue Description                                                                                        |
+====+==========================================+==========================================================================================================+
| 1  | `CSIT-????                               | DPDK L3fwd tests with 9000B L2 packet size are not passing with Mellanox NICs.                           |
|    | <https://jira.fd.io/browse/CSIT-????>`_  | L3fwd application does not accept parameter for increasing -mbuf-size in same way DPDK testpmd does.     |
+----+------------------------------------------+----------------------------------------------------------------------------------------------------------+

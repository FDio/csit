Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **CSIT test environment** version has not changed from ver. 11 used
     in previous release, see :ref:`test_environment_versioning`.

#. DPDK PERFORMANCE TESTS

   - **Intel Xeon SKX performance testbeds** got decommissioned and
     removed from FD.io performance lab.

#. DPDK RELEASE VERSION CHANGE

   - |csit-release| tested |dpdk-release|, as used by |vpp-release|.

.. _dpdk_known_issues:

Known Issues
------------

List of known issues in |csit-release| for DPDK performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1848                              | 2n-clx, 3n-alt: sporadic testpmd/l3fwd tests fail with no or low traffic.                                 |
|    | <https://jira.fd.io/browse/CSIT-1848>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

New
___

List of new issues in |csit-release| for DPDK performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+

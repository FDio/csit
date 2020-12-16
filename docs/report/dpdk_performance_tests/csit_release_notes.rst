Release Notes
=============

Changes in |csit-release|
-------------------------

#. DPDK PERFORMANCE TESTS

   - Fixed DPDK compilation on ARM systems.

   - **AMD 2n-zn2 testbed**: New physical testbed type installed in
     FD.io CSIT, with DPDK performance data added to this report.

#. DPDK RELEASE VERSION CHANGE

   - |csit-release| tested |dpdk-release|, as used by |vpp-release|.

.. _dpdk_known_issues:

Known Issues
------------

List of known issues in |csit-release| for DPDK performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1761                              | Denverton systems in FD.io CSIT lab (2n-dnv and 3n-dnv) reports dpdk compilation error very often.        |
|    | <https://jira.fd.io/browse/CSIT-1761>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1762                              | TRex reports link DOWN in case of dpdk testpmd tests on FD.io CSIT Denverton systems (2n-dnv and 3n-dnv). |
|    | <https://jira.fd.io/browse/CSIT-1762>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

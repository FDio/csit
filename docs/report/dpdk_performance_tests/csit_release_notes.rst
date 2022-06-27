Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **CSIT test environment** version has been updated to ver. 8, see
     :ref:`test_environment_versioning`.

#. DPDK PERFORMANCE TESTS

   - **Arm Ampere Altra**: Performance test data for these platforms
     is now provided by testbeds newly installed in FD.io CSIT labs.
     For details about the physical setup see
     :ref:`physical_testbeds_3n_alt`.

#. DPDK RELEASE VERSION CHANGE

   - |csit-release| tested |dpdk-release|, as used by |vpp-release|.

.. _dpdk_known_issues:

Known Issues
------------

List of known issues in |csit-release| for DPDK performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1762                              | TRex reports link DOWN in case of dpdk testpmd tests on FD.io CSIT Denverton systems (2n-dnv and 3n-dnv). |
|    | <https://jira.fd.io/browse/CSIT-1762>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

New
___

List of new issues in |csit-release| for DPDK performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  # | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1848                              | 2n-clx, 2n-skx, 3n-alt: sporadic testpmd/l3fwd tests fail with no or low traffic.                         |
|    | <https://jira.fd.io/browse/CSIT-1848>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
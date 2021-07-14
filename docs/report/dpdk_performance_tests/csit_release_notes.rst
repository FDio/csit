Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **Upgrade to Ubuntu 20.04 LTS**: Re-installed base operating system
     to Ubuntu 20.04.2 LTS. Upgrade included also baseline Docker
     containers used for spawning topology.

   - **CSIT test environment** version has been updated to ver. 7, see
     :ref:`test_environment_versioning`.

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

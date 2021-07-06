Release Notes
=============

Changes in |csit-release|
-------------------------


#. DPDK PERFORMANCE TESTS

   - CSIT test environment is versioned, see
     :ref:`test_environment_versioning`.

   - **Upgrade to Ubuntu 20.04 LTS**: Reinstall base operating system to Ubuntu
     20.04.2 LTS. Upgrade includes also baseline Docker containers used for
     spawning topology.

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

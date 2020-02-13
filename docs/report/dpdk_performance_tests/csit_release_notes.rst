Release Notes
=============

Changes in |csit-release|
-------------------------

#. DPDK PERFORMANCE TESTS

   - **Intel Xeon 2n-skx, 3n-skx and 2n-clx testbeds**: Testpmd and
     L3fwd performance test data is not included in this report
     version. This is due to the lower performance and behaviour
     inconsistency of these systems following the upgrade of processor
     microcode packages (skx ucode 0x2000064, clx ucode 0x500002c) as
     part of updating Ubuntu 18.04 LTS kernel version. Tested VPP and
     DPDK applications (L3fwd) are affected. Skx and Clx test data
     will be added in subsequent maintenance report version(s) once
     the issue is resolved. See :ref:`dpdk_known_issues`.

.. // Alternative Note for 1st Bullet when bad microcode Skx, Clx results are published
.. - **Intel Xeon 2n-skx, 3n-skx and 2n-clx testbeds**: Testpmd and
..   L3fwd performance test data is included in this report version,
..   but it shows lower performance and behaviour inconsistency of
..   these systems following the upgrade of processor microcode
..   packages (skx ucode 0x2000064, clx ucode 0x500002c) as part of
..   updating Ubuntu 18.04 LTS kernel version. Tested VPP and DPDK
..   applications (L3fwd) are affected. Skx and Clx test data will be
..   corrected in subsequent maintenance report version(s) once the
..   issue is resolved. See :ref:`vpp_known_issues`.

#. DPDK RELEASE VERSION CHANGE

   - |csit-release| tested |dpdk-release|, as used by |vpp-release|.

.. _dpdk_known_issues:

Known Issues
------------

List of known issues in |csit-release| for DPDK performance tests:

+----+------------------------------------------+----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                   | Issue Description                                                                                        |
+====+==========================================+==========================================================================================================+
| 8  | `CSIT-1675                               | Intel Xeon 2n-skx, 3n-skx and 2n-clx testbeds behaviour and performance became inconsistent following    |
|    | <https://jira.fd.io/browse/CSIT-1675>`_  | the upgrade to the latest Ubuntu 18.04 LTS kernel version (4.15.0-72-generic) and associated microcode   |
|    |                                          | packages (skx ucode 0x2000064, clx ucode 0x500002c). VPP as well as DPDK L3fwd tests are affected.       |
+----+------------------------------------------+----------------------------------------------------------------------------------------------------------+

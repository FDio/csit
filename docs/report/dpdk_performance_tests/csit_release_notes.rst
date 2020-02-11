Release Notes
=============

Changes in |csit-release|
-------------------------

#. DPDK PERFORMANCE TESTS

   - **Intel Xeon 2n-skx, 3n-skx and 2n-clx**: Testpmd and L3fwd test
     data is not included in this report version. This is due to
     performance and behaviour inconsistency following the upgrade to
     the latest Ubuntu 18.04 LTS kernel version (4.15.0-72-generic)
     and associated microcode versions (skx: 0x2000064, clx:
     0x5000021). Test data will be added in subsequent maintenance
     report version(s) once testing is completed using reverted kernel
     (4.15.0-46-generic) and microcode (skx: 0x2000043, clx:
     0x500002c).

#. DPDK RELEASE VERSION CHANGE

   - |csit-release| tested |dpdk-release|, as used by |vpp-release|.

Known Issues
------------

List of known issues in |csit-release| for DPDK performance tests:

+----+------------------------------------------+----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                   | Issue Description                                                                                        |
+====+==========================================+==========================================================================================================+
| 1  | `CSIT-1675                               | Intel Xeon 2n-skx, 3n-skx and 2n-clx testbeds behaviour and performance became inconsistent following    |
|    | <https://jira.fd.io/browse/CSIT-1675>`_  | the upgrade to the latest Ubuntu 18.04 LTS kernel version (4.15.0-72-generic) and associated microcode   |
|    |                                          | versions (skx: 0x2000064, clx: 0x5000021). VPP as well as DPDK L3fwd applications are affected.          |
+----+------------------------------------------+----------------------------------------------------------------------------------------------------------+

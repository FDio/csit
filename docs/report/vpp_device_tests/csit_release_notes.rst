Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **Flow based tests**: Added functional flow based tests (
     IPv4 GTPU, IPv4 IPSEC, IPv4 L2TPV3OIP, IPv4 NTUPLE TCP/UDP, IPv4 TCP/UDP,
     IPv6 NTUPLE TCP/UDP, IPv6 TCP/UDP).
   - **Intel E810-C**: Added 2 * Intel E810-2CQDA2 NIC cards into 1n-skx
     testbeds.
   - **Suite generator**: CSIT suite generator extended to cover also VPP device
     jobs. It is possible to generate NIC/driver suite combinations per
     definition lists. Job specifications added to control test being run on per
     patch.

Known Issues
------------

List of known issues in |csit-release| for VPP functional tests in VPP Device:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|    |                                         |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

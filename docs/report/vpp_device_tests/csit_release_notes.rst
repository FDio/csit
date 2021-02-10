Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **Bug fixes**.

#. TEST COVERAGE

   - Increased test coverage: **GENEVE**, **ACL** and **MACIP** from ACL plugin.

#. DEPRECATED API MESSAGES

   - Updated API calls for **link bonding**, **COP**, **IPSEC**, **NAT** and
     **NSIM**.

Known Issues
------------

List of known issues in |csit-release| for VPP functional tests in VPP Device:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `VPP-1943                               | Running multiple VPPs with SR-IOV VFs belonging to the same PF sometimes results in VPP not initializing  |
|    | <https://jira.fd.io/browse/VPP-1943>`_  | the VF interfaces properly due to a race condition between the PF and VFs. Observed with Intel NIC        |
|    |                                         | firmware version 6.01 0x800035da 1.1747.0 and i40e driver versions 2.1.14-k and 2.13.10.                  |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

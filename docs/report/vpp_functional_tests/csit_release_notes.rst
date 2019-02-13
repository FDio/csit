Release Notes
=============

Changes in |csit-release|
-------------------------

#. TEST FRAMEWORK

   - **Bug fixes**.

#. CSIT TEST MIMGRATION

   - **VPP_Path**: Continuing migration of the original FD.io CSIT VIRL
     tests to VPP-make_test VPP integration tests for functional
     acceptance of VPP feature path(s) driven by use case(s). See P1
     and P2 markup in `CSIT_VIRL migration progress
     <https://docs.google.com/spreadsheets/d/1PciV8XN9v1qHbIRUpFJoqyES29_vik7lcFDl73G1usc/edit?usp=sharing>`_

Known Issues
------------

List of known issues in |csit-release| for VPP functional tests in VIRL:

+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| # | JiraID                                  | Issue Description                                                                                                       |
+===+=========================================+=========================================================================================================================+
| 1 | `CSIT-129                               | DHCPv4 client: Client responses to DHCPv4 OFFER sent with different XID.                                                |
|   | <https://jira.fd.io/browse/CSIT-129>`_  | Client replies with DHCPv4 REQUEST message when received DHCPv4 OFFER message with different (wrong) XID.               |
|   | `VPP-99                                 |                                                                                                                         |
|   | <https://jira.fd.io/browse/VPP-99>`_    |                                                                                                                         |
+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| 2 | `CSIT-398                               | Softwire - MAP-E: Incorrect calculation of IPv6 destination address when IPv4 prefix is 0.                              |
|   | <https://jira.fd.io/browse/CSIT-398>`_  | IPv6 destination address is wrongly calculated in  case that IPv4 prefix is equal to 0 and IPv6 prefix is less than 40. |
|   | `VPP-380                                |                                                                                                                         |
|   | <https://jira.fd.io/browse/VPP-380>`_   |                                                                                                                         |
+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| 3 | `CSIT-399                               | Softwire - MAP-E: Map domain is created when incorrect parameters provided.                                             |
|   | <https://jira.fd.io/browse/CSIT-399>`_  | Map domain is created in case that the sum of suffix length of IPv4 prefix and PSID length is greater than EA bits      |
|   | `VPP-435                                | length. IPv6 destination address contains bits writen with PSID over the EA-bit length when IPv4 packet is sent.        |
|   | <https://jira.fd.io/browse/VPP-435>`_   |                                                                                                                         |
+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| 4 | `CSIT-409                               | IPv6 RA: Incorrect IPv6 destination address in response to ICMPv6 Router Solicitation.                                  |
|   | <https://jira.fd.io/browse/CSIT-409>`_  | Wrong IPv6 destination address (ff02::1) is used in ICMPv6 Router Advertisement packet sent as a response to received   |
|   | `VPP-406                                | ICMPv6 Router Solicitation packet.                                                                                      |
|   | <https://jira.fd.io/browse/VPP-406>`_   |                                                                                                                         |
+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| 5 | `CSIT-565                               | Vhost-user: QEMU reconnect does not work.                                                                               |
|   | <https://jira.fd.io/browse/CSIT-565>`_  | QEMU 2.5.0 used in CSIT does not support vhost-user reconnect. Requires upgrading CSIT VIRL environment to QEMU 2.7.0.  |
+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| 6 | `CSIT-1371                              | Softwire: Exclude all softwire functional tests until KWs re-worked to PAPI                                             |
|   | <https://jira.fd.io/browse/CSIT-1371>`_ | Map commands were remove from VAT by VPP patch https://gerrit.fd.io/r/#/c/16115/.                                       |
+---+-----------------------------------------+-------------------------------------------------------------------------------------------------------------------------+

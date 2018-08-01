Release Notes
=============

Changes in |csit-release|
-------------------------

#. Code updates in CSIT functional framework:

   - few test case bug fixes.

#. VPP_Path:

   - Implementation of new VPP-make_test VPP integration tests for functional
     acceptance of VPP feature path(s) driven by use case(s).

   - All VIRL P0 tests (`CSIT_VIRL migration progress
     <https://docs.google.com/spreadsheets/d/1PciV8XN9v1qHbIRUpFJoqyES29_vik7lcFDl73G1usc/edit?usp=sharing>`_)
     migrated to VPP_Path using VPP make test.

Known Issues
------------

List of known issues in |csit-release| for VPP functional tests in VIRL:

+---+-------------------------------------------------+----------+------------------------------------------------------+
| # | .. centered:: Issue                             | Jira ID  | .. centered:: Description                            |
+===+=================================================+==========+======================================================+
| 1 | DHCPv4 client: Client responses to DHCPv4 OFFER | CSIT-129 | Client replies with DHCPv4 REQUEST message when      |
|   | sent with different XID.                        | VPP-99   | received DHCPv4 OFFER message with different (wrong) |
|   |                                                 |          | XID.                                                 |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 2 | Softwire - MAP-E: Incorrect calculation of IPv6 | CSIT-398 | IPv6 destination address is wrongly calculated in    |
|   | destination address when IPv4 prefix is 0.      | VPP-380  | case that IPv4 prefix is equal to 0 and IPv6 prefix  |
|   |                                                 |          | is less than 40.                                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 3 | Softwire - MAP-E: Map domain is created when    | CSIT-399 | Map domain is created in case that the sum of suffix |
|   | incorrect parameters provided.                  | VPP-435  | length of IPv4 prefix and PSID length is greater     |
|   |                                                 |          | than EA bits length. IPv6 destination address        |
|   |                                                 |          | contains bits writen with PSID over the EA-bit       |
|   |                                                 |          | length when IPv4 packet is sent.                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 4 | IPv6 RA: Incorrect IPv6 destination address in  | CSIT-409 | Wrong IPv6 destination address (ff02::1) is used in  |
|   | response to ICMPv6 Router Solicitation.         | VPP-406  | ICMPv6 Router Advertisement packet sent as a         |
|   |                                                 |          | response to received  ICMPv6 Router Solicitation     |
|   |                                                 |          | packet.                                              |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 5 | Vhost-user: QEMU reconnect does not work.       | CSIT-565 | Used QEMU 2.5.0 does not support vhost-user          |
|   |                                                 |          | reconnect. Requires upgrading CSIT VIRL environment  |
|   |                                                 |          | to QEMU 2.7.0.                                       |
+---+-------------------------------------------------+----------+------------------------------------------------------+

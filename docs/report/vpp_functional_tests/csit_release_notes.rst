CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Code updates and optimizations in CSIT functional framework:

   - VPP install test - VPP installation have been moved to separate test in
   test suite setup phase to clearly indicate any issue with VPP installation;

   - VPP verify test - test to check VPP responsiveness after installation;

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP functional tests in VIRL:

+---+-------------------------------------------------+----------+------------------------------------------------------+
| # | Issue                                           | Jira ID  | Description                                          |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 1 | DHCPv4 client: Client responses to DHCPv4 OFFER | CSIT-129 | Client replies with DHCPv4 REQUEST message when      |
|   | sent with different XID.                        |          | received DHCPv4 OFFER message with different (wrong) |
|   |                                                 |          | XID.                                                 |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 2 | Softwire - MAP-E: Incorrect calculation of IPv6 | CSIT-398 | IPv6 destination address is wrongly calculated in    |
|   | destination address when IPv4 prefix is 0.      |          | case that IPv4 prefix is equal to 0 and IPv6 prefix  |
|   |                                                 |          | is less than 40.                                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 3 | Softwire - MAP-E: Map domain is created when    | CSIT-399 | Map domain is created in case that the sum of suffix |
|   | incorrect parameters provided.                  |          | length of IPv4 prefix and PSID length is greater     |
|   |                                                 |          | than EA bits length. IPv6 destination address        |
|   |                                                 |          | contains bits writen with PSID over the EA-bit       |
|   |                                                 |          | length when IPv4 packet is sent.                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 4 | IPv6 RA: Incorrect IPv6 destination address in  | CSIT-409 | Wrong IPv6 destination address (ff02::1) is used in  |
|   | response to ICMPv6 Router Solicitation.         |          | ICMPv6 Router Advertisement packet sent as a         |
|   |                                                 |          | response to received  ICMPv6 Router Solicitation     |
|   |                                                 |          | packet.                                              |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 5 | Vhost-user: QEMU reconnect does not work.       | CSIT-565 | Using QEMU 2.5.0 that does not support vhost-user    |
|   |                                                 |          | reconnect. It requires moving CSIT VIRL environment  |
|   |                                                 |          | to QEMU 2.7.0.                                       |
+---+-------------------------------------------------+----------+------------------------------------------------------+

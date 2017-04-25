CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Introduction of Centos7 tests

#. Added VPP functional tests

    - more VM vhost-user tests incl. two VM four vhost interface tests
    - more LISP tests
    - more IPSec crypto tests
    - IPv4 and IPv6 Equal-Cost Multi-Path routing tests
    - Telemetry:
      - IPFIX tests
      - SPAN tests

Known Issues - to be updated
------------

Here is the list of known issues in CSIT |release| for VPP functional tests in VIRL: (to be updated)

+---+-------------------------------------------------+-----------------------------------------------------------------+
| # | Issue                                           | Description                                                     |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 1 | DHCPv4 client: Client responses to DHCPv4 OFFER | Client replies with DHCPv4 REQUEST message when received DHCPv4 |
|   | sent with different XID                         | OFFER message with different (wrong) XID.                       |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 2 | Softwire - MAP-E: Incorrect calculation of IPv6 | IPv6 destination address is wrongly calculated in case that     |
|   | destination address when IPv4 prefix is 0       | IPv4 prefix is equal to 0 and IPv6 prefix is less than 40.      |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 3 | Softwire - MAP-E: Map domain is created when    | Map domain is created in case that the sum of suffix length of  |
|   | incorrect parameters provided                   | IPv4 prefix and PSID length is greater than EA bits length.     |
|   |                                                 | IPv6 destination address contains bits writen with PSID over    |
|   |                                                 | the EA-bit length when IPv4 packet is sent.                     |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 4 | IPv6 RA: Incorrect IPv6 destination address in  | Wrong IPv6 destination address (ff02::1) is used in ICMPv6      |
|   | response to ICMPv6 Router Solicitation          | Router Advertisement packet sent as a response to received      |
|   |                                                 | ICMPv6 Router Solicitation packet.                              |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 5 | IPFIX: IPv6_src key name reported instead of    | The report contains IPv6_src key name instead of IPv6_dst when  |
|   | IPv6_dst                                        | classify session is configured with IPv6 destination address.   |
|   |                                                 | Anyhow the correct IPv6 destination address is reported.        |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 6 | SPAN: Tx traffic is not mirrored                | Tx traffic is not mirrored from SPAN source port to SPAN        |
|   |                                                 | destination port.                                               |
|   |                                                 | NOTE: Fix is going to be merged in vpp stable/1701.             |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 7 | SPAN: Packet trace always contains local0 as    | There is reported wrong destination port in the traffic trace:  |
|   | destination port                                |         SPAN: mirrored GigabitEthernet0/5/0 -> local0           |
|   |                                                 | The (Rx) traffic is mirrored to correct destination port.       |
+---+-------------------------------------------------+-----------------------------------------------------------------+


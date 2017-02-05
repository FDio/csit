
.. |br| raw:: html

    <br />

CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Naming change for all VPP functional test suites in VIRL

    - VPP functional test case names stayed unchanged

#. VPP functional test environment changes

    - upgrade to Ubuntu 16.04
    - VM and vhost-user test environment optimizations

#. Introduction of Centos tests

#. Added VPP functional tests

    - more VM vhost-user tests
    - more LISP tests
    - more IPSec crypto tests
    - IPv4 and IPv6 Equal-Cost Multi-Path routing tests
    - Telemetry:
      - IPFIX tests
      - SPAN tests

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP functional tests in VIRL:

+-------------------------------------------------+-----------------------------------------------------------------+
| ISSUE                                           | DESCRIPTION                                                     |
+-------------------------------------------------+-----------------------------------------------------------------+
| DHCPv4 client: Client responses to DHCPv4 OFFER | Client replies with DHCPv4 REQUEST message when received DHCPv4 |
| sent with different XID                         | OFFER message with different (wrong) XID.                       |
+-------------------------------------------------+-----------------------------------------------------------------+
| Softwire - MAP-E: Incorrect calculation of IPv6 | IPv6 destination address is wrongly calculated in case that     |
| destination address when IPv4 prefix is 0       | IPv4 prefix is equal to 0 and IPv6 prefix is less than 40.      |
+-------------------------------------------------+-----------------------------------------------------------------+
| Softwire - MAP-E: Map domain is created when    | Map domain is created in case that the sum of suffix length of  |
| incorrect parameters provided                   | IPv4 prefix and PSID length is greater than EA bits length.     |
|                                                 | IPv6 destination address contains bits writen with PSID over    |
|                                                 | the EA-bit length when IPv4 packet is sent.                     |
+-------------------------------------------------+-----------------------------------------------------------------+
| IPv6 RA: Incorrect IPv6 destination address in  | Wrong IPv6 destination address (ff02::1) is used in ICMPv6      |
| response to ICMPv6 Router Solicitation          | Router Advertisement packet sent as a response to received      |
|                                                 | ICMPv6 Router Solicitation packet.                              |
+-------------------------------------------------+-----------------------------------------------------------------+
| IPFIX: IPv6_src key name reported instead of    | The report contains IPv6_src key name instead of IPv6_dst when  |
| IPv6_dst                                        | classify session is configured with IPv6 destination address.   |
|                                                 | Anyhow the correct IPv6 destination address is reported.        |
+-------------------------------------------------+-----------------------------------------------------------------+
| SPAN: Tx traffic is not mirrored                | Tx traffic is not mirrored from SPAN source port to SPAN        |
|                                                 | destination port. |br|                                          |
|                                                 | NOTE: Fix is going to be merged in vpp stable/1701.             |
+-------------------------------------------------+-----------------------------------------------------------------+
| SPAN: Packet trace always contains local0 as    | There is reported wrong destination port in the traffic trace:  |
| destination port                                | |br|    SPAN: mirrored GigabitEthernet0/5/0 -> local0    |br|   |
|                                                 | The (Rx) traffic is mirrored to correct destination port.       |
+-------------------------------------------------+-----------------------------------------------------------------+

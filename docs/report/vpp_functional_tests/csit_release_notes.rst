CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Introduction of Centos7 tests (please, see item 8 of known issues)

#. Added VPP functional tests

    - more VLAN tests (IPv4 routing, L2BD with VM)
    - more vhost-user interface tests
    - implemented VAT command history (in the teardown of every test case)

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP functional tests in VIRL:

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
| 6 | IPv4 + VLAN: Processing of tagged frame doesn't | Dot1q tagged packets are thrown away in case of IPv4 routing on |
|   | work with virtio driver                         | interface binded to virtio driver.                              |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 7 | VHOST-user: QEMU re-connect doesn't work        | Used QEMU 2.5.0 doesn't support re-connection. Usage of QEMU    |
|   |                                                 | 2.7.0 is not recommended by vpp-dev team at the moment.         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 8 | Centos7: LISP and VXLAN test failures           | We can observe crash of SUT1 VM during LISP tests execution,    |
|   |                                                 | that leads to failure of all other tests (sometimes observed    |
|   |                                                 | during VXLAN tests execution too). |br|                         |
|   |                                                 | NOTE: Possible root cause identified after upgrade of one of    |
|   |                                                 | VIRL servers. When fix is confirmed in a short time it will be  |
|   |                                                 | merged to CSIT rls1704 branch.                                  |
+---+-------------------------------------------------+-----------------------------------------------------------------+

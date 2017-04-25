CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Introduction of Centos7 tests

#. Added VPP functional tests

    - IPv4 routed-forwarding with dot1q VLAN sub-interfaces
    - L2BD switched-forwarding with dot1q VLAN sub-interfaces and vhost-user to VM
    - IPv4 routed-forwarding with vhost-user interfaces to VM
    - Vhost-User interface re-connect tests

#. Implemented VAT command history collection for every test case as part of teardown.


Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP functional tests in VIRL:

+---+-------------------------------------------------+-----------------------------------------------------------------+
| # | Issue                                           | Description                                                     |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 1 | DHCPv4 client: Client responses to DHCPv4 OFFER | Client replies with DHCPv4 REQUEST message when received DHCPv4 |
|   | sent with different XID                         | OFFER message with different (wrong) XID.                       |
|   |                                                 | Jira: ` CSIT-129 <https://jira.fd.io/browse/CSIT-129>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 2 | Softwire - MAP-E: Incorrect calculation of IPv6 | IPv6 destination address is wrongly calculated in case that     |
|   | destination address when IPv4 prefix is 0       | IPv4 prefix is equal to 0 and IPv6 prefix is less than 40.      |
|   |                                                 | Jira: ` CSIT-398 <https://jira.fd.io/browse/CSIT-398>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 3 | Softwire - MAP-E: Map domain is created when    | Map domain is created in case that the sum of suffix length of  |
|   | incorrect parameters provided                   | IPv4 prefix and PSID length is greater than EA bits length.     |
|   |                                                 | IPv6 destination address contains bits writen with PSID over    |
|   |                                                 | the EA-bit length when IPv4 packet is sent.                     |
|   |                                                 | Jira: ` CSIT-399 <https://jira.fd.io/browse/CSIT-399>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 4 | IPv6 RA: Incorrect IPv6 destination address in  | Wrong IPv6 destination address (ff02::1) is used in ICMPv6      |
|   | response to ICMPv6 Router Solicitation          | Router Advertisement packet sent as a response to received      |
|   |                                                 | ICMPv6 Router Solicitation packet.                              |
|   |                                                 | Jira: ` CSIT-409 <https://jira.fd.io/browse/CSIT-409>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 5 | IPFIX: IPv6_src key name reported instead of    | The report contains IPv6_src key name instead of IPv6_dst when  |
|   | IPv6_dst                                        | classify session is configured with IPv6 destination address.   |
|   |                                                 | Anyhow the correct IPv6 destination address is reported.        |
|   |                                                 | Jira: ` CSIT-402 <https://jira.fd.io/browse/CSIT-402>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 6 | IPv4 + VLAN: Processing of tagged frame doesn't | Dot1q tagged packets are thrown away in case of IPv4 routing on |
|   | work with virtio driver                         | interface binded to virtio driver.                              |
|   |                                                 | Jira: ` CSIT-564 <https://jira.fd.io/browse/CSIT-564>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 7 | VHOST-user: QEMU re-connect doesn't work        | Used QEMU 2.5.0 doesn't support re-connection. Usage of QEMU    |
|   |                                                 | 2.7.0 is not recommended by vpp-dev team at the moment.         |
|   |                                                 | Jira: ` CSIT-565 <https://jira.fd.io/browse/CSIT-565>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 8 | Centos7: LISP and VXLAN test failures           | We can observe crash of SUT1 VM during LISP tests execution,    |
|   |                                                 | that leads to failure of all other tests (sometimes observed    |
|   |                                                 | during VXLAN tests execution too).                              |
|   |                                                 | NOTE: Possible root cause identified after upgrade of one of    |
|   |                                                 | VIRL servers. When fix is confirmed in a short time it will be  |
|   |                                                 | merged to CSIT rls1704 branch.                                  |
|   |                                                 | Jira: ` CSIT-566 <https://jira.fd.io/browse/CSIT-566>`_         |
+---+-------------------------------------------------+-----------------------------------------------------------------+

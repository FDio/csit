CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Introduction of Centos7 tests

#. Implemented VAT command history collection for every test case as part of teardown

#. Added VPP functional tests

    - IPv4 routed-forwarding with dot1q VLAN sub-interfaces
    - L2BD switched-forwarding with dot1q VLAN sub-interfaces and vhost-user to VM
    - IPv4 routed-forwarding with vhost-user interfaces to VM
    - Vhost-User interface re-connect tests

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP functional tests in VIRL:

+---+-------------------------------------------------+----------+------------------------------------------------------+
| # | Issue                                           | Jira ID  | Description                                          |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 1 | DHCPv4 client: Client responses to DHCPv4 OFFER | CSIT-129 | Client replies with DHCPv4 REQUEST message when      |
|   | sent with different XID                         |          | received DHCPv4 OFFER message with different (wrong) |
|   |                                                 |          | XID.                                                 |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 2 | Softwire - MAP-E: Incorrect calculation of IPv6 | CSIT-398 | IPv6 destination address is wrongly calculated in    |
|   | destination address when IPv4 prefix is 0       |          | case that IPv4 prefix is equal to 0 and IPv6 prefix  |
|   |                                                 |          | is less than 40.                                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 3 | Softwire - MAP-E: Map domain is created when    | CSIT-399 | Map domain is created in case that the sum of suffix |
|   | incorrect parameters provided                   |          | length of IPv4 prefix and PSID length is greater     |
|   |                                                 |          | than EA bits length. IPv6 destination address        |
|   |                                                 |          | contains bits writen with PSID over the EA-bit       |
|   |                                                 |          | length when IPv4 packet is sent.                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 4 | IPv6 RA: Incorrect IPv6 destination address in  | CSIT-409 | Wrong IPv6 destination address (ff02::1) is used in  |
|   | response to ICMPv6 Router Solicitation          |          | ICMPv6 Router Advertisement packet sent as a         |
|   |                                                 |          | response to received  ICMPv6 Router Solicitation     |
|   |                                                 |          | packet.                                              |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 5 | IPFIX: IPv6_src key name reported instead of    | CSIT-402 | The report contains IPv6_src key name instead of     |
|   | IPv6_dst                                        |          | IPv6_dst when classify session is configured with    |
|   |                                                 |          | IPv6 destination address. Anyhow the correct IPv6    |
|   |                                                 |          | destination address is reported.                     |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 6 | IPv4 + VLAN: Processing of tagged frame doesn't | CSIT-564 | Dot1q tagged packets are thrown away in case of IPv4 |
|   | work with virtio driver                         |          | routing on interface binded to virtio driver.        |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 7 | VHOST-user: QEMU re-connect doesn't work        | CSIT-565 | Used QEMU 2.5.0 doesn't support re-connection. Usage |
|   |                                                 |          | of QEMU 2.7.0 is not recommended by vpp-dev team at  |
|   |                                                 |          | the moment.                                          |
+---+-------------------------------------------------+----------+------------------------------------------------------+
| 8 | Centos7: LISP and VXLAN test failures           | CSIT-566 | We can observe crash of SUT1 VM during LISP tests    |
|   |                                                 |          | execution, that leads to failure of all other tests  |
|   |                                                 |          | (sometimes observed  during VXLAN tests execution    |
|   |                                                 |          | too). NOTE: Possible root cause identified after     |
|   |                                                 |          | upgrade of one of VIRL servers. When fix is          |
|   |                                                 |          | confirmed in a short time it will be merged to CSIT  |
|   |                                                 |          | rls1704 branch.                                      |
+---+-------------------------------------------------+----------+------------------------------------------------------+

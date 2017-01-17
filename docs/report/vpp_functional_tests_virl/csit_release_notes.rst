
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

Functional Tests Naming
-----------------------

CSIT |release| introduced a common structured naming convention for all
performance and functional tests. This change was driven by substantially
growing number and type of CSIT test cases. Firstly, the original practice did
not always follow any strict naming convention. Secondly test names did not
always clearly capture tested packet encapsulations, and the actual type or
content of the tests. Thirdly HW configurations in terms of NICs, ports and
their locality were not captured either. These were but few reasons that drove
the decision to change and define a new more complete and stricter test naming
convention, and to apply this to all existing and new test cases.

The new naming should be intuitive for majority of the tests. The complete
description of CSIT test naming convention is provided on `CSIT test naming
page <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.

Here few illustrative examples of the new naming usage for functional test
suites:

#. **Physical port to physical port - a.k.a. NIC-to-NIC, Phy-to-Phy, P2P**

    - *eth2p-ethip4-ip4base-func.robot* => 2 ports of Ethernet, IPv4 baseline
      routed forwarding, functional tests.

#. **Physical port to VM (or VM chain) to physical port - a.k.a. NIC2VM2NIC,
   P2V2P, NIC2VMchain2NIC, P2V2V2P**

    - *eth2p-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-func.robot* => 2 ports of
      Ethernet, IPv4 VXLAN Ethernet, L2 bridge-domain switching to/from two vhost
      interfaces and one VM, functional tests.

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

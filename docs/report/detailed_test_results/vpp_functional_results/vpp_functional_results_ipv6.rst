
.. |br| raw:: html

    <br />

IPv6 Routed-Forwarding
----------------------

eth2p-ethip6-ip6base-func
'''''''''''''''''''''''''

**IPv6 routing test cases**  RFC2460 IPv6, RFC4443 ICMPv6, RFC4861 Neighbor Discovery. Encapsulations: Eth-IPv6-ICMPv6 on links TG-DUT1, TG-DUT2, DUT1-DUT2; Eth-IPv6-NS/NA on links TG-DUT. IPv6 routing tests use circular 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured with IPv6 routing and static routes. Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2 and received on TG links on the other side of circular topology. On receive TG verifies packets IPv6 src-addr, dst-addr and MAC addresses.

+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                    | Documentation                                                                                                                                                                             | Status |
+=========================================================================+===========================================================================================================================================================================================+========+
| TC01: DUT replies to ICMPv6 Echo Req to its ingress interface           | Make TG send ICMPv6 Echo Req to DUT ingress interface. Make TG verify ICMPv6 Echo Reply is correct.                                                                                       | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT replies to ICMPv6 Echo Req pkt with size 64B-to-1500B-incr-1B | Make TG send ICMPv6 Echo Reqs to DUT ingress interface, incrementating frame size from 64B to 1500B with increment step of 1Byte. Make TG verify ICMP Echo Replies are correct.           | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT routes to its egress interface                                | Make TG send ICMPv6 Echo Req towards DUT1 egress interface connected to DUT2. Make TG verify ICMPv6 Echo Reply is correct.                                                                | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: DUT1 routes to DUT2 ingress interface                             | Make TG send ICMPv6 Echo Req towards DUT2 ingress interface connected to DUT1. Make TG verify ICMPv6 Echo Reply is correct.                                                               | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: DUT1 routes to DUT2 egress interface                              | Make TG send ICMPv6 Echo Req towards DUT2 egress interface connected to TG. Make TG verify ICMPv6 Echo Reply is correct.                                                                  | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: DUT1 and DUT2 route between TG interfaces                         | Make TG send ICMPv6 Echo Req between its interfaces across DUT1 and DUT2. Make TG verify ICMPv6 Echo Replies are correct.                                                                 | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC08: DUT replies to IPv6 Neighbor Solicitation                         | On DUT configure interface IPv6 address in the main routing domain. Make TG send Neighbor Solicitation message on the link to DUT and verify DUT Neighbor Advertisement reply is correct. | PASS   |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6-ip6base-ip6ecmp-func
'''''''''''''''''''''''''''''''''

**Ipv6 Multipath routing test cases**   

 - **[Top] Network topologies:** TG=DUT 2-node topology with two links between nodes.  

 - **[Cfg] DUT configuration:** On DUT configure interfaces IPv4 adresses, and multipath routing.  

 - **[Ver] TG verification:** Test packets are sent from TG on the first link to DUT. Packet is received on TG on the second link from DUT1.

+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                    | Documentation                                                                                                                                                                                                                               | Status |
+=========================================+=============================================================================================================================================================================================================================================+========+
| TC01: IPv6 Equal-cost multipath routing | [Top] TG=DUT  |br| [Cfg] On DUT configure multipath routing wiht two equal-cost paths.  |br| [Ver] TG sends 100 IPv6 ICMP packets traffic on the first link to DUT. On second link to TG verify if traffic is divided into two paths.       | PASS   |
+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6-ip6base-ip6ra-func
'''''''''''''''''''''''''''''''

**IPv6 Router Advertisement test cases**  RFC4861 Neighbor Discovery. Encapsulations: Eth-IPv6-RA on links TG-DUT1. IPv6 Router Advertisement tests use 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured with IPv6 routing and static routes. TG verifies received RA packets.

+--------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                           | Documentation                                                                                                                                                                                                                                                                                                 | Status |
+================================================================================+===============================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT transmits RA on IPv6 enabled interface                               | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 configure IPv6 interface on the link to TG.  |br| [Ver] Make TG wait for IPv6 Router Advertisement packet to be sent by DUT1 and verify the received RA packet is correct.                                                                                         | PASS   |
+--------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT retransmits RA on IPv6 enabled interface after a set interval        | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 configure IPv6 interface on the link to TG.  |br| [Ver] Make TG wait for two IPv6 Router Advertisement packets to be sent by DUT1 and verify the received RA packets are correct.                                                                                  | PASS   |
+--------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT responds to Router Solicitation request                              | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 configure IPv6 interface on the link to TG and suppress sending of Router Advertisement packets periodically.  |br| [Ver] Make TG send IPv6 Router Solicitation request to DUT1, listen for response from DUT1 and verify the received RA packet is correct.       | FAIL   |
+--------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT responds to Router Solicitation request sent from link local address | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 configure IPv6 interface on the link to TG and suppress sending of Router Advertisement packets periodically.  |br| [Ver] Make TG send IPv6 Router Solicitation request to DUT1, listen for response from DUT1 and verify the received RA packet is correct.       | FAIL   |
+--------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


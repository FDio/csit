
.. |br| raw:: html

    <br />

IPv4 Routed-Forwarding
----------------------

eth2p-ethip4-ip4base-func
'''''''''''''''''''''''''

**IPv4 routing test cases**  RFC791 IPv4, RFC826 ARP, RFC792 ICMPv4. Encapsulations: Eth-IPv4-ICMPv4 on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv4 routing tests use circular 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured with IPv4 routing and static routes. Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2 and received on TG links on the other side of circular topology. On receive TG verifies packets IPv4 src-addr, dst-addr and MAC addresses.

+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                 | Documentation                                                                                                                                                                   | Status |
+======================================================================+=================================================================================================================================================================================+========+
| TC01: DUT replies to ICMPv4 Echo Req to its ingress interface        | Make TG send ICMPv4 Echo Req to DUT ingress interface. Make TG verify ICMP Echo Reply is correct.                                                                               | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT routes IPv4 to its egress interface                        | Make TG send ICMPv4 Echo Req towards DUT1 egress interface connected to DUT2. Make TG verify ICMPv4 Echo Reply is correct.                                                      | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT1 routes IPv4 to DUT2 ingress interface                     | Make TG send ICMPv4 Echo Req towards DUT2 ingress interface connected to DUT1. Make TG verify ICMPv4 Echo Reply is correct.                                                     | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT1 routes IPv4 to DUT2 egress interface                      | Make TG send ICMPv4 Echo Req towards DUT2 egress interface connected to TG. Make TG verify ICMPv4 Echo Reply is correct.                                                        | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: DUT1 and DUT2 route IPv4 between TG interfaces                 | Make TG send ICMPv4 Echo Req between its interfaces across DUT1 and DUT2. Make TG verify ICMPv4 Echo Replies are correct.                                                       | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: DUT replies to ICMPv4 Echo Reqs with size 64B-to-1500B-incr-1B | Make TG send ICMPv4 Echo Reqs to DUT ingress interface, incrementating frame size from 64B to 1500B with increment step of 1Byte. Make TG verify ICMP Echo Replies are correct. | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC08: DUT replies to ARP request                                     | Make TG send ARP Request to DUT and verify ARP Reply is correct.                                                                                                                | PASS   |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-ip4base-ip4arp-func
''''''''''''''''''''''''''''''''

**IPv4 ARP test cases**  RFC826 ARP: Eth-IPv4 and Eth-ARP on links TG-DUT1, TG-DUT2, DUT1-DUT2: IPv4 ARP tests use 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured with IPv4 routing and static routes. DUT ARP functionality is tested by making TG send ICMPv4 Echo Requests towards its other interface via DUT1 and DUT2.

+---------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                      | Documentation                                                                                                                                                            | Status |
+===========================================================================+==========================================================================================================================================================================+========+
| TC01: DUT sends ARP Request for unresolved locally connected IPv4 address | Make TG send test packet destined to IPv4 address of its other interface connected to DUT2. Make TG verify DUT2 sends ARP Request for locally connected TG IPv4 address. | PASS   |
+---------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT sends ARP Request for route next hop IPv4 address               | Make TG send test packet destined to IPv4 address matching static route on DUT2. Make TG verify DUT2 sends ARP Request for next hop of the static route.                 | PASS   |
+---------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-ip4base-ip4ecmp-func
'''''''''''''''''''''''''''''''''

**Ipv4 Multipath routing test cases**   

 - **[Top] Network topologies:** TG=DUT 2-node topology with two links between nodes.  

 - **[Cfg] DUT configuration:** On DUT configure interfaces IPv4 adresses, and multipath routing.  

 - **[Ver] TG verification:** Test packets are sent from TG on the first link to DUT. Packet is received on TG on the second link from DUT1.

+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                    | Documentation                                                                                                                                                                                                                               | Status |
+=========================================+=============================================================================================================================================================================================================================================+========+
| TC01: IPv4 Equal-cost multipath routing | [Top] TG=DUT  |br| [Cfg] On DUT configure multipath routing wiht two equal-cost paths.  |br| [Ver] TG sends 100 IPv4 ICMP packets traffic on the first link to DUT. On second link to TG verify if traffic is divided into two paths.       | PASS   |
+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-ip4base-ip4proxyarp-func
'''''''''''''''''''''''''''''''''''''

**RFC1027 Proxy ARP test cases**   

 - **[Top] Network topologies:** TG-DUT1 2-node topology with single link between nodes.  

 - **[Cfg] DUT configuration:** DUT1 is configured with Proxy ARP  

 - **[Ver] TG verification:** Test ARP Request packet is sent from TG on link to DUT1; on receive TG verifies ARP reply packet for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC1027.

+-------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                      | Documentation                                                                                                                                                                                                                                                                              | Status |
+===========================================================================================+============================================================================================================================================================================================================================================================================================+========+
| TC01: DUT sends ARP reply on behalf of another machine from the IP range                  | [Top] TG-DUT1.  |br| [Ref] RFC1027.  |br| [Cfg] On DUT1 configure interface IPv4 address and proxy ARP for IP range.  |br| [Ver] Make TG send ARP request to DUT1 interface, verify if DUT1 sends correct ARP reply on behalf of machine which IP is in range.                             | PASS   |
+-------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT sends ARP reply on behalf of another machine from beginning of the IP range     | [Top] TG-DUT1.  |br| [Ref] RFC1027.  |br| [Cfg] On DUT1 configure interface IPv4 address and proxy ARP for IP range.  |br| [Ver] Make TG send ARP request to DUT1 interface, verify if DUT1 sends correct ARP reply on behalf of machine which IP is from beginning of the IP range.       | PASS   |
+-------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT sends ARP reply on behalf of another machine from end of the IP range           | [Top] TG-DUT1.  |br| [Ref] RFC1027.  |br| [Cfg] On DUT1 configure interface IPv4 address and proxy ARP for IP range.  |br| [Ver] Make TG send ARP request to DUT1 interface, verify if DUT1 sends correct ARP reply on behalf of machine which IP is from end of the IP range.             | PASS   |
+-------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT does not send ARP reply on behalf of another machine from below of the IP range | [Top] TG-DUT1.  |br| [Ref] RFC1027.  |br| [Cfg] On DUT1 configure interface IPv4 address and proxy ARP for IP range.  |br| [Ver] Make TG send ARP request to DUT1 interface, verify if DUT1 does not send ARP reply on behalf of machine which IP is from below of the IP range.           | PASS   |
+-------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: DUT does not send ARP reply on behalf of another machine from above of the IP range | [Top] TG-DUT1.  |br| [Ref] RFC1027.  |br| [Cfg] On DUT1 configure interface IPv4 address and proxy ARP for IP range.  |br| [Ver] Make TG send ARP request to DUT1 interface, verify if DUT1 does not send ARP reply on behalf of machine which IP is from above of the IP range.           | PASS   |
+-------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


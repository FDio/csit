
.. |br| raw:: html

    <br />

L2XC Ethernet Switching
-----------------------

eth2p-eth-l2xcbase-eth-2vhost-1vm-func
''''''''''''''''''''''''''''''''''''''

**L2 cross-connect test cases**   

 - **[Top] Network Topologies:** TG=DUT=VM 3-node topology with VM and double parallel links.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 is configured with L2 cross-connect (L2XC) switching.  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 via VM; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                   | Documentation                                                                                                                                                                                                                                                                                                                                                                 | Status |
+========================================================================+===============================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT with two L2XCs switches ICMPv4 between TG and local VM links | [Top] TG=DUT=VM.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT configure  two L2 cross-connects (L2XC), each with one untagged interface to TG and untagged i/f to local VM over vhost-user.  |br| [Ver] Make TG send ICMPv4 Echo Reqs in both directions between two of its i/fs to be switched by DUT to and from VM; verify all packets are received.  |br| [Ref]        | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with two L2XCs switches ICMPv6 between TG and local VM links | [Top] TG=DUT=VM.  |br| [Enc] Eth-IPv6-ICMPv6.  |br| [Cfg] On DUT configure  two L2 cross-connects (L2XC), each with one untagged i/f to TG and untagged i/f to local VM over vhost-user.  |br| [Ver] Make TG send ICMPv6 Echo Reqs in both directions between two of its i/fs to be switched by DUT to and from VM; verify all packets are received.  |br| [Ref]              | PASS   |
+------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-eth-l2xcbase-func
'''''''''''''''''''''''

**L2 cross-connect test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 cross-connect (L2XC) switching.  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                             | Documentation                                                                                                                                                                                                                                                                                                                                                                      | Status |
+==================================================================+====================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 with L2XC switch ICMPv4 between two TG links | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 and  DUT2 configure L2 cross-connect (L2XC), each with one interface to TG and one Ethernet interface towards the other DUT.  |br| [Ver] Make TG send ICMPv4 Echo Req in both directions between two of its interfaces to be switched by DUT1 and DUT2; verify all packets are received.  |br| [Ref]       | PASS   |
+------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 with L2XC switch ICMPv6 between two TG links | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-ICMPv6.  |br| [Cfg] On DUT1 and  DUT2 configure L2 cross-connect (L2XC), each with one interface to TG and one Ethernet interface towards the other DUT.  |br| [Ver] Make TG send ICMPv6 Echo Req in both directions between two of its interfaces to be switched by DUT1 and DUT2; verify all packets are received.  |br| [Ref]       | PASS   |
+------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+



.. |br| raw:: html

    <br />

L2BD Ethernet Switching
-----------------------

eth2p-eth-l2bdbasemaclrn-eth-2vhost-1vm-func
''''''''''''''''''''''''''''''''''''''''''''

**L2 bridge-domain test cases**   

 - **[Top] Network Topologies:** TG=DUT=VM 3-node topology with VM and double parallel links.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 is configured with two L2 bridge-domains (L2BD) switching combined with MAC learning enabled.  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 via VM; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                         | Documentation                                                                                                                                                                                                                                                                                                                                                            | Status |
+==============================================================================+==========================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT with two L2BDs (MAC learn) switches ICMPv4 between TG and VM links | [Top] TG=DUT=VM.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure  two L2BDs with MAC learning, each with vhost-user i/f to local VM and i/f to TG; configure VM to loop pkts back betwen its two virtio i/fs.  |br| [Ver] Make TG verify ICMPv4 Echo Req pkts are switched thru DUT1 and VM in both directions and are correct on receive.  |br| [Ref]        | PASS   |
+------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with two L2BDs (MAC learn) switches ICMPv6 between TG and VM links | [Top] TG=DUT=VM.  |br| [Enc] Eth-IPv6-ICMPv6.  |br| [Cfg] On DUT1 configure  two L2BDs with MAC learning, each with vhost-user i/f to local VM and i/f to TG; configure VM to loop pkts back betwen its two virtio i/fs.  |br| [Ver] Make TG verify ICMPv6 Echo Req pkts are switched thru DUT1 and VM in both directions and are correct on receive.  |br| [Ref]        | PASS   |
+------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-eth-l2bdbasemaclrn-func
'''''''''''''''''''''''''''''

**L2 bridge-domain test cases**   

 - **[Top] Network Topologies:** TG=DUT1 2-node topology with two links between nodes; TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge-domain (L2BD) switching combined with MAC learning enabled.  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+--------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                     | Documentation                                                                                                                                                                                                                                                                      | Status |
+==========================================================================+====================================================================================================================================================================================================================================================================================+========+
| TC01: DUT reports active interfaces                                      | [Top] TG=DUT1; TG-DUT1-DUT2-TG.  |br| [Enc] None.  |br| [Cfg] Discovered  active interfaces.  |br| [Ver] Report active interfaces on DUT.  |br| [Ref]                                                                                                                              | PASS   |
+--------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with L2BD (MAC learning) switch ICMPv4 between two TG links    | [Top] TG=DUT1.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure  two i/fs into L2BD with MAC learning.  |br| [Ver] Make TG verify ICMPv4 Echo Req pkts are switched thru DUT1 in both directions and are correct on receive.  |br| [Ref]                                 | PASS   |
+--------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT1 and DUT2 with L2BD (MAC learning) switch between two TG links | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 and DUT2  configure two i/fs into L2BD with MAC learning.  |br| [Ver] Make TG verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2 in both directions and are correct on receive.  |br| [Ref]       | PASS   |
+--------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-eth-l2bdbasemacstc-eth-2vhost-1vm-func
''''''''''''''''''''''''''''''''''''''''''''

**L2 bridge-domain test cases**   

 - **[Top] Network Topologies:** TG=DUT=VM 3-node topology with VM and double parallel links.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 is configured with two L2 bridge-domains (L2BD) switching combined with static MACs.  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 via VM; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+--------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                           | Documentation                                                                                                                                                                                                                                                                                                                                                           | Status |
+================================================================================+=========================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT with two L2BDs (static MACs) switches ICMPv4 between TG and VM links | [Top] TG=DUT=VM.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure  two L2BDs with static MACs, each with vhost-user i/f to local VM and i/f to TG; configure VM to loop pkts back betwen its two virtio i/fs.  |br| [Ver] Make TG verify ICMPv4 Echo Req pkts are switched thru DUT1 and VM in both directions and are correct on receive.  |br| [Ref]        | PASS   |
+--------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with two L2BDs (static MACs) switches ICMPv6 between TG and VM links | [Top] TG=DUT=VM.  |br| [Enc] Eth-IPv6-ICMPv6.  |br| [Cfg] On DUT1 configure  two L2BDs with static MACs, each with vhost-user i/f to local VM and i/f to TG; configure VM to loop pkts back betwen its two virtio i/fs.  |br| [Ver] Make TG verify ICMPv6 Echo Req pkts are switched thru DUT1 and VM in both directions and are correct on receive.  |br| [Ref]        | PASS   |
+--------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-eth-l2bdbasemacstc-func
'''''''''''''''''''''''''''''

**L2 bridge-domain test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge-domain (L2BD) switching combined with static MACs.  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+-------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                    | Documentation                                                                                                                                                                                                                                                                     | Status |
+=========================================================================+===================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 with L2BD (static MACs) switch between two TG links | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 and  DUT2 configure two i/fs into L2BD with static MACs.  |br| [Ver] Make TG verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2 in both directions and are correct on receive.  |br| [Ref]       | PASS   |
+-------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth4p-eth-l2bdbasemaclrn-l2shg-func
'''''''''''''''''''''''''''''''''''

**L2 bridge-domain test cases**   

 - **[Top] Network Topologies:** TG=DUT1=DUT2=TG 3-node circular topology with double parallel links.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4; Eth-IPv6-ICMPv6 for L2 switching of IPv6 use. Both apply to all links.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge-domain (L2BD) switching combined with MAC learning enabled and Split Horizon Groups (SHG).  

 - **[Ver] TG verification:** Test ICMPv4 (or ICMPv6) Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 (IPv6) src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+--------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                           | Documentation                                                                                                                                                                                                                                                                                                                                                                     | Status |
+================================================================================+===================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 with L2BD (MAC learn) and SHG switch between four TG links | [Top] TG=DUT1=DUT2=TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 and  DUT2 configure four i/fs into L2BD with MAC learning and the same SHG on i/fs towards TG.  |br| [Ver] Make TG verify ICMPv4 Echo Req pkts are switched thru DUT1 and DUT2 in both directions and are correct on receive; verify no pkts are switched thru SHG isolated interfaces.  |br| [Ref]       | PASS   |
+--------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


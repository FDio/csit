
.. |br| raw:: html

    <br />

Tap Interface
-------------

api-crud-tap-func
'''''''''''''''''

**Tap Interface CRUD Tests**  

 - **[Top] Network Topologies:** TG=DUT1 2-node topology with two links between nodes.  

 - **[Enc] Packet Encapsulations:** No packet sent.  

 - **[Cfg] DUT configuration:** Add/Modify/Delete linux-TAP on DUT1.  

 - **[Ver] Verification:** Check dump of tap interfaces for correctness.  

 - **[Ref] Applicable standard specifications:**

+---------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                  | Documentation                                                                                                                                                                                    | Status |
+=======================================+==================================================================================================================================================================================================+========+
| TC01: Tap Interface Modify And Delete | [Top] TG-DUT1-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] Set two TAP interfaces.  |br| [Ver] Verify that TAP interface can be modified, deleted, and no other TAP interface is affected.       | PASS   |
+---------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-eth-l2bdbasemaclrn-eth-2tap-func
''''''''''''''''''''''''''''''''''''''

**Tap Interface Traffic Tests**  

 - **[Top] Network Topologies:** TG=DUT1 2-node topology with two links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG) are set depending on test case; Namespaces (NM) are set on DUT1 with attached linux-TAP.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent by TG on link to DUT1; On receipt TG verifies packets for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                          | Documentation                                                                                                                                                                                                                                                                                                                                              | Status |
+===============================+============================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: Tap Interface Simple BD | [Top] TG-DUT1-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure two L2BD with two if's for each L2BD with MAC learning and one L2BD joining two linux-TAP interfaces created by VPP located in namespace.  |br| [Ver] Packet sent from TG is passed through all L2BD and received back on TG. Then src_ip, dst_ip and MAC are checked.        | PASS   |
+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-eth-l2bdbasemaclrn-l2shg-eth-2tap-func
''''''''''''''''''''''''''''''''''''''''''''

**Tap Interface Traffic Tests**  

 - **[Top] Network Topologies:** TG=DUT1 2-node topology with two links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG) are set depending on test case; Namespaces (NM) are set on DUT1 with attached linux-TAP.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent by TG on link to DUT1; On receipt TG verifies packets for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                             | Documentation                                                                                                                                                                                                                                                                                                                                                                                                    | Status |
+==================================================+==================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: Tap Interface BD - Different Split Horizon | [Top] TG-DUT1-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure one if into L2BD with MAC learning. Add two TAP interfaces into this L2BD and assign them different SHG. Setup two namespaces and assign two linux-TAP interfaces to it respectively.  |br| [Ver] Packet is sent from TG to both linux-TAP interfaces and reply is checked. Ping from First linux-TAP to another should pass.       | PASS   |
+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: Tap Interface BD - Same Split Horizon      | [Top] TG-DUT1-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure one if into L2BD with MAC learning. Add two TAP interfaces into this L2BD and assign them same SHG. Setup two namespaces and assign two linux-TAP interfaces to it respectively.  |br| [Ver] Packet is sent from TG to both linux-TAP interfaces and reply is checked. Ping from First linux-TAP to another should fail.            | PASS   |
+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-ip4base-eth-1tap-func
''''''''''''''''''''''''''''''''''

**Tap Interface Traffic Tests**  

 - **[Top] Network Topologies:** TG=DUT1 2-node topology with two links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4 for L2 switching of IPv4.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge-domain (L2BD) MAC learning enabled; Split Horizon Groups (SHG) are set depending on test case; Namespaces (NM) are set on DUT1 with attached linux-TAP.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent by TG on link to DUT1; On receipt TG verifies packets for correctness and their IPv4 src-addr, dst-addr, and MAC addresses.  

 - **[Ref] Applicable standard specifications:**

+-----------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                          | Documentation                                                                                                                                                                                                                                                                                             | Status |
+===============================================+===========================================================================================================================================================================================================================================================================================================+========+
| TC01: Tap Interface IP Ping Without Namespace | [Top] TG-DUT1-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure two interface addresses with IPv4 of which one is TAP interface ( dut_to_tg_if and TAP ). and one is linux-TAP.  |br| [Ver] Packet sent from TG gets to the destination and ICMP-reply is received on TG.                    | PASS   |
+-----------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: Tap Interface IP Ping With Namespace    | [Top] TG-DUT1-TG.  |br| [Enc] Eth-IPv4-ICMPv4.  |br| [Cfg] On DUT1 configure two interface addresses with IPv4 of which one is TAP interface ( dut_to_tg_if and TAP ). and one is linux-TAP in namespace.  |br| [Ver] Packet sent from TG gets to the destination and ICMP-reply is received on TG.       | PASS   |
+-----------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


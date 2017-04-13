
.. |br| raw:: html

    <br />

LISP Overlay Tunnels
--------------------

api-crud-lisp-func
''''''''''''''''''

**API test cases**   

 - **[Top] Network Topologies:** DUT1 1-node topology.  

 - **[Enc] Packet Encapsulations:** None.  

 - **[Cfg] DUT configuration:** DUT1 gets configured with all LISP parameters.  

 - **[Ver] Verification:** DUT1 operational data gets verified following configuration.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+--------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                   | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                    | Status |
+========================================================+==================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT can enable and disable LISP                  | [Top] DUT1.  |br| [Enc] None.  |br| [Cfg1] Test LISP enable/disable API; On  DUT1 enable LISP.  |br| [Ver1] Check DUT1 if LISP is enabled.  |br| [Cfg2] Then disable LISP.  |br| [Ver2] Check DUT1 if LISP is disabled.  |br| [Ref] RFC6830.                                                                                                                                                                                                     | PASS   |
+--------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT can add and delete locator_set               | [Top] DUT1.  |br| [Enc] None.  |br| [Cfg1] Test LISP locator_set API; on  DUT1 configure locator_set and locator.  |br| [Ver1] Check DUT1 configured locator_set and locator are correct.  |br| [Cfg2] Then remove locator_set and locator.  |br| [Ver2] check DUT1 locator_set and locator are removed.  |br| [Ref] RFC6830.                                                                                                                    | PASS   |
+--------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT can add, reset and delete locator_set        | [Top] DUT1.  |br| [Enc] None.  |br| [Cfg1] Test LISP locator_set API; on  DUT1 configure locator_set and locator.  |br| [Ver1] Check DUT1 locator_set and locator are correct.  |br| [Cfg2] Then reset locator_set and set it again.  |br| [Ver2] Check DUT1 locator_set and locator are correct.  |br| [Cfg3] Then remove locator_set and locator.  |br| [Ver3] Check DUT1 all locator_set and locators are removed.  |br| [Ref] RFC6830.       | PASS   |
+--------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT can add and delete eid address               | [Top] DUT1.  |br| [Enc] None.  |br| [Cfg1] Test LISP eid API; on DUT1  configure LISP eid IP address.  |br| [Ver1] Check DUT1 configured data is correct.  |br| [Cfg2] Remove configured data.  |br| [Ver2] Check DUT1 all eid IP addresses are removed.  |br| [Ref] RFC6830.                                                                                                                                                                    | PASS   |
+--------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: DUT can add and delete LISP map resolver address | [Top] DUT1.  |br| [Enc] None.  |br| [Cfg1] Test LISP map resolver address  API; on DUT1 configure LISP map resolver address.  |br| [Ver1] Check DUT1 configured data is correct.  |br| [Cfg2] Remove configured data.  |br| [Ver2] Check DUT1 all map resolver addresses are removed.  |br| [Ref] RFC6830.                                                                                                                                       | PASS   |
+--------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4ipsectptlispgpe-ip4base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

**IPv4-ip4-ipsec-lispgpe-ip4 - main fib, vrf (gpe_vni-to-vrf)**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** ICMPv4-IPv4-IPSec-LISPGPE-IPv4-ICMPv4.  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 via VM to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                   | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+========================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 over Vhost to LISP GPE tunnel using IPsec (transport) on RLOC Int.      | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMP on DUT1-DUT2, Eth-IPv4-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS. Create Qemu vm on DUT1 and configure bridge between two vhosts.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip4 - main fib, virt2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv4 over Vhost to LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip4 - main fib, virt2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.                                                                    | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4ipsectptlispgpe-ip4base-func
''''''''''''''''''''''''''''''''''''''''

**IPv4-ip4-ipsec-lispgpe-ip4 - main fib, vrf (gpe_vni-to-vrf)**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** ICMPv4-IPv4-IPSec-LISPGPE-IPv4-ICMPv4.  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                                               | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Status |
+====================================================================================================================================+==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int.                           | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTs.  |br| [Ver] Case: ip4-lispgpe-ipsec-ip4 - main fib Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.             | PASS   |
+------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) lisp_gpe0 Int.                         | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTs.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip4 - main fib Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.             | PASS   |
+------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int and VRF on EID is enabled. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTs.  |br| [Ver] Case: ip4-lispgpe-ipsec-ip4 - vrf, main fib Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int and VRF is enabled.   | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTs.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip4 - vrf, main fib Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4ipsectptlispgpe-ip6base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip4-ipsec-lispgpe-ip6 - main fib, vrf, virt2lisp, phy2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISPGPE-IPSec-IPv6-ICMP, Eth-IPv4-IPSec-LISPGPE-IPv6-ICMP  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 via VM to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                   | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+========================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 over Vhost to LISP GPE tunnel using IPsec (transport) on RLOC Int.      | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPSec-IPv6-ICMP on DUT1-DUT2, Eth-IPv6-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS. Create Qemu vm on DUT1 and configure bridge between two vhosts.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip6 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv6 over Vhost to LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6, on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip6 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.                                                                   | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4ipsectptlispgpe-ip6base-func
''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip4-ipsec-lispgpe-ip6 - main fib, vrf, virt2lisp, phy2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISPGPE-IPSec-IPv6-ICMP, Eth-IPv4-IPSec-LISPGPE-IPv6-ICMP  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                          | Documentation                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+===============================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int.      | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPSec-IPv6-ICMP on DUT1-DUT2, Eth-IPv6-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.          | PASS   |
+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4ipsectptlispgpe-ip6basevrf-func
'''''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip4-ipsec-lispgpe-ip6 - main fib, vrf, virt2lisp, phy2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISPGPE-IPSec-IPv6-ICMP, Eth-IPv4-IPSec-LISPGPE-IPv6-ICMP  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                             | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Status |
+==================================================================================================================+===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6, on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip4-ipsec-lispgpe-ip6 - vrf, phy2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lisp-ip4base-func
'''''''''''''''''''''''''''''

**IP AFI independent functional tests.**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+---------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                      | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Status |
+===========================================================================+====================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 over LISPoIPv4 tunnel after disable-enable | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg1] On DUT1 and DUT2 configure IPv4 LISP static adjacencies.  |br| [Ver1] Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Cfg2] Disable LISP.  |br| [Ver2] Verify packets are not received via LISP tunnel.  |br| [Cfg3] Re-enable LISP.  |br| [Ver3] Verify packets are received again via LISP tunnel.  |br| [Ref] RFC6830.       | PASS   |
+---------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lisp-l2bdbasemaclrn-func
''''''''''''''''''''''''''''''''''''

**ip4-lispgpe-ip4 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-ICMPv4-LISPGpe-IP4  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+----------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                           | Documentation                                                                                                                                                                                                                                                                                                                                                                           | Status |
+================================================================+=========================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: Route IPv4 packet through LISP with Bridge Domain setup. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-ICMPv4-LISPGpe-IP4  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2. Also configure BD and assign it to LISP VNI.  |br| [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP tunnel between them; verify IPv4, Ether headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+----------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip4base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''

**ip4-lispgpe-ip4 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+--------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                       | Documentation                                                                                                                                                                                                                                                                                                                                                                                             | Status |
+============================================================================================+===========================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using vhost interfaces | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip4-lispgpe-ip4 - main fib, virt2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.        | PASS   |
+--------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip4base-func
''''''''''''''''''''''''''''''''

**ip4-lispgpe-ip4 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+-----------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                          | Documentation                                                                                                                                                                                                                                                                                                                                                                                                       | Status |
+===============================================================================================+=====================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip4-lispgpe-ip4 - phy2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+-----------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip4basevrf-eth-2vhost-1vm-func
''''''''''''''''''''''''''''''''''''''''''''''''''

**ip4-lispgpe-ip4 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+---------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                          | Documentation                                                                                                                                                                                                                                                                                                                                                                                                             | Status |
+===============================================================================================================+===========================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using vhost interfaces and VRF is enabled | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip4-lispgpe-ip4 - vrf, virt2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+---------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip4basevrf-func
'''''''''''''''''''''''''''''''''''

**ip4-lispgpe-ip4 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                             | Documentation                                                                                                                                                                                                                                                                                                                                                                                                            | Status |
+==================================================================================================================+==========================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip4-lispgpe-ip4 - vrf, phy2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip6base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''

**LISP static adjacency test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+--------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                       | Documentation                                                                                                                                                                                                                                                                                                                                                                                             | Status |
+============================================================================================+===========================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using vhost interfaces | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip6-lispgpe-ip4 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.        | PASS   |
+--------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip6base-func
''''''''''''''''''''''''''''''''

**LISP static adjacency test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                 | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Status |
+======================================================================+======================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISPoIPv4 tunnel | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] On DUT1 and DUT2 configure IPv4 LISP static adjacencies.  |br| [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Cfg2] Reconf LISP.  |br| [Ver2] Verify packets are received again via LISP tunnel.  |br| [Ref] RFC6830.       | PASS   |
+----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4lispgpe-ip6basevrf-func
'''''''''''''''''''''''''''''''''''

**LISP static adjacency test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv4 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv4 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                             | Documentation                                                                                                                                                                                                                                                                                                                                                                                                            | Status |
+==================================================================================================================+==========================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv4-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv4 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip6-lispgpe-ip4 - vrf, phy2lisp Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6ipsectptlispgpe-ip4base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip4-ipsec-lispgpe-ip6 - main fib, virt2lisp, phy2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISPGPE-IPSec-IPv4-ICMP, Eth-IPv6-IPSec-LISPGPE-IPv4-ICMP  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Test cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                   | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+========================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 over Vhost to LISP GPE tunnel using IPsec (transport) on RLOC Int.      | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISPGPE-IPSec-IPv4-ICMP on DUT1-DUT2, Eth-IPv4-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS. Create Qemu vm on DUT1 and configure bridge between two vhosts.  |br| [Ver] Case: ip6-ipsec-lispgpe-ip4 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv4 over Vhost to LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6, on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip6-ipsec-lispgpe-ip4 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.                                                                   | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6ipsectptlispgpe-ip4base-func
''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip4-ipsec-lispgpe-ip6 - main fib, virt2lisp, phy2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISPGPE-IPSec-IPv4-ICMP, Eth-IPv6-IPSec-LISPGPE-IPv4-ICMP  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                          | Documentation                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+===============================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int.      | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISPGPE-IPSec-IPv4-ICMP on DUT1-DUT2, Eth-IPv4-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.          | PASS   |
+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv4 bidirectionally over LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-IPSec-LISPGPE-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6ipsectptlispgpe-ip6base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip6-ipsec-lispgpe-ip6 - main fib, vrf (gpe_vni-to-vrf), phy2lisp, virt2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6,  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 via VM to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                   | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+========================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 over Vhost to LISP GPE tunnel using IPsec (transport) on RLOC Int.      | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMP on DUT1-DUT2, Eth-IPv6-ICMP on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS. Create Qemu vm on DUT1 and configure bridge between two vhosts.  |br| [Ver] Case: ip6-ipsec-lispgpe-ip6 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv6 over Vhost to LISP GPE tunnel using IPsec (transport) on lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip6-ipsec-lispgpe-ip6 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.                                                                    | PASS   |
+--------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6ipsectptlispgpe-ip6base-func
''''''''''''''''''''''''''''''''''''''''

**IPv6 - ip6-ipsec-lispgpe-ip6 - main fib, vrf (gpe_vni-to-vrf), phy2lisp, virt2lisp**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6,  

 - **[Cfg] DUT configuration:** Each DUT is configured with LISP and IPsec. IPsec is in transport mode. Tests cases are for IPsec configured both on RLOC interface or lisp_gpe0 interface.  

 - **[Ver] TG verification:** Packet is send from TG(if1) across the DUT1 to DUT2 where it is forwarded to TG(if2).  

 - **[Ref] Applicable standard specifications:** RFC6830, RFC4303.

+------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                       | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Status |
+============================================================================================================+================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using IPsec (transport) on RLOC Int.   | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip6-lispgpe-ipsec-ip6 - main fib, phys2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using IPsec (transport) lisp_gpe0 Int. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-IPSec-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2 with IPsec in between DUTS.  |br| [Ver] Case: ip6-ipsec-lispgpe-ip6 - main fib, phys2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830, RFC4303.        | PASS   |
+------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6lisp-l2bdbasemaclrn-func
''''''''''''''''''''''''''''''''''''

**l2-lispgpe-ip6 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IP6-ICMPv6-LISPGpe-IP6  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with L2 bridge domains and neighbors. LISPoIPv6 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+----------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                           | Documentation                                                                                                                                                                                                                                                                                                                                                                          | Status |
+================================================================+========================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: Route IPv6 packet through LISP with Bridge Domain setup. | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IP6-ICMPv6-LISPGpe-IP6  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2. Also configure BD and assign it to LISP VNI.  |br| [Ver] Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP tunnel between them; verify IPv6, Ether headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+----------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6lispgpe-ip4base-func
''''''''''''''''''''''''''''''''

**LISP static adjacency test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn for IPv4 routing over LISPoIPv6 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv4 routing and static routes. LISPoIPv6 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv4 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                 | Documentation                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Status |
+======================================================================+======================================================================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv4 bidirectionally over LISPoIPv6 tunnel | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISP-IPv4-ICMPv4 on DUT1-DUT2, Eth-IPv4-ICMPv4 on TG-DUTn.  |br| [Cfg] On DUT1 and DUT2 configure IPv6 LISP static adjacencies.  |br| [Ver] Make TG send ICMPv4 Echo Req between its interfaces across both DUTs and LISP tunnel between them; verify IPv4 headers on received packets are correct.  |br| [Cfg2] Reconf LISP.  |br| [Ver2] Verify packets are received again via LISP tunnel.  |br| [Ref] RFC6830.       | PASS   |
+----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6lispgpe-ip6base-eth-2vhost-1vm-func
'''''''''''''''''''''''''''''''''''''''''''''''

**ip6-lispgpe-ip6 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv6 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv6 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+--------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                       | Documentation                                                                                                                                                                                                                                                                                                                                                                                                   | Status |
+============================================================================================+=================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using vhost interfaces | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip6-ipsec-lispgpe-ip6 - main fib, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.        | PASS   |
+--------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6lispgpe-ip6base-func
''''''''''''''''''''''''''''''''

**ip6-lispgpe-ip6 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv6 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv6 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+-----------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                          | Documentation                                                                                                                                                                                                                                                                                                                                                                                                       | Status |
+===============================================================================================+=====================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using physical interfaces | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip6-lispgpe-ip6 - phy2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+-----------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6lispgpe-ip6basevrf-eth-2vhost-1vm-func
''''''''''''''''''''''''''''''''''''''''''''''''''

**ip6-lispgpe-ip6 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv6 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv6 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                          | Documentation                                                                                                                                                                                                                                                                                                                                                                                                              | Status |
+===============================================================================================================+============================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using vhost interfaces and VRF is enabled | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip6-lispgpe-ip6 - vrf, virt2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830.         | PASS   |
+---------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6lispgpe-ip6basevrf-func
'''''''''''''''''''''''''''''''''''

**ip6-lispgpe-ip6 encapsulation test cases**   

 - **[Top] Network Topologies:** TG-DUT1-DUT2-TG 3-node circular topology with single links between nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv6-LISP-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn for IPv6 routing over LISPoIPv6 tunnel.  

 - **[Cfg] DUT configuration:** DUT1 and DUT2 are configured with IPv6 routing and static routes. LISPoIPv6 tunnel is configured between DUT1 and DUT2.  

 - **[Ver] TG verification:** Test ICMPv6 Echo Request packets are sent in both directions by TG on links to DUT1 and DUT2; on receive TG verifies packets for correctness and their IPv6 src-addr, dst-addr and MAC addresses.  

 - **[Ref] Applicable standard specifications:** RFC6830.

+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                                             | Documentation                                                                                                                                                                                                                                                                                                                                                                                                            | Status |
+==================================================================================================================+==========================================================================================================================================================================================================================================================================================================================================================================================================================+========+
| TC01: DUT1 and DUT2 route IPv6 bidirectionally over LISP GPE tunnel using physical interfaces and VRF is enabled | [Top] TG-DUT1-DUT2-TG.  |br| [Enc] Eth-IPv6-LISPGPE-IPv6-ICMPv6 on DUT1-DUT2, Eth-IPv6-ICMPv6 on TG-DUTn.  |br| [Cfg] Configure IPv6 LISP static adjacencies on DUT1 and DUT2.  |br| [Ver] Case: ip6-lispgpe-ip6 - vrf, phy2lisp Make TG send ICMPv6 Echo Req between its interfaces across both DUTs and LISP GPE tunnel between them; verify IPv6 headers on received packets are correct.  |br| [Ref] RFC6830.        | PASS   |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


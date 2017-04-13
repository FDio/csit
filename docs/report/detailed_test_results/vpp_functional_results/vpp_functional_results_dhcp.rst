
.. |br| raw:: html

    <br />

DHCP - Client and Proxy
-----------------------

eth2p-ethip4-ip4base-ip4dhcpclient-func
'''''''''''''''''''''''''''''''''''''''

**DHCPv4 Client related test cases**

+------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                       | Documentation                                                                                                                                                        | Status |
+============================================================+======================================================================================================================================================================+========+
| VPP sends a DHCP DISCOVER                                  | Configure DHCPv4 client on interface to TG without hostname and check if DHCPv4 DISCOVER message contains all required fields with expected values.                  | PASS   |
+------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| VPP sends a DHCPv4 DISCOVER with hostname                  | Configure DHCPv4 client on interface to TG with hostname and check if DHCPv4 DISCOVER message contains all required fields with expected values.                     | PASS   |
+------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| VPP sends DHCPv4 REQUEST after OFFER                       | Configure DHCPv4 client on interface to TG and check if DHCPv4 REQUEST message contains all required fields.                                                         | PASS   |
+------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| VPP doesn't send DHCPv4 REQUEST after OFFER with wrong XID | Configure DHCPv4 client on interface to TG. If server sends DHCPv4 OFFER with different XID as in DHCPv4 DISCOVER, DHCPv4 REQUEST message shouldn't be sent.         | FAIL   |
+------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| VPP honors DHCPv4 lease time                               | Send IP configuration to the VPP client via DHCPv4. Address is checked with ICMP echo request and there should be no reply for echo request when lease has expired.  | PASS   |
+------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-ip4base-ip4dhcpproxy-func
''''''''''''''''''''''''''''''''''''''

**DHCPv4 proxy test cases**   

 - **[Top] Network Topologies:** TG = DUT with two links between the nodes.  

 - **[Enc] Packet Encapsulations:** Eth-IPv4-UDP-BOOTP-DHCP  

 - **[Cfg] DUT configuration:** DUT is configured with DHCPv4 proxy.  

 - **[Ver] TG verification:** Test DHCPv4 packets are sent on TG on first link to DUT and received on TG on second link. On receive TG verifies if DHCPv4 packets are valid.

+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                    | Documentation                                                                                                                                                                                           | Status |
+=========================================================+=========================================================================================================================================================================================================+========+
| TC01: VPP proxies valid DHCPv4 request to DHCPv4 server | [Top] TG=DUT   |br| [Enc] Eth-IPv4-UDP-BOOTP-DHCP  |br| [Cfg] On DUT setup DHCPv4 proxy.  |br| [Ver] Make TG verify matching DHCPv4 packets between client and DHCPv4 server through DHCP proxy.        | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: VPP proxy ignores invalid DHCPv4 request          | [Top] TG=DUT   |br| [Enc] Eth-IPv4-UDP-BOOTP-DHCP  |br| [Cfg] On DUT setup DHCPv4 proxy.  |br| [Ver] Make TG verify matching invalid DHCPv4 packets are dropped.                                        | PASS   |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6-ip6base-ip6dhcpproxy-func
''''''''''''''''''''''''''''''''''''''

**DHCPv6 proxy test cases**   

 - **[Top] Network Topologies:** TG = DUT with two links between the nodes.  

 - **[Cfg] DUT configuration:** DUT is configured with DHCPv6 proxy.  

 - **[Ver] TG verification:** Test DHCPv6 packets are sent on TG on first link to DUT and received on TG on second link. On receive TG verifies if DHCPv6 packets are valid  

 - **[Ref] Applicable standard specifications:** RFC 3315

+---------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                    | Documentation                                                                                                                                                                            | Status |
+=========================================================+==========================================================================================================================================================================================+========+
| TC01: VPP proxies valid DHCPv6 request to DHCPv6 server | [Top] TG=DUT  |br| [Cfg] On DUT setup DHCP proxy.  |br| [Ver] Make TG verify matching DHCPv6 packets between client and  DHCPv6 server through DHCPv6 proxy.  |br| [Ref] RFC 3315        | PASS   |
+---------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


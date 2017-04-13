
.. |br| raw:: html

    <br />

iACL Security
-------------

eth2p-eth-l2xcbase-iaclbase-func
''''''''''''''''''''''''''''''''

**Ingress ACL test cases**   

 - **[Top] Network Topologies:** TG - DUT1 - DUT2 - TG with one link between the nodes.  

 - **[Cfg] DUT configuration:** DUT2 is configured with L2 Cross connect. DUT1 is configured with iACL classification on link to TG,  

 - **[Ver] TG verification:** Test ICMPv4 Echo Request packets are sent in one direction by TG on link to DUT1 and received on TG link to DUT2. On receive TG verifies if packets are dropped.

+-------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                              | Documentation                                                                                                                                                                   | Status |
+===================================================================+=================================================================================================================================================================================+========+
| TC01: DUT with iACL MAC src-addr drops matching pkts              | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 add source MAC address to classify table with 'deny'.  |br| [Ver] Make TG verify matching packets are dropped.                       | PASS   |
+-------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with iACL MAC dst-addr drops matching pkts              | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 add destination MAC address to classify table with 'deny'.  |br| [Ver] Make TG verify matching packets are dropped.                  | PASS   |
+-------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT with iACL MAC src-addr and dst-addr drops matching pkts | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 add source and destination MAC address to classify table with 'deny'.  |br| [Ver] Make TG verify matching packets are dropped.       | PASS   |
+-------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT with iACL EtherType drops matching pkts                 | [Top] TG-DUT1-DUT2-TG.  |br| [Cfg] On DUT1 add EtherType IPv4(0x0800) to classify table with 'deny'.  |br| [Ver] Make TG verify matching packets are dropped.                   | PASS   |
+-------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip4-ip4base-iaclbase-func
''''''''''''''''''''''''''''''''''

**IPv4 routing with ingress ACL test cases**  Encapsulations: Eth-IPv4 on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv4 ingress ACL (iACL) tests use 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured with IPv4 routing and static routes. DUT1 is configured with iACL on link to TG, iACL classification and permit/deny action are configured on a per test case basis. Test ICMPv4 Echo Request packets are sent in one direction by TG on link to DUT1 and received on TG link to DUT2. On receive TG verifies if packets are dropped, or if received verifies packet IPv4 src-addr, dst-addr and MAC addresses.

+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                     | Documentation                                                                                                                 | Status |
+==========================================================================+===============================================================================================================================+========+
| TC01: DUT with iACL IPv4 src-addr drops matching pkts                    | On DUT1 add source IPv4 address to classify table with 'deny'. Make TG verify matching packets are dropped.                   | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with iACL IPv4 dst-addr drops matching pkts                    | On DUT1 add destination IPv4 address to classify table with 'deny'. Make TG verify matching packets are dropped.              | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT with iACL IPv4 src-addr and dst-addr drops matching pkts       | On DUT1 add source and destination IPv4 addresses to classify table with 'deny'. Make TG verify matching packets are dropped. | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT with iACL IPv4 protocol set to TCP drops matching pkts         | On DUT1 add protocol mask and TCP protocol (0x06) to classify table with 'deny'. Make TG verify matching packets are dropped. | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: DUT with iACL IPv4 protocol set to UDP drops matching pkts         | On DUT1 add protocol mask and UDP protocol (0x11) to classify table with 'deny'. Make TG verify matching packets are dropped. | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: DUT with iACL IPv4 TCP src-ports drops matching pkts               | On DUT1 add TCP source ports to classify table with 'deny'. Make TG verify matching packets are dropped.                      | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: DUT with iACL IPv4 TCP dst-ports drops matching pkts               | On DUT1 add TCP destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.                 | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC08: DUT with iACL IPv4 TCP src-ports and dst-ports drops matching pkts | On DUT1 add TCP source and destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.      | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC09: DUT with iACL IPv4 UDP src-ports drops matching pkts               | On DUT1 add UDP source ports to classify table with 'deny'. Make TG verify matching packets are dropped.                      | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC10: DUT with iACL IPv4 UDP dst-ports drops matching pkts               | On DUT1 add TCP destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.                 | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+
| TC11: DUT with iACL IPv4 UDP src-ports and dst-ports drops matching pkts | On DUT1 add UDP source and destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.      | PASS   |
+--------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6-ip6base-iaclbase-func
''''''''''''''''''''''''''''''''''

**IPv6 routing with ingress ACL test cases**  Encapsulations: Eth-IPv6 on links TG-DUT1, TG-DUT2, DUT1-DUT2. IPv6 ingress ACL (iACL) tests use 3-node topology TG - DUT1 - DUT2 - TG with one link between the nodes. DUT1 and DUT2 are configured with IPv6 routing and static routes. DUT1 is configured with iACL on link to TG, iACL classification and permit/deny action are configured on a per test case basis. Test ICMPv6 Echo Request packets are sent in one direction by TG on link to DUT1 and received on TG link to DUT2. On receive TG verifies if packets are dropped, or if received verifies packet IPv6 src-addr, dst-addr and MAC addresses.

+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                                                           | Documentation                                                                                                                                                                    | Status |
+================================================================================================+==================================================================================================================================================================================+========+
| TC01: DUT with iACL IPv6 src-addr drops matching pkts                                          | On DUT1 add source IPv6 address to classify table with 'deny'. Make TG verify matching packets are dropped.                                                                      | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: DUT with iACL IPv6 dst-addr drops matching pkts                                          | On DUT1 add destination IPv6 address to classify table with 'deny'. Make TG verify matching packets are dropped.                                                                 | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: DUT with iACL IPv6 src-addr and dst-addr drops matching pkts                             | On DUT1 add source and destination IPv6 addresses to classify table with 'deny'. Make TG verify matching packets are dropped.                                                    | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: DUT with iACL IPv6 protocol set to TCP drops matching pkts                               | On DUT1 add protocol mask and TCP protocol (0x06) to classify table with 'deny'. Make TG verify matching packets are dropped.                                                    | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC05: DUT with iACL IPv6 protocol set to UDP drops matching pkts                               | On DUT1 add protocol mask and UDP protocol (0x11) to classify table with 'deny'. Make TG verify matching packets are dropped.                                                    | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC06: DUT with iACL IPv6 TCP src-ports drops matching pkts                                     | On DUT1 add TCP source ports to classify table with 'deny'. Make TG verify matching packets are dropped.                                                                         | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC07: DUT with iACL IPv6 TCP dst-ports drops matching pkts                                     | On DUT1 add TCP destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.                                                                    | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC08: DUT with iACL IPv6 TCP src-ports and dst-ports drops matching pkts                       | On DUT1 add TCP source and destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.                                                         | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC09: DUT with iACL IPv6 UDP src-ports drops matching pkts                                     | On DUT1 add UDP source ports to classify table with 'deny'. Make TG verify matching packets are dropped.                                                                         | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC10: DUT with iACL IPv6 UDP dst-ports drops matching pkts                                     | On DUT1 add TCP destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.                                                                    | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC11: DUT with iACL IPv6 UDP src-ports and dst-ports drops matching pkts                       | On DUT1 add UDP source and destination ports to classify table with 'deny'. Make TG verify matching packets are dropped.                                                         | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC12: DUT with iACL MAC src-addr and iACL IPv6 UDP src-ports and dst-ports drops matching pkts | On DUT1 add source MAC address to classify (L2) table and add UDP source and destination ports to classify (hex) table with 'deny'. Make TG verify matching packets are dropped. | PASS   |
+------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


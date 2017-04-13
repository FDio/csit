
.. |br| raw:: html

    <br />

RPF Source Security
-------------------

eth2p-ethip4-ip4base-rpf-func
'''''''''''''''''''''''''''''

**Source RPF check on IPv4 test cases**   

 - **[Top] Network Topologies:** TG - DUT1 - DUT2 - TG with one link between the nodes.  

 - **[Cfg] DUT configuration:** DUT2 is configured with L2 Cross connect. DUT1 is configured with IP source check on link to TG,  

 - **[Ver] TG verification:** Test ICMP Echo Request packets are sent in one direction by TG on link to DUT1 and received on TG link to DUT2. On receive TG verifies if packets which source address is not in routes are dropped.

+-----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                                | Documentation                                                                                                                                                         | Status |
+=====================================================+=======================================================================================================================================================================+========+
| TC01: VPP source RPF check on IPv4 src-addr         | [Top] TG-DUT1-DUT2-TG  |br| [Cfg] On DUT1 setup IP source check.  |br| [Ver] Make TG verify matching packets which source address is not in routes are dropped.       | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: VPP pass traffic on non-enabled RPF interface | [Top] TG-DUT1-DUT2-TG  |br| [Cfg] On DUT1 setup IP source check.  |br| [Ver] Make TG verify matching packets on non-enabled RPF interface are passed.                 | PASS   |
+-----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


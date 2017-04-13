
.. |br| raw:: html

    <br />

QoS Policer Metering
--------------------

eth2p-ethip4-ip4base-ipolicemarkbase-func
'''''''''''''''''''''''''''''''''''''''''

**IPv4 policer test cases**   

 - **[Top] Network topologies:** TG=DUT1 2-node topology with two links between nodes.  

 - **[Cfg] DUT configuration:** On DUT1 configure interfaces IPv4 adresses, and static ARP record on the second interface.  

 - **[Ver] TG verification:** Test packet is sent from TG on the first link to DUT1. Packet is received on TG on the second link from DUT1.  

 - **[Ref] Applicable standard specifications:** RFC2474, RFC2697, RFC2698.

+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                            | Documentation                                                                                                                                                                                                                                                                                                                      | Status |
+=================================================+====================================================================================================================================================================================================================================================================================================================================+========+
| TC01: VPP policer 2R3C Color-aware marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2698.  |br| [Cfg] On DUT1 configure 2R3C color-aware policer on the first interface.  |br| [Ver] TG sends IPv4 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv4 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: VPP policer 2R3C Color-blind marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2698.  |br| [Cfg] On DUT1 configure 2R3C color-blind policer on the first interface.  |br| [Ver] TG sends IPv4 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv4 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: VPP policer 1R3C Color-aware marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2697.  |br| [Cfg] On DUT1 configure 1R3C color-aware policer on the first interface.  |br| [Ver] TG sends IPv4 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv4 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: VPP policer 1R3C Color-blind marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2697.  |br| [Cfg] On DUT1 configure 1R3C color-blind policer on the first interface.  |br| [Ver] TG sends IPv4 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv4 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+

eth2p-ethip6-ip6base-ipolicemarkbase-func
'''''''''''''''''''''''''''''''''''''''''

**IPv6 policer test cases**   

 - **[Top] Network topologies:** TG=DUT1 2-node topology with two links between nodes.  

 - **[Cfg] DUT configuration:** On DUT1 configure interfaces IPv6 adresses, and static neighbor record on the second interface.  

 - **[Ver] TG verification:** Test packet is sent from TG on the first link to DUT1. Packet is received on TG on the second link from DUT1.  

 - **[Ref] Applicable standard specifications:** RFC2474, RFC2697, RFC2698.

+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| Name                                            | Documentation                                                                                                                                                                                                                                                                                                                      | Status |
+=================================================+====================================================================================================================================================================================================================================================================================================================================+========+
| TC01: VPP policer 2R3C Color-aware marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2698.  |br| [Cfg] On DUT1 configure 2R3C color-aware policer on the first interface.  |br| [Ver] TG sends IPv6 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv6 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC02: VPP policer 2R3C Color-blind marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2698.  |br| [Cfg] On DUT1 configure 2R3C color-blind policer on the first interface.  |br| [Ver] TG sends IPv6 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv6 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC03: VPP policer 1R3C Color-aware marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2697.  |br| [Cfg] On DUT1 configure 1R3C color-aware policer on the first interface.  |br| [Ver] TG sends IPv6 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv6 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+
| TC04: VPP policer 1R3C Color-blind marks packet | [Top] TG=DUT1.  |br| [Ref] RFC2474, RFC2697.  |br| [Cfg] On DUT1 configure 1R3C color-blind policer on the first interface.  |br| [Ver] TG sends IPv6 TCP packet on the first link to DUT1. On DUT1 packet is marked with DSCP tag. Verify if DUT1 sends correct IPv6 TCP packet with correct DSCP on the second link to TG.       | PASS   |
+-------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+


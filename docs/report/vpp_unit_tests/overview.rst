Overview
========

.. note::

    This section includes an abbreviated version of the VPP Test Framework
    overview maintained within the VPP project. Complete overview can be found
    in `VPP test framework documentation`_.

VPP Unit Test Framework
-----------------------

VPP Test Framework is used to ease writing, running and debugging unit tests
for the VPP. It is based on python as a high level language to  allow rapid
test development. scapy\_ is used as a tool for creating and dissecting
packets.

VPP Test Framework does not send any packets to VPP directly. Traffic is
instead injected using VPP packet-generator interfaces. Packets are written
into a temporary .pcap file, which is then read by the VPP code with packets
getting injected into the VPP processing nodes.

Similarly, VPP does not send any packets to VPP Test Framework directly.
Instead, VPP packet capture feature is used to capture and write packets to a
temporary .pcap file, which is then read and analyzed by the VPP Test
Framework.

For complete description of the VPP Test Framework including anatomy of a test
case and detailed documentation of existing VPP unit test cases please refer
to the `VPP test framework documentation`_

Unit Tests Coverage
-------------------

Following VPP functional test areas are covered in VPP unit test code included
in VPP rls1710 with results listed in this report:

- ARP - ARP, Proxy ARP.
- ACL plugin - stateful and stateless security-groups access-control-lists.
- BFD IPv4 - Bidirectional Forwarding Detection - baseline, APIs, authorization, authentication.
- BFD IPv6 - Bidirectional Forwarding Detection - baseline, APIs, authorization, authentication.
- Classifier - classification with IP ACL, MAC ACL, IP PBR.
- CRUD Loopback - create, read, update, delete Loopback interfaces.
- Deterministic NAT - Carrier Grade NAT tests.
- DHCP - DHCPv4 and DHCPv6 Proxy.
- FIB - baseline and scale tests.
- Flow-per-packet plugin - collect and report L2 and IP4 flow statistics.
- Flowprobe tests.
- GRE - GRE IPv4/IPv6 tunnel, L2, VRF tests.
- GTPU - baseline GTPU tests.
- IP Multicast - IPv4/IPv6 multicast replication, connected source check.
- IP4 VRF Multi-instance - create, read, update, delete and verify IPv4 VRFs.
- IP6 VRF Multi-instance - create, read, update, delete and verify IPv6 VRFs.
- IPv4 - baseline FIB tests.
- IPv4 FIB CRUD - add/update/delete IPv4 routes.
- IPv6 - baseline FIB operations, NS/RS exception handling.
- IRB - Integrated Routing and Bridging tests.
- L2 FIB CRUD - add/update/delete L2 MAC entries.
- L2BD - L2 Bridge-Domain baseline tests incl. single- and dual-loop.
- L2XC - L2 cross-connect baseline tests incl. single- and dual-loop.
- L2XC Multi-instance - L2 cross-connect multi-instance tests.
- LISP - basic LISP tests.
- Load Balancer - IP4 GRE4, IP4 GRE6, IP6 GRE4, IP6 GRE6.
- MACIP - ingress access control for IPv4, IPv6 with L2BDP and IP routing.
- MFIB Unit.
- MPLS - MPLS baseline tests.
- MPLS PIC edge convergence - prefix independent convergence tests for MPLS PE.
- NAT44 - NAT44 tests, IPFIX logging, VRF awareness.
- NAT64 - NAT64 static and dynamic translation tests.
- SPAN - Switched Port Analyzer packet mirroring.
- SRv6 - Segment Routing IPv6 tests.
- VTR Test Case - VLAN tag manipulation tests.
- VXLAN - baseline VXLAN tunneling.
- VXLAN-GPE - baseline VXLAN-GPE tunneling tests including multicast.

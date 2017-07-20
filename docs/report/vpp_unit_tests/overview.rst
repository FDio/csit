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
in VPP rls1704 with results listed in this report:

- CRUD Loopback - create, read, update, delete Loopback interfaces.
- Flow-per-packet plugin - collect and report L2 and IP4 flow statistics.
- DHCP - DHCPv4 and DHCPv6 Proxy.
- IP4 VRF Multi-instance - create, read, update, delete and verify IPv4 VRFs.
- Load Balancer - IP4 GRE4, IP4 GRE6, IP6 GRE4, IP6 GRE6.
- FIB Unit Tests.
- Bidirectional Forwarding Detection (BFD) IPv4 - baseline BFD session operation.
- Bidirectional Forwarding Detection (BFD) IPv6 - baseline BFD session operation.
- Bidirectional Forwarding Detection (BFD) - API tests.
- Bidirectional Forwarding Detection (BFD) - changing authorization.
- Bidirectional Forwarding Detection (BFD) - SHA1 authentication.
- IPv6 Tests - baseline FIB operations, NS/RS exception handling.
- SPAN Test - Switched Port Analyzer packet mirroring.
- GRE Tests - GRE tunnel tests.
- SNAT Test Cases - SNAT44 tests.
- Deterministic NAT Test Cases - Carrier Grade NAT tests.
- NAT64 Test Cases - NAT64 static and dynamic translation tests.
- L2XC Multi-instance - L2 cross-connect multi-instance tests.
- IPv4 Tests - baseline FIB tests.
- IPv4 FIB CRUD - add/update/delete IPv4 routes.
- IRB Tests - Integrated Routing and Bridging tests.
- ACL plugin - stateful and stateless security-groups access-control-lists.
- MPLS Tests - MPLS baseline tests.
- MPLS PIC edge convergence - prefix independent convergence tests for MPLS PE.
- L2XC Tests - L2 cross-connect baseline tests incl. single- and dual-loop.
- MFIB Unit Tests.
- IP Multicast Tests - IPv4/IPv6 multicast replication, connected source check.
- Classifier - classification with IP ACL, MAC ACL, IP PBR.
- VXLAN Tests - baseline VXLAN tunneling.
- VXLAN-GPE Test Cases - baseline VXLAN-GPE tunneling tests including multicast.
- VTR Test Case - VLAN tag manipulation tests.
- L2 FIB CRUD - add/update/delete L2 MAC entries.
- L2BD Tests - L2 Bridge-Domain baseline tests incl. single- and dual-loop.
- Flowprobe tests.
- GTPU Test Cases - baseline GTPU tests.

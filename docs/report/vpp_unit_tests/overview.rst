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

- ACL Security - stateful and stateless security-groups access-control-lists.
- APIs - VAPI, VOM, PAPI, JVPP.
- ARP - ARP, proxy ARP, static arp.
- BFD - API, Authentication, Authentication Change, CLI.
- BFD IPv4 - sessions operation.
- BFD IPv6 - sessions operation.
- BIER - Bit Indexed Explicit Replication.
- Classifier - classification with IP ACL, MAC ACL, IP PBR.
- Container Integration - IPv4, IPv6 local-spoof connectivity tests.
- CRUD Loopback - create, read, update, delete Loopback interfaces.
- DHCP - DHCPv4/v6 Client and Proxy.
- Distributed Virtual Router.
- DS-Lite Softwire - softwire termination.
- FIB - baseline and scale tests.
- Flowprobe.
- Geneve Tunnels.
- GRE Tunnels - GRE IPv4/IPv6 tunnel, L2, VRF tests.
- GTPU Tunnels - baseline GTPU tests.
- IP Multicast Routing - IPv4/IPv6 multicast replication, connected source check.
- IPSec - baseline IPSec sanity tests.
- IPv4 FIB CRUD - add/update/delete IPv4 routes.
- IPv4 Routing.
- IP4 VRF Multi-instance - create, read, update, delete and verify IPv4 VRFs.
- IPv6 Routing - baseline FIB operations, NS/RS exception handling.
- IP6 VRF Multi-instance - create, read, update, delete and verify IPv6 VRFs.
- IRB Integrated Routing-Bridging.
- Kube-proxy - data plane NAT tests.
- L2 FIB CRUD - add/update/delete L2 MAC entries.
- L2BD Multi-instance.
- L2BD Switching - L2 Bridge-Domain baseline tests incl. single- and dual-loop.
- L2XC Multi-instance - L2 cross-connect multi-instance tests.
- L2XC Switching - L2 cross-connect baseline tests incl. single- and dual-loop.
- LISP Tunnels - basic LISP tests.
- Load Balancer - IP4 GRE4, IP4 GRE6, IP6 GRE4, IP6 GRE6.
- MACIP Access Control - ingress access control for IPv4, IPv6 with L2BDP and IP routing.
- MAP Softwires - softwire termination.
- MFIB Multicast FIB.
- MPLS Switching - MPLS baseline, prefix independent convergence for MPLS PE.
- NAT44 - NAT44 tests, IPFIX logging, VRF awareness, deterministic CGNAT.
- NAT64 - NAT64 static and dynamic translation tests.
- P2P Ethernet Subinterface.
- PPPoE Encapsulation.
- SPAN Switch Port Analyzer - packet mirroring.
- SRv6 Routing - Segment Routing IPv6 tests.
- TCP/IP Stack - unit tests, builtin client/server transfers.
- UDP Stack - unit tests.
- VTR VLAN Tag Rewrites - VLAN tag rewrite tests.
- VXLAN Tunnels - baseline VXLAN tests including multicast.
- VXLAN-GPE Tunnels - baseline VXLAN-GPE tunneling including multicast.
- Other Tests - ping, session, template verification, timer tests.

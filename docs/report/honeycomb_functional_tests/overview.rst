Overview
========

Tested Virtual Topologies
-------------------------

CSIT Honeycomb functional tests are executed on virtualized topologies created
using :abbr:`VIRL (Virtual Internet Routing Lab)` simulation platform
contributed by Cisco. VIRL runs on physical baremetal servers hosted by LF FD.io
project. All tests are executed in two node logical test topology - Traffic
Generator (TG) node and Systems Under Test (SUT1) node connected in a loop.
Logical test topology is shown in the figure below.::

                     +------------------------+
                     |                        |
                     |  +------------------+  |
        +--------------->                  <--------------+
        |            |  |                  |  |           |
        |  |------------>       DUT1       <-----------+  |
        |  |         |  +------------------+  |        |  |
        |  |         |                        |        |  |
        |  |         |                  SUT1  |        |  |
        |  |         +------------------------+        |  |
        |  |                                           |  |
        |  |                                           |  |
        |  |               +-----------+               |  |
        |  +--------------->           <---------------+  |
        |                  |    TG     |                  |
        +------------------>           <------------------+
                           +-----------+

SUT1 is a VM (Ubuntu or Centos, depending on the test suite), TG is a Traffic
Generator (TG, another Ubuntu VM). SUTs run Honeycomb and VPP SW applications
in Linux user-mode as a Device Under Test (DUT) within the VM. TG runs Scapy
SW application as a packet Traffic Generator. Logical connectivity between
SUTs and to TG is provided using virtual NICs using VMs' virtio driver.

Virtual testbeds are created on-demand whenever a verification job is started
(e.g. triggered by the gerrit patch submission) and destroyed upon completion
of all functional tests. Each node is a Virtual Machine and each connection
that is drawn on the diagram is available for use in any test case. During the
test execution, all nodes are reachable thru the Management network connected
to every node via dedicated virtual NICs and virtual links (not shown above
for clarity).

Functional Tests Coverage
-------------------------

The following Honeycomb functional test areas are included in the CSIT-|release|
with results listed in this report:

- **Basic interface management** - CRUD for interface state,
  - ipv4/ipv6 address, ipv4 neighbor, MTU value.
  - Test case count: 14
- **L2BD** - CRUD for L2 Bridge-Domain, interface assignment.
  - Create up to two bridge domains with all implemented functions turned on.
  - (flooding, unknown-unicast flooding, forwarding, learning, arp-termination)
  - Assign up to two physical interfaces to a single bridge domain.
  - Remove interface assignments, remove bridge domains.
  - Test case count: 5
- **L2FIB** - CRD for L2-FIB entries.
  - Create 4 FIB entries
  - (one of each for filter/forward, static/dynamic combinations).
  - Remove FIB entries.
  - Test case count: 7
- **VxLAN** - CRD for VxLAN tunnels.
  - Create VxLAN interface.
  - Disable VxLAN interface.
  - Re-create a disabled VxLAN interface.
  - Test case count: 6
- **VxLAN-GPE** - CRD for VxLAN GPE tunnels.
  - Create VxLAN GPE interface.
  - Disable VxLAN interface.
  - Re-create a disabled VxLAN interface.
  - Test case count: 7
- **Vhost-user** - CRUD for Vhost-user interfaces.
  - Create, modify and delete Vhost-user interface, as client and server.
  - Test case count: 8
- **TAP** - CRUD for Tap interface management.
  - Create, modify and delete TAP interface.
  - Test case count: 3
- **VLAN** - CRUD for VLAN sub-interface management.
  - Create VLAN sub-interface over a physical interface.
  - Toggle interface state separately for super-interface and sub-interface.
  - Configure IP address and bridge domain assignment on sub-interface.
  - Configure VLAN tag rewrite on sub-interface.
  - Test case count: 24
- **ACL** - CRD for low-level classifiers: table and session management,
  - interface assignment.
  - Configure up to 2 classify tables.
  - Configure up to 2 classify sessions on one table.
  - Assign classify session to a physical interface.
  - Remove tables, sessions, interface assignments.
  - Test case count: 9
- **PBB** - CRD for provider backbone bridge sub-interface.
  - Configure, modify and remove a PBB sub-interface over a physical interface.
  - Test case count: 8
- **NSH_SFC** - CRD for NSH maps and entries, using NSH_SFC plugin.
  - Configure up to 2 NSH entries.
  - Configure up to 2 NSH maps.
  - Modify and delete NSH maps and entries.
  - Test case count: 8
- **LISP** - CRD for Lisp: mapping, locator set, adjacency, map resolver.
  - Toggle Lisp feature status.
  - Configure and delete Lisp mapping as local and remote.
  - Configure and delete Lisp adjacency mapping
  - Configure and delete Lisp map resolver, proxy ITR.
  - Test case count: 18
- **LISP GPE** - CRUD for LISP GPE mappings.
  - Toggle Lisp GPE feature status.
  - Configure Lisp GPE mappings.
  - Traffic test verifying encapsulation.
  - Test case count: 12
- **NAT** - CRD for NAT entries, interface assignment.
  - Configure and delete up to two NAT entries.
  - Assign NAT entries to a physical interface.
  - Test case count: 6
- **Port mirroring** - CRD for SPAN port mirroring, interface assignment.
  - Configure SPAN port mirroring on a physical interface, mirroring
  - up to 2 interfaces.
  - Remove SPAN configuration from interfaces.
  - Test case count: 14
- **ACL-PLUGIN** - CRD for high-level classifier
  - MAC + IP address classification.
  - IPv4, IPv6 address classification.
  - TCP, UDP, ICMP, ICMPv6 protocol/next-header classification.
  - port number classification.
  - ICMP, ICMPv6 code and type classification.
  - Test case count: 15
- **ProxyARP** - CRD for proxyARP feature.
  - Configure proxyARP.
  - Assign to interface.
  - Test case count: 3
- **ProxyND6** - CRD for Neighbor Discovery Proxy.
  - Configure ProxyND6 feature on interface.
  - Test case count: 4
- **DHCP Relay** - CRD for DHCP relay feature.
  - Configure DHCP Relays.
  - IPv4 and IPv6 variants.
  - Test case count: 4
- **SLAAC** - CRD for Stateless Address AutoConfiguration.
  - Configure SLAAC feature on interfaces.
  - Test case count: 7
- **Routing** - CRD for routing.
  - Configure single-hop route.
  - Configure multi-hop routes.
  - Configure blackhole route.
  - IPv4 and IPv6 variants.
  - Test case count: 6
- **Policer** - CRD for traffic policing feature.
  - Configure Policing rules.
  - Assign to interface.
  - Test case count: 6
- **Border Gateway Protocol** - CRUD and functional tests for BGP.
  - Configure peers and routes
  - Check interactions with another BGP peer.
  - Test case count: 13
- **Honeycomb Infractructure** - configuration persistence,
  - Netconf notifications for interface events,
  - Netconf negative tests aimed at specific issues
  - Netconf/Restconf northbound over IPv6
  - Test case count: 12

Total 219 Honeycomb functional tests in the CSIT-|release|.

Operational data in Honeycomb should mirror configuration data at all times.
Because of this, test cases follow this general pattern:

#. read operational data of the feature using restconf.
#. read status of the feature using VPP API dump.
#. modify configuration of the feature using restconf.
#. verify changes to operational data using restconf.
#. verify changes using VPP API dump, OR
#. send a packet to VPP node and observe behaviour to verify configuration.

Test cases involving network interfaces utilize the first two interfaces on
the DUT node.

Functional Tests Naming
-----------------------

CSIT-|release| introduced a common structured naming convention for all
performance and functional tests. This change was driven by substantially
growing number and type of CSIT test cases. Firstly, the original practice did
not always follow any strict naming convention. Secondly test names did not
always clearly capture tested packet encapsulations, and the actual type or
content of the tests. Thirdly HW configurations in terms of NICs, ports and
their locality were not captured either. These were but few reasons that drove
the decision to change and define a new more complete and stricter test naming
convention, and to apply this to all existing and new test cases.

The new naming should be intuitive for majority of the tests. The complete
description of CSIT test naming convention is provided on `CSIT test naming
page <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.

Here few illustrative examples of the new naming usage for functional test
suites:

#. **Physical port to physical port - a.k.a. NIC-to-NIC, Phy-to-Phy, P2P**

   - *eth2p-ethip4-ip4base-func.robot* => 2 ports of Ethernet, IPv4 baseline
     routed forwarding, functional tests.

#. **Physical port to VM (or VM chain) to physical port - a.k.a. NIC2VM2NIC,
   P2V2P, NIC2VMchain2NIC, P2V2V2P**

   - *eth2p-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-func.robot* => 2 ports of
     Ethernet, IPv4 VXLAN Ethernet, L2 bridge-domain switching to/from two vhost
     interfaces and one VM, functional tests.

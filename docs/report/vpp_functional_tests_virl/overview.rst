Overview
========

Tested Topologies VIRL
----------------------

CSIT VPP functional tests are executed on virtualized topologies created using
Virtual Internet Routing Lab (VIRL) simulation platform contributed by Cisco.
VIRL runs on physical baremetal servers hosted by LF FD.io project.  Majority
of the tests are executed in the three node logical test topology - Traffic
Generator (TG) node and two Systems Under Test (SUT) nodes connected in a
loop. Some tests use two node logical test topology - TG node and SUT1 node.
Both logical test topologies are shown in the figures below.

    +------------------------+           +------------------------+
    |                        |           |                        |
    |  +------------------+  |           |  +------------------+  |
    |  |                  <----------------->                  |  |
    |  |                  |  |           |  |                  |  |
    |  |       DUT1       <----------------->       DUT2       |  |
    |  +--^--^------------+  |           |  +------------^--^--+  |
    |     |  |               |           |               |  |     |
    |     |  |         SUT1  |           |  SUT2         |  |     |
    +------------------------+           +------------------------+
          |  |                                           |  |
          |  |                                           |  |
          |  |               +-----------+               |  |
          |  +--------------->           <---------------+  |
          |                  |    TG     |                  |
          +------------------>           <------------------+
                             +-----------+

                       +------------------------+
                       |                        |
                       |  +------------------+  |
          +--------------->                  <--------------+
          |            |  |                  |  |           |
          |  |------------>       DUT1       <-----------+  |
          |  |         |  +--^--^------------+  |        |  |
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

Virtual testbeds are created dynamically whenever a verification job is
started triggered by the patch submission to gerrit and destroyed upon
completion of all functional tests. During test execution, all nodes are
reachable thru the MGMT network connected to every node via dedicated NICs and
links (not shown above for clarity). Each node is a Virtual Machine and each
connection that is drawn on the diagram is available for use in any test case.

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a nested VM is created on SUT1 and/or SUT2 for the duration of
that particular test case only. DUT (VPP) test topology with VM is shown in
the figure below including the applicable packet flow thru the VM (marked in
the figure with ``***``).

    +------------------------+           +------------------------+
    |      +----------+      |           |      +----------+      |
    |      |    VM    |      |           |      |    VM    |      |
    |      |  ******  |      |           |      |  ******  |      |
    |      +--^----^--+      |           |      +--^----^--+      |
    |        *|    |*        |           |        *|    |*        |
    |  +------v----v------+  |           |  +------v----v------+  |
    |  |      *    *      |**|***********|**|      *    *      |  |
    |  |  *****    *******<----------------->*******    *****  |  |
    |  |  *    DUT1       |  |           |  |       DUT2    *  |  |
    |  +--^---------------+  |           |  +---------------^--+  |
    |    *|                  |           |                  |*    |
    |    *|            SUT1  |           |  SUT2            |*    |
    +------------------------+           +------------------^-----+
         *|                                                 |*
         *|                                                 |*
         *|                  +-----------+                  |*
         *|                  |           |                  |*
         *+------------------>    TG     <------------------+*
         ******************* |           |********************
                             +-----------+

VPP Functional Tests Overview
-----------------------------

Following VPP functional test areas are included in the CSIT |release| with
results listed in this report:

- **DHCP - Client and Proxy** - Dynamic Host Control Protocol Client and Proxy
  for IPv4, IPv6.
- **GRE Overlay Tunnels** - Generic Routing Encapsulation for IPv4.
- **L2BD Ethernet Switching** - L2 Bridge-Domain switched-forwarding for
  untagged Ethernet, dot1q and dot1ad tagged.
- **L2XC Ethernet Switching** - L2 Cross-Connect switched-forwarding for
  untagged Ethernet, dot1q and dot1ad tagged.
- **LISP Overlay Tunnels** - Locator/ID Separation Protocol overlay tunnels and
  locator/id mapping control.
- **Softwire Tunnels** - IPv4-in-IPv6 softwire tunnels.
- **Cop Address Security** - address white-list and black-list filtering for
  IPv4, IPv6.
- **IPSec - Tunnels and Transport** - IPSec tunnel and transport modes.
- **IPv6 Routed-Forwarding** - IPv6 routed-forwarding, NS/ND, RA, ICMPv6.
- **uRPF Source Security** - unicast Reverse Path Forwarding security.
- **Tap Interface** - baseline Linux tap interface tests.
- **Telemetry - IPFIX and SPAN** - IPFIX netflow statistics and SPAN port
  mirroring.
- **VRF Routed-Forwarding** - multi-context IPVPN routed-forwarding for IPv4,
  IPv6.
- **iACL Security** - ingress Access Control List security for IPv4, IPv6, MAC.
- **IPv4 Routed-Forwarding** - IPv4 routed-forwarding, RPF, ARP, Proxy ARP,
  ICMPv4.
- **QoS Policer Metering** - ingress packet rate measuring and marking for IPv4,
  IPv6.
- **VLAN Tag Translation** - L2 VLAN tag translation 2to2, 2to1, 1to2, 1to1.
- **VXLAN Overlay Tunnels** - VXLAN tunneling for L2-over-IP, for IPv4, IPv6.

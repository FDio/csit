Overview
========

Functional tests run on virtual testbeds which are created in VIRL running on a
Cisco UCS C240 servers hosted in Linux Foundation labs. There is currently only
one testbed topology being used for functional testing - a three node topology
with two links between each pair of nodes as shown in this diagram::

    +--------+                      +--------+
    |        |                      |        |
    |  SUT1  <---------------------->  SUT2  |
    |        <---------------------->        |
    |        |                      |        |
    +---^^---+                      +---^^---+
        ||                              ||
        ||          +--------+          ||
        ||          |        |          ||
        |+---------->   TG   <----------+|
        +----------->        <-----------+
                    |        |
                    +--------+

Virtual testbeds are created dynamically whenever a patch is submitted to gerrit
and destroyed upon completion of all functional tests. During test execution,
all nodes are reachable thru the MGMT network connected to every node via
dedicated NICs and links (not shown above for clarity). Each node is a Virtual
Machine and each connection that is drawn on the diagram is available for use in
any test case.

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a nested VM is created on SUT1 and/or SUT2 for the duration of that
particular test case only. DUT (VPP) test topology with VM is shown in the
diagram below including the packet flow (marked with ``*``)::

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

The following functional test suites are included in the CSIT |release| and
this report - test areas added since CSIT rls1609 got marked with [&], extended
areas marked with [%]:

- **L2XC [%]** - L2 Cross-Connect switching of Ethernet frames (untagged, VLAN
  single-tag 802.1q, double-tag 802.1ad).
- **L2BD [%]** - L2 Bridge-Domain switching of Ethernet frames (untagged,
  802.1q, 802.1ad).
- **IPv4 [%]** - IPv4 routed-forwarding, RPF, ARP, Proxy ARP, ICMPv4.
- **IPv6 [%]** - IPv6 routed-forwarding, NS/ND, RA, ICMPv6.
- **DHCP [%]** - DHCP Client and Proxy (IPv4, IPv6).
- **VXLAN** - VXLAN tunnelling dataplane with L2BD, L2XC (untagged, 802.1q).
- **COP** - COP address security, white-listing and black-listing (IPv4, IPv6).
- **GRE [%]** - GRE tunnelling dataplane with IP routed-forwarding (IPv4).
- **LISP [%]** - LISP tunneling dataplane with IP routed-forwarding (IPv4) and
  API functionality.
- **iACL [%]** - Ingress Access Control List security (IPv4, IPv6, L2).
- **VRF [&]** - IP VPN routed-forwarding (IPv4, IPv6).
- **QoS Policer [&]** - ingress packet rate measuring, marking and limiting
  (IPv4, IPv6).
- **IPFIX [&]** - IPFIX Netflow (IPv4, IPv6).
- **IPSec [&]** - IPSec transport and tunnel mode (IPv4, IPv6).
- **Softwire [&]** - IPv4-over-IPv6 Softwire Concentration including
  LightWeight4over6, MAP-E, MAP-T.
- **VLAN rewrites [&]** - L2 VLAN rewrite tests 2-2, 2-1, 1-2 with L2XC and L2BD.
- **Tap Interface [&]** - baseline Linux tap interface tests.
- **HoneyComb [&]** - HoneyComb control plane interface into VPP.

Total 252 functional tests in the CSIT |release| (up from 199 functional
tests in the CSIT rls1609).

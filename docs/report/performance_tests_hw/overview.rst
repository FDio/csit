Overview
========

CSIT performance tests are executed on physical baremetal servers located in
Linux Foundation FD.io CPL labs. Testbed physical topology is presented in the
figure below.::

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

SUT1 and SUT2 are two System Under Test servers (Cisco UCS C240, each with two
Intel XEON CPUs), TG is a Traffic Generator (TG, another Cisco UCS C240, with
two Intel XEON CPUs). SUTs run VPP SW application in Linux user-mode as a
Device Under Test (DUT). TG runs T-Rex SW application as a packet Traffic
Generator. Physical connectivity between SUTs and to TG is provided using
different NIC models that need to be tested for performance. Currently
installed and tested NIC models include:

- 2port10GE X520-DA2 Intel.
- 2port10GE X710 Intel.
- 2port10GE VIC1227 Cisco.
- 2port40GE VIC1385 Cisco.
- 2port40GE XL710 Intel.

Detailed test bed specification and topology is described in
[[CSIT/CSIT_LF_testbed]].

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a VM is created on SUT1 and SUT2. DUT (VPP) test topology with VM
is shown in the diagram below including the packet flow (marked with \*\*\*).

Note that for VM tests, packets are switched by DUT (VPP) twice, hence the
throughput rates measured by TG must be multiplied by two to represent the
actual DUT packet forwarding rate.

Performance tests are split into two main categories:

- Throughput discovery - discovery of packet forwarding rate using binary search
  in accordance to RFC2544.

  - NDR - discovery of Non Drop Rate, zero packet loss.
  - PDR - discovery of Partial Drop Rate, with specified non-zero packet loss.

- Throughput verification - verification of packet forwarding rate against
  previously discovered throughput rate. These tests are currently done against
  0.9 of reference NDR, with reference rates updated periodically.

CSIT |release| includes following performance test suites:

- 2port10GE X520-DA2 Intel

  - **L2XC** - L2 Cross-Connect switched-forwarding of untagged, dot1q, dot1ad
    VLAN tagged Ethernet frames.
  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with and without MAC learning.
  - **IPv4** - IPv4 routed-forwarding.
  - **IPv6** - IPv6 routed-forwarding.
  - **IPv4 Scale** - IPv4 routed-forwarding with 20k, 200k and 2M FIB entries.
  - **IPv6 Scale** - IPv6 routed-forwarding with 20k, 200k and 2M FIB entries.
  - **VM with vhost-user** - switching between NIC ports and VM over vhost-user
    interfaces in different switching modes incl. L2 Cross-Connect, L2
    Bridge-Domain, VXLAN with L2BD, IPv4 routed-forwarding.
  - **COP** - IPv4 and IPv6 routed-forwarding with COP address security.
  - **iACL** - IPv4 and IPv6 routed-forwarding with iACL address security.
  - **LISP** - LISP overlay tunneling for IPv4-over-IPV4, IPv6-over-IPv4,
    IPv6-over-IPv6, IPv4-over-IPv6 in IPv4 and IPv6 routed-forwarding modes.
  - **VXLAN** - VXLAN overlay tunnelling integration with L2XC.
  - **QoS Policer** - ingress packet rate measuring, marking and limiting
    (IPv4).

- 2port40GE XL710 Intel

  - **L2XC** - L2 Cross-Connect switched-forwarding of untagged Ethernet frames.
  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.
  - **IPv4** - IPv4 routed-forwarding.
  - **IPv6** - IPv6 routed-forwarding.

- 2port10GE X710 Intel

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.

- 2port10GE VIC1227 Cisco

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.

- 2port40GE VIC1385 Cisco

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
     with MAC learning.


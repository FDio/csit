Overview
========

At a physical level there are actually five units of 10GE and 40GE NICs per
SUT made by different vendors: Intel 2p10GE NICs (x520, x710), Intel 40GE NICs
(xl710), Cisco 2p10GE VICs, Cisco 2p40GE VICs. During test execution, all nodes
are reachable thru the MGMT network connected to every node via dedicated NICs
and links (not shown above for clarity). Currently the performance tests only
utilize one model of Intel NICs.  Detailed test bed specification and topology
is described in [[CSIT/CSIT_LF_testbed]].

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a VM is created on SUT1 and SUT2. DUT (VPP) test topology with VM
is shown in the diagram below including the packet flow (marked with \*\*\*)::

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

Note that for VM tests, packets are switched by DUT (VPP) twice, hence the
throughput rates measured by TG must be multiplied by two to represent the
actual DUT packet forwarding rate.

Because performance testing is run on physical test beds and some tests require
a long time to complete, the performance test jobs have been split into short
duration and long duration variants. The long performance jobs are run on a
periodic basis and run all of the long performance test suites discovering
throughput rates - NDR (Non-Drop Rate) and PDR (Partial Drop Rate) - and
measuring packet latency. The short performance jobs are run on demand and run
the short performance test suites verifying packet throughput against the
reference NDR rates. There are also separate test suites for each NIC type.

The following performance test suites are included in the CSIT-17.01 Release and
measurements listed in this report - test areas added since CSIT-16.09 got
marked with "[&]", extended areas marked with "[%]":

- Long performance test suites with Intel X520-DA2 NIC (2 port 10GbE) - total
  of 469 tests:

  - **L2XC** - NDR & PDR for L2 Cross-Connect switched-forwarding of untagged \
    and QinQ, 801.2Q Vlan, VXLAN tagged packets.
  - **L2BD** - NDR & PDR for L2 Bridge Domain switched-forwarding.
  - **IPv4** - NDR & PDR for IPv4 routed-forwarding.
  - **IPv6** - NDR & PDR for IPv6 routed-forwarding.
  - **COP** - NDR & PDR for IPv4 and IPv6 routed-forwarding with COP address \
    security.
  - **iACL** - NDR & PDR for IPv4 and IPv6 routed-forwarding with iACL address \
    security.
  - **LISP** - NDR & PDR for LISP tunneling dataplane with IP \
    routed-forwarding (IPv4).
  - **VXLAN** - NDR & PDR for VXLAN tunnelling integration with L2XC.
  - **QoS Policer** - NDR & PDR for ingress packet rate measuring, marking \
    and limiting (IPv4).
  - **IPv4 Scale** - NDR & PDR for IPv4 routed-forwarding with 20K, 200K, \
    2M FIB entries.
  - **IPv6 Scale** - NDR & PDR for IPv6 routed-forwarding with 20K, 200K, \
    2M FIB entries.
  - **vhost-user [&]** - NDR & PDR for L2 Cross-Connect, L2 Bridge-Domain, IPv4 \
    routed-forwarding with VM over vhost-user interface.

- Long performance test suites with Intel XL-710 NIC (2 ports 40GbE) - total of
  9 tests:

  - **L2 Cross-Connect** - NDR & PDR for L2 Cross-Connect \
    switched-forwarding of untagged and QinQ, 801.2Q Vlan, VXLAN tagged packets.
  - **L2 Bridge-Domain** - NDR & PDR for L2 Bridge Domain \
    switched-forwarding.
  - **IPv4** - NDR & PDR for IPv4 routed-forwarding.
  - **IPv6** - NDR & PDR for IPv6 routed-forwarding.


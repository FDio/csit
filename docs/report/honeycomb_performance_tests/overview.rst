Overview
========

Tested Physical Topologies
--------------------------

CSIT VPP performance tests are executed on physical baremetal servers hosted by
LF FD.io project. Testbed physical topology is shown in the figure below.

::

    +------------------------+           +------------------------+
    |                        |           |                        |
    |  +------------------+  |           |  +------------------+  |
    |  |                  |  |           |  |                  |  |
    |  |                  <----------------->                  |  |
    |  |       DUT1       |  |           |  |       DUT2       |  |
    |  +--^---------------+  |           |  +---------------^--+  |
    |     |                  |           |                  |     |
    |     |            SUT1  |           |  SUT2            |     |
    +------------------------+           +------------------^-----+
          |                                                 |
          |                                                 |
          |                  +-----------+                  |
          |                  |           |                  |
          +------------------>    TG     <------------------+
                             |           |
                             +-----------+

SUT1 runs VPP SW application in Linux user-mode as a
Device Under Test (DUT), and a python script to generate traffic. SUT2 and TG
are unused.
sical connectivity between SUTs and to TG is provided using
different NIC model. Currently installed NIC models include:

Performance tests involve sending Netconf requests over localhost to the
Honeycomb listener port, and measuring response time.

Note that reported performance results are specific to the SUTs tested.
Current LF FD.io SUTs are based on Intel XEON E5-2699v3 2.3GHz CPUs. SUTs with
other CPUs are likely to yield different results.

For detailed LF FD.io test bed specification and physical topology please refer
to `LF FDio CSIT testbed wiki page
<https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

Performance Tests Coverage
--------------------------

As of right now, there is only a single Honeycomb performance test. Measuring
response time for a simple read operation, performed synchronously and using
single (not batch) requests.

Currently the tests do not trigger automatically, but can be run on-demand from
the hc2vpp project.

Performance Tests Naming
------------------------

CSIT |release| follows a common structured naming convention for all
performance and system functional tests, introduced in CSIT |release-1|.

The naming should be intuitive for majority of the tests. Complete
description of CSIT test naming convention is provided on `CSIT test naming wiki
<https://wiki.fd.io/view/CSIT/csit-test-naming>`_.

Here few illustrative examples of the new naming usage for performance test
suites:

#. **Physical port to physical port - a.k.a. NIC-to-NIC, Phy-to-Phy, P2P**

   - *PortNICConfig-WireEncapsulation-PacketForwardingFunction-
     PacketProcessingFunction1-...-PacketProcessingFunctionN-TestType*
   - *10ge2p1x520-dot1q-l2bdbasemaclrn-ndrdisc.robot* => 2 ports of 10GE on
     Intel x520 NIC, dot1q tagged Ethernet, L2 bridge-domain baseline switching
     with MAC learning, NDR throughput discovery.
   - *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrchk.robot* => 2 ports of 10GE
     on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain baseline
     switching with MAC learning, NDR throughput discovery.
   - *10ge2p1x520-ethip4-ip4base-ndrdisc.robot* => 2 ports of 10GE on Intel
     x520 NIC, IPv4 baseline routed forwarding, NDR throughput discovery.
   - *10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot* => 2 ports of 10GE on
     Intel x520 NIC, IPv6 scaled up routed forwarding, NDR throughput
     discovery.

#. **Physical port to VM (or VM chain) to physical port - a.k.a. NIC2VM2NIC,
   P2V2P, NIC2VMchain2NIC, P2V2V2P**

   - *PortNICConfig-WireEncapsulation-PacketForwardingFunction-
     PacketProcessingFunction1-...-PacketProcessingFunctionN-VirtEncapsulation-
     VirtPortConfig-VMconfig-TestType*
   - *10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot* => 2 ports
     of 10GE on Intel x520 NIC, dot1q tagged Ethernet, L2 bridge-domain
     switching to/from two vhost interfaces and one VM, NDR throughput
     discovery.
   - *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot* => 2
     ports of 10GE on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain
     switching to/from two vhost interfaces and one VM, NDR throughput
     discovery.
   - *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc.robot* => 2
     ports of 10GE on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain
     switching to/from four vhost interfaces and two VMs, NDR throughput
     discovery.

Methodology: Multi-Core
-----------------------

**Multi-core Test** - CSIT |release| multi-core tests are executed in the
following thread and core configurations:

#. 1t - 1 Honeycomb Netconf thread on 1 CPU physical core.
#. 8t - 8 Honeycomb Netconf thread on 8 CPU physical core.
#. 16t - 16 Honeycomb Netconf thread on 16 CPU physical core.

Traffic generator also uses multiple threads/cores, to simulate multiple
Netconf clients accessing the Honeycomb server.

Methodology: Performance measurement
------------------------------------

The following values are measured and reported in tests:

- Average request rate. Averaged over the entire test duration, over all client
threads. Negative replies (if any) are not counted and are reported separately.

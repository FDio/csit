Overview
========

Tested Physical Topologies
--------------------------

CSIT VPP performance tests are executed on physical baremetal servers hosted by LF
FD.io project. Testbed physical topology is shown in the figure below.

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

SUT1 and SUT2 are two System Under Test servers (Cisco UCS C240, each with two
Intel XEON CPUs), TG is a Traffic Generator (TG, another Cisco UCS C240, with
two Intel XEON CPUs). SUTs run VPP SW application in Linux user-mode as a
Device Under Test (DUT). TG runs TRex SW application as a packet Traffic
Generator. Physical connectivity between SUTs and to TG is provided using
different NIC models that need to be tested for performance. Currently
installed and tested NIC models include:

#. 2port10GE X520-DA2 Intel.
#. 2port10GE X710 Intel.
#. 2port10GE VIC1227 Cisco.
#. 2port40GE VIC1385 Cisco.
#. 2port40GE XL710 Intel.

From SUT and DUT perspective, all performance tests involve forwarding packets
between two physical Ethernet ports (10GE or 40GE). Due to the number of
listed NIC models tested and available PCI slot capacity in SUT servers, in
all of the above cases both physical ports are located on the same NIC. In
some test cases this results in measured packet throughput being limited not
by VPP DUT but by either the physical interface or the NIC capacity.

Going forward CSIT project will be looking to add more hardware into FD.io
performance labs to address larger scale multi-interface and multi-NIC
performance testing scenarios.

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a VM is created on SUT1 and SUT2. DUT (VPP) test topology with VM
is shown in the figure below including applicable packet flow thru the VM
(marked in the figure with ``***``).

::

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

For VM tests, packets are switched by DUT (VPP) twice, hence the
throughput rates measured by TG (and listed in this report) must be multiplied
by two to represent the actual DUT aggregate packet forwarding rate.

Note that reported VPP performance results are specific to the SUT tested.
Current LF FD.io SUTs are based on Intel XEON E5-2699v3 2.3GHz CPUs. SUTs with
other CPUs are likely to yield different results. A good rule of thumb, that
can be applied to estimate VPP packet thoughput for Phy-to-Phy (NIC-to-NIC,
PCI-to-PCI) topology, is to expect the forwarding performance to be
proportional to CPU core frequency, assuming CPU is the only limiting factor
and all other SUT aspects equal to FD.io CSIT environment. The same rule of
thumb can be also applied for Phy-to-VM-to-Phy (NIC-to-VM-to-NIC) topology,
but due to much higher dependency on very high frequency memory operations and
sensitivity to Linux kernel scheduler settings and behaviour, this estimation
may not always yield good enough accuracy.

Detailed LF FD.io test bed specification and physical topology are described
in `wiki CSIT LF FDio testbed <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

Performance Tests Coverage
--------------------------

Performance tests are split into the two main categories:

- Throughput discovery - discovery of packet forwarding rate using binary search
  in accordance to RFC2544.

  - NDR - discovery of Non Drop Rate packet throughput, at zero packet loss;
    followed by packet one-way latency measurements at 10%, 50% and 100% of
    discovered NDR throughput.
  - PDR - discovery of Partial Drop Rate, with specified non-zero packet loss
    currently set to 0.5%; followed by packet one-way latency measurements at
    100% of discovered PDR throughput.

- Throughput verification - verification of packet forwarding rate against
  previously discovered throughput rate. These tests are currently done against
  0.9 of reference NDR, with reference rates updated periodically.

CSIT |release| includes following performance test suites, listed per NIC type:

- 2port10GE X520-DA2 Intel

  - **L2XC** - L2 Cross-Connect switched-forwarding of untagged, dot1q, dot1ad
    VLAN tagged Ethernet frames.
  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning; disabled MAC learning i.e. static MAC tests to be added.
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
  - **VXLAN** - VXLAN overlay tunnelling integration with L2XC and L2BD.
  - **QoS Policer** - ingress packet rate measuring, marking and limiting
    (IPv4).

- 2port40GE XL710 Intel

  - **L2XC** - L2 Cross-Connect switched-forwarding of untagged Ethernet frames.
  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.
  - **IPv4** - IPv4 routed-forwarding.
  - **IPv6** - IPv6 routed-forwarding.
  - **VM with vhost-user** - switching between NIC ports and VM over vhost-user
    interfaces in different switching modes incl. L2 Bridge-Domain.

- 2port10GE X710 Intel

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.
  - **VM with vhost-user** - switching between NIC ports and VM over vhost-user
    interfaces in different switching modes incl. L2 Bridge-Domain.

- 2port10GE VIC1227 Cisco

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
    with MAC learning.

- 2port40GE VIC1385 Cisco

  - **L2BD** - L2 Bridge-Domain switched-forwarding of untagged Ethernet frames
     with MAC learning.

Execution of performance tests takes time, especially the throughput discovery
tests. Due to limited HW testbed resources available within FD.io labs hosted
by Linux Foundation, the number of tests for NICs other than X520 (a.k.a.
Niantic) has been limited to few baseline tests. Over time we expect the HW
testbed resources to grow, and will be adding complete set of performance
tests for all models of hardware to be executed regularly and(or)
continuously.

Performance Tests Naming
------------------------

CSIT |release| introduced a common structured naming convention for all
performance and functional tests. This change was driven by substantially
growing number and type of CSIT test cases. Firstly, the original practice did
not always follow any strict naming convention. Secondly test names did not
always clearly capture tested packet encapsulations, and the actual type or
content of the tests. Thirdly HW configurations in terms of NICs, ports and
their locality were not captured either. These were but few reasons that drove
the decision to change and define a new more complete and stricter test naming
convention, and to apply this to all existing and new test cases.

The new naming should be intuitive for majority of the tests. The complete
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

Methodology: Multi-Thread and Multi-Core
----------------------------------------

**HyperThreading** - CSIT |release| performance tests are executed with SUT
servers' Intel XEON CPUs configured in HyperThreading Disabled mode (BIOS
settings). This is the simplest configuration used to establish baseline
single-thread single-core SW packet processing and forwarding performance.
Subsequent releases of CSIT will add performance tests with Intel
HyperThreading Enabled (requires BIOS settings change and hard reboot).

**Multi-core Test** - CSIT |release| multi-core tests are executed in the
following VPP thread and core configurations:

#. 1t1c - 1 VPP worker thread on 1 CPU physical core.
#. 2t2c - 2 VPP worker threads on 2 CPU physical cores.
#. 4t4c - 4 VPP threads on 4 CPU physical cores.

Note that in quite a few test cases running VPP on 2 or 4 physical cores hits
the tested NIC I/O bandwidth or packets-per-second limit.

Methodology: Packet Throughput
------------------------------

Following values are measured and reported for packet throughput tests:

- NDR binary search per RFC2544:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps
    (2x <per direction packets-per-second>)"
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)"

- PDR binary search per RFC2544:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps (2x
    <per direction packets-per-second>)"
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)"
  - Packet loss tolerance: "LOSS_ACCEPTANCE <accepted percentage of packets
    lost at PDR rate>""

- NDR and PDR are measured for the following L2 frame sizes:

  - IPv4: 64B, IMIX_v4_1 (28x64B,16x570B,4x1518B), 1518B, 9000B.
  - IPv6: 78B, 1518B, 9000B.


Methodology: Packet Latency
---------------------------

TRex Traffic Generator (TG) is used for measuring latency of VPP DUTs. Reported
latency values are measured using following methodology:

- Latency tests are performed at 10%, 50% of discovered NDR rate (non drop rate)
  for each NDR throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the rate of
  10kpps at the prescribed packet size; these are sent in addition to the main
  load streams.
- TG reports min/avg/max latency values per stream direction, hence two sets
  of latency values are reported per test case; future release of TRex is
  expected to report latency percentiles.
- Reported latency values are aggregate across two SUTs due to three node
  topology used for all performance tests; for per SUT latency, reported value
  should be divided by two.
- 1usec is the measurement accuracy advertised by TRex TG for the setup used in
  FD.io labs used by CSIT project.
- TRex setup introduces an always-on error of about 2*2usec per latency flow -
  additonal Tx/Rx interface latency induced by TRex SW writing and reading
  packet timestamps on CPU cores without HW acceleration on NICs closer to the
  interface line.


Methodology: KVM VM vhost
-------------------------

CSIT |release| introduced environment configuration changes to KVM Qemu vhost-
user tests in order to more representatively measure VPP-17.01 performance in
configurations with vhost-user interfaces and VMs.

Current setup of CSIT FD.io performance lab is using tuned settings for more
optimal performance of KVM Qemu:

- Default Qemu virtio queue size of 256 descriptors.
- Adjusted Linux kernel CFS scheduler settings, as detailed on this CSIT wiki
  page: https://wiki.fd.io/view/CSIT/VM-vhost-env-tuning.

Adjusted Linux kernel CFS settings make the NDR and PDR throughput performance
of VPP+VM system less sensitive to other Linux OS system tasks by reducing
their interference on CPU cores that are designated for critical software
tasks under test, namely VPP worker threads in host and Testpmd threads in
guest dealing with data plan.
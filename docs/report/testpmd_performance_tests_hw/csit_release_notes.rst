CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Naming change for all Testpmd performance test suites and test cases.

#. Added Testpmd tests

    - new NICs - Intel x520


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

Multi-Thread and Multi-Core Measurements
----------------------------------------

**HyperThreading** - CSIT |release| performance tests are executed with SUT
servers' Intel XEON CPUs configured in HyperThreading Disabled mode (BIOS
settings). This is the simplest configuration used to establish baseline
single-thread single-core SW packet processing and forwarding performance.
Subsequent releases of CSIT will add performance tests with Intel
HyperThreading Enabled (requires BIOS settings change and hard reboot).

**Multi-core Test** - CSIT |release| multi-core tests are executed in the
following Testpmd thread and core configurations:

#. 1t1c - 1 Testpmd worker thread on 1 CPU physical core.
#. 2t2c - 2 Testpmd worker threads on 2 CPU physical cores.
#. 4t4c - 4 Testpmd threads on 4 CPU physical cores.

Note that in quite a few test cases running Testpmd on 2 or 4 physical cores
hits the tested NIC I/O bandwidth or packets-per-second limit.

Packet Throughput Measurements
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

  - IPv4: 64B, 1518B, 9000B.


Packet Latency Measurements
---------------------------

TRex Traffic Generator (TG) is used for measuring latency of Testpmd DUTs.
Reported latency values are measured using following methodology:

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


Report Addendum Tests - More NICs
---------------------------------

Adding test cases with more NIC types. Once the results become available, they
will be published as an addendum to the current version of CSIT |release|
report.

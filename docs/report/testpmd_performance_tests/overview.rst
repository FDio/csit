Overview
========

Tested Physical Topologies
--------------------------

CSIT Testpmd performance tests are executed on physical baremetal servers hosted
by LF FD.io project. Testbed physical topology is shown in the figure below.

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

SUT1 and SUT2 are two System Under Test servers (currently Cisco UCS C240,
each with two Intel XEON CPUs), TG is a Traffic Generator (TG, currently
another Cisco UCS C240, with two Intel XEON CPUs). SUTs run Testpmd SW
application in Linux user-mode as a Device Under Test (DUT). TG runs TRex SW
application as a packet Traffic Generator. Physical connectivity between SUTs
and to TG is provided using direct links (no L2 switches) connecting different
NIC models that need to be tested for performance. Currently installed and
tested NIC models include:

#. 2port10GE X520-DA2 Intel.
#. 2port10GE X710 Intel.
#. 2port10GE VIC1227 Cisco.
#. 2port40GE VIC1385 Cisco.
#. 2port40GE XL710 Intel.

Detailed LF FD.io test bed specification and topology is described in
`wiki CSIT LF testbed <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

Performance Tests Coverage
--------------------------

Performance tests are split into the two main categories:

- Throughput discovery - discovery of packet forwarding rate using binary search
  in accordance with RFC2544.

  - NDR - discovery of Non Drop Rate packet throughput, at zero packet loss;
    followed by packet one-way latency measurements at 10%, 50% and 100% of
    discovered NDR throughput.
  - PDR - discovery of Partial Drop Rate, with specified non-zero packet loss
    currently set to 0.5%; followed by packet one-way latency measurements at
    100% of discovered PDR throughput.

- Throughput verification - verification of packet forwarding rate against
  previously discovered NDR throughput. These tests are currently done against
  0.9 of reference NDR, with reference rates updated periodically.

CSIT |release| includes following performance test suites, listed per NIC type:

- 2port10GE X520-DA2 Intel

  - **L2IntLoop** - L2 Interface Loop forwarding any Ethernet frames between
    two Interfaces.

Execution of performance tests takes time, especially the throughput discovery
tests. Due to limited HW testbed resources available within FD.io labs hosted
by Linux Foundation, the number of tests for NICs other than X520 (a.k.a.
Niantic) has been limited to few baseline tests. Over time we expect the HW
testbed resources to grow, and will be adding complete set of performance
tests for all models of hardware to be executed regularly and(or)
continuously.

Methodology: Multi-Thread and Multi-Core
----------------------------------------

**HyperThreading** - CSIT |release| performance tests are executed with SUT
servers' Intel XEON CPUs configured in HyperThreading Disabled mode (BIOS
settings). This is the simplest configuration used to establish baseline
single-thread single-core SW packet processing and forwarding performance.
Subsequent releases of CSIT will add performance tests with Intel
HyperThreading Enabled (requires BIOS settings change and hard reboot).

**Multi-core Test** - CSIT |release| multi-core tests are executed in the
following Testpmd thread and core configurations:

#. 1t1c - 1 Testpmd pmd thread on 1 CPU physical core.
#. 2t2c - 2 Testpmd pmd threads on 2 CPU physical cores.
#. 4t4c - 4 Testpmd pmd threads on 4 CPU physical cores.

Note that in many tests running Testpmd reaches tested NIC I/O bandwidth
or packets-per-second limit.

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

  - IPv4: 64B, 1518B, 9000B.


Methodology: Packet Latency
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
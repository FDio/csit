Overview
========

Tested Physical Topologies
--------------------------

CSIT DPDK performance tests are executed on physical baremetal servers hosted
by :abbr:`LF (Linux Foundation)` FD.io project. Testbed physical topology is
shown in the figure below.::

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
two Intel XEON CPUs). SUTs run Testpmd/L3FWD SW SW application in Linux
user-mode as a Device Under Test (DUT). TG runs TRex SW application as a packet
Traffic Generator. Physical connectivity between SUTs and to TG is provided
using different NIC models that need to be tested for performance. Currently
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

Note that reported DUT (DPDK) performance results are specific to the SUTs
tested. Current :abbr:`LF (Linux Foundation)` FD.io SUTs are based on Intel
XEON E5-2699v3 2.3GHz CPUs. SUTs with other CPUs are likely to yield different
results. A good rule of thumb, that can be applied to estimate DPDK packet
thoughput for Phy-to-Phy (NIC-to-NIC, PCI-to-PCI) topology, is to expect
the forwarding performance to be proportional to CPU core frequency,
assuming CPU is the only limiting factor and all other SUT parameters
equivalent to FD.io CSIT environment. The same rule of thumb can be also
applied for Phy-to-VM/LXC-to-Phy (NIC-to-VM/LXC-to-NIC) topology, but due to
much higher dependency on intensive memory operations and sensitivity to Linux
kernel scheduler settings and behaviour, this estimation may not always yield
good enough accuracy.

For detailed :abbr:`LF (Linux Foundation)` FD.io test bed specification and
physical topology please refer to `LF FD.io CSIT testbed wiki page
<https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

Performance Tests Coverage
--------------------------

Performance tests are split into two main categories:

- Throughput discovery - discovery of packet forwarding rate using binary search
  in accordance to :rfc:`2544`.

  - NDR - discovery of Non Drop Rate packet throughput, at zero packet loss;
    followed by one-way packet latency measurements at 10%, 50% and 100% of
    discovered NDR throughput.
  - PDR - discovery of Partial Drop Rate, with specified non-zero packet loss
    currently set to 0.5%; followed by one-way packet latency measurements at
    100% of discovered PDR throughput.

- Throughput verification - verification of packet forwarding rate against
  previously discovered throughput rate. These tests are currently done against
  0.9 of reference NDR, with reference rates updated periodically.

|csit-release| includes following performance test suites, listed per NIC type:

- 2port10GE X520-DA2 Intel

  - **L2IntLoop** - L2 Interface Loop forwarding any Ethernet frames between
    two Interfaces.

- 2port40GE XL710 Intel

  - **L2IntLoop** - L2 Interface Loop forwarding any Ethernet frames between
    two Interfaces.

- 2port10GE X520-DA2 Intel

  - **IPv4 Routed Forwarding** - L3 IP forwarding of Ethernet frames between
    two Interfaces.

Execution of performance tests takes time, especially the throughput discovery
tests. Due to limited HW testbed resources available within FD.io labs hosted
by Linux Foundation, the number of tests for NICs other than X520 (a.k.a.
Niantic) has been limited to few baseline tests. Over time we expect the HW
testbed resources to grow, and will be adding complete set of performance
tests for all models of hardware to be executed regularly and(or)
continuously.

Performance Tests Naming
------------------------

|csit-release| follows a common structured naming convention for all performance
and system functional tests, introduced in CSIT rls1701.

The naming should be intuitive for majority of the tests. Complete description
of CSIT test naming convention is provided on :ref:`csit_test_naming`.

Methodology: Multi-Core and Multi-Threading
-------------------------------------------

**Intel Hyper-Threading** - |csit-release| performance tests are executed with
SUT servers' Intel XEON processors configured in Intel Hyper-Threading Disabled
mode (BIOS setting). This is the simplest configuration used to establish
baseline single-thread single-core application packet processing and forwarding
performance. Subsequent releases of CSIT will add performance tests with Intel
Hyper-Threading Enabled (requires BIOS settings change and hard reboot of
server).

**Multi-core Tests** - |csit-release| multi-core tests are executed in the
following VPP thread and core configurations:

#. 1t1c - 1 pmd worker thread on 1 CPU physical core.
#. 2t2c - 2 pmd worker threads on 2 CPU physical cores.

Note that in many tests running Testpmd/L3FWD reaches tested NIC I/O bandwidth
or packets-per-second limit.

Methodology: Packet Throughput
------------------------------

Following values are measured and reported for packet throughput tests:

- NDR binary search per :rfc:`2544`:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps
    (2x <per direction packets-per-second>)"
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)"

- PDR binary search per :rfc:`2544`:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps (2x
    <per direction packets-per-second>)"
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)"
  - Packet loss tolerance: "LOSS_ACCEPTANCE <accepted percentage of packets
    lost at PDR rate>""

- NDR and PDR are measured for the following L2 frame sizes:

  - IPv4: 64B, 1518B, 9000B.

All rates are reported from external Traffic Generator perspective.


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

Methodology: TRex Traffic Generator Usage
-----------------------------------------

The `TRex traffic generator <https://wiki.fd.io/view/TRex>`_ is used for all
CSIT performance tests. TRex stateless mode is used to measure NDR and PDR
throughputs using binary search (NDR and PDR discovery tests) and for quick
checks of DUT performance against the reference NDRs (NDR check tests) for
specific configuration.

TRex is installed and run on the TG compute node. The typical procedure is:

- If the TRex is not already installed on TG, it is installed in the
  suite setup phase - see `TRex intallation`_.
- TRex configuration is set in its configuration file
  ::

  /etc/trex_cfg.yaml

- TRex is started in the background mode
  ::

  $ sh -c 'cd <t-rex-install-dir>/scripts/ && sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /tmp/trex.log 2>&1 &' > /dev/null

- There are traffic streams dynamically prepared for each test, based on traffic
  profiles. The traffic is sent and the statistics obtained using
  :command:`trex_stl_lib.api.STLClient`.

**Measuring packet loss**

- Create an instance of STLClient
- Connect to the client
- Add all streams
- Clear statistics
- Send the traffic for defined time
- Get the statistics

If there is a warm-up phase required, the traffic is sent also before test and
the statistics are ignored.

**Measuring latency**

If measurement of latency is requested, two more packet streams are created (one
for each direction) with TRex flow_stats parameter set to STLFlowLatencyStats. In
that case, returned statistics will also include min/avg/max latency values.

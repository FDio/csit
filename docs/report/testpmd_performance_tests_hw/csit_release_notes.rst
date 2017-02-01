CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added Testpmd tests

    - new NICs - Intel x520

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

#. 1t1c - 1 Testpmd pmd thread on 1 CPU physical core.
#. 2t2c - 2 Testpmd pmd threads on 2 CPU physical cores.
#. 4t4c - 4 Testpmd pmd threads on 4 CPU physical cores.

Note that in many tests running Testpmd reaches tested NIC I/O bandwidth
or packets-per-second limit.

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


Report Addendum Tests - Additional NICs
---------------------------------------

Adding test cases with more NIC types. Once the results become available, they
will be published as an addendum to the current version of CSIT |release|
report.

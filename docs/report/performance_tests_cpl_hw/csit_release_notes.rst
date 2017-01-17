CSIT Release Notes
==================

Changes in CSIT rls1701
-----------------------

Performance Tests Naming
------------------------

Measured Performance Improvements
---------------------------------

Multi-Thread(-Core) Measurements
--------------------------------

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

  - IPv4: 64B, IMIX_v4_1 (28x64B,16x570B,4x1518B), 1518B, 9000B.
  - IPv6: 78B, 1518B, 9000B.


Packet Latency Measurements
---------------------------

TRex traffic generator (TG) new (experimental) functionality is used for
measuring latency of VPP SUTs. Reported latency values are measured using
following methodology:

- Latency tests are performed at 10%, 50% of discovered NDR rate (non drop rate)
  for each NDR throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the rate of
  10kpps at the prescribed packet size; these are sent in addition to the main
  load streams.
- TG reports min/avg/max latency values per stream, hence two sets of latency
  values are reported per test case; future release of TRex is expected to
  report latency percentiles.
- Reported latency values are aggregate across two SUTs due to three node
  topology used for all performance tests; for per SUT latency, reported value
  should be divided by two.
- 1usec is measurements accuracy advertised by TRex TG for the setup used in
  FD.io labs.
- TRex setup introduces an always-on error of about 2*2usec per latency flow -
  additonal Tx/Rx interface latency induced by TRex SW writing and reading
  packet timestamps on CPU cores without HW acceleration on NICs closer to the
  interface line.


KVM VM vhost Measurements
-------------------------

Current setup of CSIT FD.io performance lab is using default Ubuntu 14.04.02
KVM Qemu settings:

- Default Qemu virtio queue size of 256 descriptors.
- Default Linux CFS scheduler settings.

These default settings make the NDR performance of VPP+VM system very sensitive
to any OS system tasks (i.e. Linux kernel) interference on CPU cores that are
designated for critical software tasks under test, namely VPP worker threads in
host and Testpmd threads in guest. CSIT committers decided against tweaking
listed default settings. Instead we decided to report the NDR and PDR
performance numbers with default settings. The impact of CPU jitter on SUTs
performance is clearly visible if one compares NDR and PDR results across
multiple test runs as presented in trending graphs in sections "VPP Trend
Graphs RFC2544:NDR" and "VPP Trend Graphs RFC2544:PDR". To bring NDR rate for
SUTs closer to PDR rates, both Qemu virtio queue size and Linux CFS scheduler
settings need to be adjusted.

Going forward, once integrated into CSIT system, we want to add a separate set
of tests with adjusted default parameters namely i) increased Qemu virtio queue
size to 1024 descriptors, ii) consider adjusting CFS scheduler settings for
tasks under test. Both are subject to ongoing improvements in Qemu code (see
added vhost functionality in Qemu 2.7) and VPP vhost-user driver (see vhost
indirect descriptors patch).


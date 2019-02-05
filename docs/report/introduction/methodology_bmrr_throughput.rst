(B)MRR Throughput
-----------------

Maximum Receive Rate (MRR) tests are complementary to MLRsearch tests,
as they provide a maximum "raw" throughput benchmark for development and
testing community. MRR tests measure the packet forwarding rate under
the maximum load offered by traffic generator over a set trial duration,
regardless of packet loss. Maximum load for specified Ethernet frame
size is set to the bi-directional link rate.

In |csit-release| MRR test code has been updated with a configurable
burst MRR parameters: trial duration and number of trials in a single
burst. This enabled a new Burst MRR (BMRR) methodology for more precise
performance trending.

Current parameters for BMRR tests:

- Ethernet frame sizes: 64B (78B for IPv6), IMIX, 1518B, 9000B; all
  quoted sizes include frame CRC, but exclude per frame transmission
  overhead of 20B (preamble, inter frame gap).

- Maximum load offered: 10GE and 40GE link (sub-)rates depending on NIC
  tested, with the actual packet rate depending on frame size,
  transmission overhead and traffic generator NIC forwarding capacity.

  - For 10GE NICs the maximum packet rate load is 2* 14.88 Mpps for 64B,
    a 10GE bi-directional link rate.
  - For 25GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 25GE bi-directional link sub-rate limited by TG 25GE NIC used,
    XXV710.
  - For 40GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 40GE bi-directional link sub-rate limited by TG 40GE NIC used,
    XL710. Packet rate for other tested frame sizes is limited by PCIe
    Gen3 x8 bandwidth limitation of ~50Gbps.

- Trial duration: 1 sec.

- Number of trials per burst: 10.

Similarly to NDR/PDR throughput tests, MRR test should be reporting bi-
directional link rate (or NIC rate, if lower) if tested VPP
configuration can handle the packet rate higher than bi-directional link
rate, e.g. large packet tests and/or multi-core tests.

MRR tests are currently used for FD.io CSIT continuous performance
trending and for comparison between releases. Daily trending job tests
subset of frame sizes, focusing on 64B (78B for IPv6) for all tests and
IMIX for selected tests (vhost, memif).

MRR-like measurements are being used to establish starting conditions
for experimental Probabilistic Loss Ratio Search (PLRsearch) used for
soak testing, aimed at verifying continuous system performance over an
extended period of time, hours, days, weeks, months. PLRsearch code is
currently in experimental phase in FD.io CSIT project.

.. _mrr_throughput:

MRR Throughput
--------------

Maximum Receive Rate (MRR) tests are complementary to MLRsearch tests,
as they provide a maximum "raw" throughput benchmark for the development and
testing community. MRR tests measure the packet forwarding rate under
the maximum load offered by traffic generator, over a set trial duration,
regardless of packet loss.

MRR tests are currently used for following test jobs:

- Report performance comparison: 64B, IMIX for vhost, memif.
- Daily performance trending: 64B, IMIX for vhost, memif.
- Per-patch performance verification: 64B.
- PLRsearch soaking tests: 64B.

Maximum offered load for specific L2 Ethernet frame size is set to
either the maximum bi-directional link rate or tested NIC model
capacity, as follows:

- For 10GE NICs, the maximum packet rate load is 2x14.88 Mpps for 64B, a
  10GE bi-directional link rate.
- For 25GE NICs, the maximum packet rate load is 2x18.75 Mpps for 64B, a
  25GE bi-directional link sub-rate limited by 25GE NIC used on TRex TG,
  XXV710.
- For 40GE NICs, the maximum packet rate load is 2x18.75 Mpps for 64B, a
  40GE bi-directional link sub-rate limited by 40GE NIC used on TRex
  TG,XL710. Packet rate for other tested frame sizes is limited by
  PCIeGen3 x8 bandwidth limitation of ~50Gbps.

MRR test code implements multiple bursts of offered packet load and has
two configurable burst parameters: individual trial duration and number
of trials in a single burst. This enables more precise performance
trending by providing more results data for analysis.

Burst parameter settings vary between different tests using MRR:

- MRR individual trial duration:

  - Report performance comparison: 1 sec.
  - Daily performance trending: 1 sec.
  - Per-patch performance verification: 10 sec.
  - PLRsearch soaking tests: 5.2 sec.

- Number of MRR trials per burst:

  - Report performance comparison: 10.
  - Daily performance trending: 10.
  - Per-patch performance verification: 5.
  - PLRsearch soaking tests: 1.

Performance Tests
-----------------

Performance trending relies on Maximum Receive Rate (MRR) tests.
MRR tests measure the packet forwarding rate, in multiple trials of set
duration, under the maximum load offered by traffic generator
regardless of packet loss. Maximum load for specified Ethernet frame
size is set to the bi-directional link rate.

Current parameters for performance trending MRR tests:

- **Ethernet frame sizes**: 64B (78B for IPv6 tests) for all tests, IMIX for
  selected tests (vhost, memif); all quoted sizes include frame CRC, but
  exclude per frame transmission overhead of 20B (preamble, inter frame
  gap).
- **Maximum load offered**: 10GE and 40GE link (sub-)rates depending on NIC
  tested, with the actual packet rate depending on frame size,
  transmission overhead and traffic generator NIC forwarding capacity.

  - For 10GE NICs the maximum packet rate load is 2* 14.88 Mpps for 64B,
    a 10GE bi-directional link rate.
  - For 40GE NICs the maximum packet rate load is 2* 18.75 Mpps for 64B,
    a 40GE bi-directional link sub-rate limited by the packet forwarding
    capacity of 2-port 40GE NIC model (XL710) used on T-Rex Traffic
    Generator.

- **Trial duration**: 1 sec.
- **Number of trials per test**: 10.
- **Test execution frequency**: twice a day, every 12 hrs (02:00,
  14:00 UTC).

Note: MRR tests should be reporting bi-directional link rate (or NIC
rate, if lower) if tested VPP configuration can handle the packet rate
higher than bi-directional link rate, e.g. large packet tests and/or
multi-core tests. In other words MRR = min(VPP rate, bi-dir link rate,
NIC rate).

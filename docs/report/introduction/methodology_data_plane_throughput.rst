Data Plane Throughput
---------------------

Network data plane packet and bandwidth throughput are measured in
accordance with :rfc:`2544`, using FD.io CSIT Multiple Loss Ratio search
(MLRsearch), an optimized throughput search algorithm, that measures
SUT/DUT packet throughput rates at different Packet Loss Ratio (PLR)
values.

Following MLRsearch values are measured across a range of L2 frame sizes
and reported:

- NON DROP RATE (NDR): packet and bandwidth throughput at PLR=0%.

  - **Aggregate packet rate**: NDR_LOWER <bi-directional packet rate>
    pps.
  - **Aggregate bandwidth rate**: NDR_LOWER <bi-directional bandwidth
    rate> Gbps.

- PARTIAL DROP RATE (PDR): packet and bandwidth throughput at PLR=0.5%.

  - **Aggregate packet rate**: PDR_LOWER <bi-directional packet rate>
    pps.
  - **Aggregate bandwidth rate**: PDR_LOWER <bi-directional bandwidth
    rate> Gbps.

NDR and PDR are measured for the following L2 frame sizes (untagged
Ethernet):

- IPv4 payload: 64B, IMIX (28x64B, 16x570B, 4x1518B), 1518B, 9000B.
- IPv6 payload: 78B, IMIX (28x78B, 16x570B, 4x1518B), 1518B, 9000B.

All rates are reported from external Traffic Generator perspective.

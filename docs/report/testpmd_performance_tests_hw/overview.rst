Overview
========

Tested Topologies HW
--------------------

CSIT Testpmd performance tests are executed on physical baremetal servers hosted
by LF FD.io project. Testbed physical topology is shown in the figure below.

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

Detailed LF FD.io test bed specification and topology is described in `CSIT LF
testbed wiki page <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

Testing Summary
---------------

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
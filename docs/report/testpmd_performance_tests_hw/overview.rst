Overview
========

Testpmd Performance Test Topologies
-----------------------------------

CSIT Testpmd performance tests are executed on physical baremetal servers hosted
by LF FD.io project. Testbed physical topology is shown in the figure below.::

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
two Intel XEON CPUs). SUTs run Testpmd SW application in Linux user-mode as a
Device Under Test (DUT). TG runs TRex SW application as a packet Traffic
Generator. Physical connectivity between SUTs and to TG is provided using
different NIC models that need to be tested for performance. Currently
installed and tested NIC models include:

#. 2port10GE X520-DA2 Intel.
#. 2port10GE X710 Intel.
#. 2port10GE VIC1227 Cisco.
#. 2port40GE VIC1385 Cisco.
#. 2port40GE XL710 Intel.

Detailed LF FD.io test bed specification and topology is described on `CSIT LF
testbed wiki page <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

Testpmd Performance Tests Overview
----------------------------------

Performance tests are split into two main categories:

- Throughput discovery - discovery of packet forwarding rate using binary search
  in accordance to RFC2544.

  - NDR - discovery of Non Drop Rate, zero packet loss.
  - PDR - discovery of Partial Drop Rate, with specified non-zero packet loss.

- Throughput verification - verification of packet forwarding rate against
  previously discovered throughput rate. These tests are currently done against
  0.9 of reference NDR, with reference rates updated periodically.

CSIT |release| includes following performance test suites:

- 2port10GE X520-DA2 Intel

  - **L2XC** - L2 Cross-Connect forwarding of untagged Ethernet frames.

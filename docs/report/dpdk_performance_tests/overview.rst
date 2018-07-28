Overview
========

For description of physical testbeds used for DPDK performance tests
please refer to :ref:`tested_physical_topologies`.

.. _tested_logical_topologies:

Logical Topologies
------------------

CSIT DPDK performance tests are executed on physical testbeds described
in :ref:`tested_physical_topologies`. Based on the packet path thru
server SUTs, three distinct logical topology types are used for DPDK DUT
data plane testing:

#. NIC-to-NIC switching topologies.

NIC-to-NIC Switching
~~~~~~~~~~~~~~~~~~~~

The simplest logical topology for software data plane application like
DPDK is NIC-to-NIC switching. Tested topologies for 2-Node and 3-Node
testbeds are shown in figures below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-2n-nic2nic}
            \label{fig:logical-2n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: logical-2n-nic2nic.svg
        :alt: logical-2n-nic2nic
        :align: center


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/vpp_performance_tests/logical-3n-nic2nic}
            \label{fig:logical-3n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: logical-3n-nic2nic.svg
        :alt: logical-3n-nic2nic
        :align: center

Server Systems Under Test (SUT) runs DPDK Testpmd/L3FWD application in
Linux user-mode as a Device Under Test (DUT). Server Traffic Generator (TG)
runs T-Rex application. Physical connectivity between SUTs and TG is provided
using different drivers and NIC models that need to be tested for performance
(packet/bandwidth throughput and latency).

From SUT and DUT perspectives, all performance tests involve forwarding
packets between two physical Ethernet ports (10GE, 25GE, 40GE, 100GE).
In most cases both physical ports on SUT are located on the same
NIC. The only exceptions are link bonding and 100GE tests. In the latter
case only one port per NIC can be driven at linerate due to PCIe Gen3
x16 slot bandwidth limiations. 100GE NICs are not supported in PCIe Gen3
x8 slots.

Note that reported DPDK DUT performance results are specific to the SUTs
tested. SUTs with other processors than the ones used in FD.io lab are
likely to yield different results. A good rule of thumb, that can be
applied to estimate DPDK packet thoughput for NIC-to-NIC switching
topology, is to expect the forwarding performance to be proportional to
processor core frequency for the same processor architecture, assuming
processor is the only limiting factor and all other SUT parameters are
equivalent to FD.io CSIT environment.

Performance Tests Coverage
--------------------------

Performance tests measure following metrics for tested DPDK DUT
topologies and configurations:

- Packet Throughput: measured in accordance with :rfc:`2544`, using
  FD.io CSIT Multiple Loss Ratio search (MLRsearch), an optimized binary
  search algorithm, producing throughput at different Packet Loss Ratio
  (PLR) values:

  - Non Drop Rate (NDR): packet throughput at PLR=0%.
  - Partial Drop Rate (PDR): packet throughput at PLR=0.5%.

- One-Way Packet Latency: measured at different offered packet loads:

  - 100% of discovered NDR throughput.
  - 100% of discovered PDR throughput.

- Maximum Receive Rate (MRR): measure packet forwarding rate under the
  maximum load offered by traffic generator over a set trial duration,
  regardless of packet loss. Maximum load for specified Ethernet frame
  size is set to the bi-directional link rate.

|csit-release| includes following performance test suites, listed per NIC type:

- **L2IntLoop** - L2 Interface Loop forwarding any Ethernet frames between
    two Interfaces.

- **IPv4 Routed Forwarding** - L3 IP forwarding of Ethernet frames between
    two Interfaces.

Execution of performance tests takes time, especially the throughput
tests. Due to limited HW testbed resources available within FD.io labs
hosted by :abbr:`LF (Linux Foundation)`, the number of tests for some
NIC models has been limited to few baseline tests.

Performance Tests Naming
------------------------

FD.io |csit-release| follows a common structured naming convention for
all performance and system functional tests, introduced in CSIT rls1701.

The naming should be intuitive for majority of the tests. Complete
description of FD.io CSIT test naming convention is provided on
:ref:`csit_test_naming`.

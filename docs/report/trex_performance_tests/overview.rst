Overview
========

TREX performance test results are reported for a range of processors.
For description of physical testbeds used for TREX performance tests
please refer to :ref:`tested_physical_topologies`.

Logical Topology
----------------

CSIT TREX performance tests are executed on physical testbeds described
in :ref:`tested_physical_topologies`. Logical topology use 1 nic that has
loopback connected ports. See figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/trex_performance_tests/}}
                \includegraphics[width=0.90\textwidth]{logical-TRex-nic2nic}
                \label{fig:logical-TRex-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: logical-TRex-nic2nic.svg
        :alt: logical-TRex-nic2nic
        :align: center


Performance Tests Coverage
--------------------------

Performance tests measure following metrics for tested TRex
topologies and configurations:

- Packet Throughput: measured in accordance with :rfc:`2544`, using
  FD.io CSIT Multiple Loss Ratio search (MLRsearch), an optimized binary
  search algorithm, producing throughput at different Packet Loss Ratio
  (PLR) values:

  - Non Drop Rate (NDR): packet throughput at PLR=0%.
  - Partial Drop Rate (PDR): packet throughput at PLR=0.5%.

- Two-way Packet Latency: measured both east-west and west-east at different
  offered packet loads:

  - 90% of discovered PDR throughput.
  - 50% of discovered PDR throughput.
  - 10% of discovered PDR throughput.
  - Minimal offered load.

|csit-release| includes following TRex data plane functionality
performance tested across a range of NIC drivers and NIC models:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| IPv4 Base             | IPv4 routing.                                |
+-----------------------+----------------------------------------------+
| IPv4 Scale            | IPv4 routing with 2M entries.                |
+-----------------------+----------------------------------------------+
| IPv6 Base             | IPv6 routing.                                |
+-----------------------+----------------------------------------------+
| IPv6 Scale            | IPv6 routing with 2M entries.                |
+-----------------------+----------------------------------------------+
| L2BD Scale            | L2 Bridge-Domain switching of untagged       |
|                       | Ethernet frames.                             |
+-----------------------+----------------------------------------------+


Performance Tests Naming
------------------------

FD.io |csit-release| follows a common structured naming convention for
all performance and system functional tests, introduced in CSIT-17.01.

The naming should be intuitive for majority of the tests. Complete
description of FD.io CSIT test naming convention is provided on
:ref:`csit_test_naming`.

Test Environment
================

Physical Testbeds
-----------------

FD.io CSIT performance tests are executed in physical testbeds hosted by
:abbr:`LF (Linux Foundation)` for FD.io project. Two physical testbed
topology types are used:

- **3-Node Topology**: Consists of two servers acting as SUTs
  (Systems Under Test) and one server as TG (Traffic Generator), all
  connected in ring topology.
- **2-Node Topology**: Consists of one server acting as SUTs and one
  server as TG both connected in ring topology.

Tested SUT servers are based on a range of processors, including Intel
Xeon Haswell-SP, Intel Xeon Skylake-SP, Arm, Intel Atom. More detailed
description is provided in
:ref:`tested_physical_topologies`. Tested logical topologies are
described in :ref:`tested_logical_topologies`.

Server Specifications
---------------------

Complete technical specifications of compute servers used in CSIT
physical testbeds are maintained in FD.io CSIT repository:
`FD.io CSIT testbeds - Xeon Skylake, Arm, Atom`_ and
`FD.io CSIT Testbeds - Xeon Haswell`_.

Pre-Test Server Calibration
---------------------------

Several SUT server sub-system runtime parameters have been identified
as impacting data plane performance tests. Calibrating those parameters
is part of FD.io CSIT pre-test activities, and includes measuring and
reporting following:

#. System level core jitter – measure duration of core interrupts by
   Linux in clock cycles and how often interrupts happen. Using
   `CPU core jitter tool <https://git.fd.io/pma_tools/tree/jitter>`_.

#. Memory bandwidth – measure bandwidth with `Intel MLC tool
   <https://software.intel.com/en-us/articles/intelr-memory-latency-checker>`_.

#. Memory latency – measure memory latency with Intel MLC tool.

#. Cache latency at all levels (L1, L2, and Last Level Cache) – measure
   cache latency with Intel MLC tool.

Measured values of listed parameters are especially important for
repeatable zero packet loss throughput measurements across multiple
system instances. Generally they come useful as a background data for
comparing data plane performance results across disparate servers.

Following sections include measured calibration data for Intel Xeon
Haswell and Intel Xeon Skylake testbeds.

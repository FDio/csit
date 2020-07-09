Test Environment
================

Physical Testbeds
-----------------

FD.io CSIT performance tests are executed in physical testbeds hosted by
:abbr:`LF (Linux Foundation)` for FD.io project. Two physical testbed
topology types are used:

- **3-Node Topology**: Consisting of two servers acting as SUTs
  (Systems Under Test) and one server as TG (Traffic Generator), all
  connected in ring topology.
- **2-Node Topology**: Consisting of one server acting as SUTs and one
  server as TG both connected in ring topology.

Tested SUT servers are based on a range of processors including Intel
Xeon Haswell-SP, Intel Xeon Skylake-SP, Intel Xeon Cascade Lake-SP, Arm, Intel
Atom. More detailed description is provided in
:ref:`tested_physical_topologies`. Tested logical topologies are
described in :ref:`tested_logical_topologies`.

Server Specifications
---------------------

Complete technical specifications of compute servers used in CSIT
physical testbeds are maintained in FD.io CSIT repository:
`FD.io CSIT testbeds - Xeon Cascade Lake`_,
`FD.io CSIT testbeds - Xeon Skylake, Arm, Atom`_ and
`FD.io CSIT Testbeds - Xeon Haswell`_.

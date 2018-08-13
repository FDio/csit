.. _test_environment:

Test Environment
================

FD.io CSIT performance tests are executed in physical testbeds hosted by
:abbr:`LF (Linux Foundation)` for FD.io project.

Two physical testbed topology types are used:

- **3-Node Topology**: Consisting of two servers acting as SUTs
  (Systems Under Test) and one server as TG (Traffic Generator), all
  connected in ring topology.
- **2-Node Topology**: Consisting of one server acting as SUTs and one
  server as TG both connected in ring topology.

Tested SUT servers are based on a range of processors including Intel
Xeon Haswell-SP, Intel Xeon Skylake-SP, Arm, Intel Atom. More detailed
description is provided in
:ref:`tested_physical_topologies`.

Tested logical topologies are described in
:ref:`tested_logical_topologies`.

SUT and TG HW Specifications
----------------------------

Complete technical specifications of compute servers used in CSIT
physical testbeds is maintained on FD.io wiki pages: `CSIT/Testbeds:
Xeon Hsw, VIRL
<https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Hsw,_VIRL.#FD.io_CSIT_testbeds_-_Xeon_Haswell.2C_VIRL>`_
and `CSIT Testbeds: Xeon Skx, Arm, Atom
<https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Skx,_Arm,_Atom.#Server_Specification>`_.

Test Environment
================

Environment Versioning
----------------------

In order to determine any benchmark anomalies (progressions,
regressions) between releases of a specific data-plane DUT application
(e.g. VPP, DPDK), the DUT needs to be tested in the same test
environment, to avoid test environment changes impacting the results and
clouding the picture.

In order to enable test system evolution, a mirror scheme is required to
determine benchmarking anomalies between releases of specific test
system like CSIT. This is achieved by testing the same DUT application
version between releases of CSIT test system.

CSIT test environment versioning scheme ensures integrity of all the
test system components, including their HW revisions, compiled SW code
versions and SW source code, within a specific CSIT version. Components
included in the CSIT environment versioning include:

- Server hosts hardware firmware and BIOS (motherboard, processsor,
  NIC(s), accelerator card(s)).
- Server host Linux operating system versions.
- Server host Linux configuration.
- TRex Traffic Generator version, drivers and configuration.
- CSIT framework code.

Following is the list of CSIT versions to date:

- Ver. 1 associated with CSIT rls1908 git branch as of 2019-08-21.
- Ver. 2 associated with CSIT rls2001 git branch as of 2020-03-27.
- Ver. 3 interim associated with master branch as of 2020-xx-xx.
- Ver. 4 associated with CSIT rls2005 git branch as of 2020-06-24.

To identify performance changes due to VPP code changes from v20.01.0 to
v20.05.0, both have been tested in CSIT environment ver. 4 and compared
against each other. All substantial progressions has been marked up with
RCA analysis. See Current vs Previous Release and Known Issues.

CSIT environment ver. 4 has been evaluated against the ver. 2 by
benchmarking VPP v20.01.0 in both environrment versions.

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
Xeon Haswell-SP, Intel Xeon Skylake-SP, Intel Xeon Cascade Lake-SP, Arm,
Intel Atom. More detailed description is provided in
:ref:`tested_physical_topologies`. Tested logical topologies are
described in :ref:`tested_logical_topologies`.

Server Specifications
---------------------

Complete technical specifications of compute servers used in CSIT
physical testbeds are maintained in FD.io CSIT repository:
`FD.io CSIT testbeds - Xeon Cascade Lake`_,
`FD.io CSIT testbeds - Xeon Skylake, Arm, Atom`_ and
`FD.io CSIT Testbeds - Xeon Haswell`_.

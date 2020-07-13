Test Environment
================

Environment Versioning
----------------------

CSIT test environment versioning has been introduced to track
modifications of the test environment.

Any benchmark anomalies (progressions, regressions) between releases of
a DUT application (e.g. VPP, DPDK), are determined by testing it in the
same test environment, to avoid test environment changes clouding the
picture.

A mirror approach is introduced to determine benchmarking anomalies due
to the test environment change. This is achieved by testing the same DUT
application version between releases of CSIT test system. This works
under the assumption that the behaviour of the DUT is deterministic
under the test conditions.

CSIT test environment versioning scheme ensures integrity of all the
test system components, including their HW revisions, compiled SW code
versions and SW source code, within a specific CSIT version. Components
included in the CSIT environment versioning include:

- **HW** Server hardware firmware and BIOS (motherboard, processsor,
  NIC(s), accelerator card(s)), tracked in CSIT branch in
  :file:`./docs/lab/<server_platform_name>_hw_bios_cfg.md`, e.g. `Xeon
  Skylake servers
  <https://git.fd.io/csit/tree/docs/lab/testbeds_sm_skx_hw_bios_cfg.md#n556>`_.
- **Linux** Server Linux OS version and configuration, tracked in CSIT
  Reports in `SUT Settings
  <https://docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_
  and `Pre-Test Server Calibration
  <https://docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html#pre-test-server-calibration>`_.
- **TRex** TRex Traffic Generator version, drivers and configuration
  tracked in `TG Settings
  <https://docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_.
- **CSIT** CSIT framework code tracked in CSIT release branches.

Following is the list of CSIT versions to date:

- Ver. 1 associated with CSIT rls1908 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls1908>`_, `Linux
  <https://docs.fd.io/csit/rls1908/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://docs.fd.io/csit/rls1908/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls1908>`_).
- Ver. 2 associated with CSIT rls2001 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2001>`_, `Linux
  <https://docs.fd.io/csit/rls2001/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://docs.fd.io/csit/rls2001/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2001>`_).
- Ver. 4 associated with CSIT rls2005 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2005>`_, `Linux
  <https://docs.fd.io/csit/rls2005/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://docs.fd.io/csit/rls2005/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2005>`_).

To identify performance changes due to VPP code development from
v20.01.0 to v20.05.0, both have been tested in CSIT environment ver. 4
and compared against each other. All substantial progressions and
regressions have been marked up with RCA analysis.
:ref:`vpp_throughput_comparisons` and :ref:`vpp_known_issues`.

CSIT environment ver. 4 has been evaluated against the ver. 2 by
benchmarking VPP v20.01.0 in both environment versions.

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

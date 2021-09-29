Test Environment
================

.. _test_environment_versioning:

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
- Ver. 5 associated with CSIT rls2009 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2009>`_, `Linux
  <https://docs.fd.io/csit/rls2009/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://docs.fd.io/csit/rls2009/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2009>`_).

  - The main change is TRex data-plane core resource adjustments:
    `increase from 7 to 8 cores and pinning cores to interfaces <https://gerrit.fd.io/r/c/csit/+/28184>`_
    for better TRex performance with symmetric traffic profiles.
- Ver. 6 associated with CSIT rls2101 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2101>`_, `Linux
  <https://docs.fd.io/csit/rls2101/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://docs.fd.io/csit/rls2101/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2101>`_).

  - The main change is TRex version upgrade:
    `increase from 2.82 to 2.86 <https://gerrit.fd.io/r/c/csit/+/29980>`_.
- Ver. 7 associated with CSIT rls2106 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2106>`_, `Linux
  <https://docs.fd.io/csit/rls2106/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://docs.fd.io/csit/rls2106/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2106>`_).

  - TRex version upgrade:
    `increase from 2.86 to 2.88 <https://gerrit.fd.io/r/c/csit/+/31652>`_.
  - Ubuntu upgrade:
    `upgrade from 18.04 LTS to 20.04.2 LTS <https://gerrit.fd.io/r/c/csit/+/31290>`_.

To identify performance changes due to VPP code development between previous
and current VPP release version, both have been tested in CSIT environment of
latest version and compared against each other. All substantial progressions and
regressions have been marked up with RCA analysis. See
:ref:`vpp_throughput_comparisons` and :ref:`vpp_known_issues`.

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
Intel Xeon Skylake-SP, Intel Xeon Cascade Lake-SP, Arm,
Intel Atom. More detailed description is provided in
:ref:`tested_physical_topologies`. Tested logical topologies are
described in :ref:`tested_logical_topologies`.

Server Specifications
---------------------

Complete technical specifications of compute servers used in CSIT
physical testbeds are maintained in FD.io CSIT repository:
`FD.io CSIT testbeds - Xeon Cascade Lake`_,
`FD.io CSIT testbeds - Xeon Skylake, Arm, Atom`_.

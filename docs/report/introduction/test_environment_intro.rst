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
To beter distinguish impact of test environment changes,
we also execute tests without any SUT (just with TRex TG sending packets
over a link looping back to TG).

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
  <https://s3-docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_
  and `Pre-Test Server Calibration
  <https://s3-docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html#id21>`_.
- **TRex** TRex Traffic Generator version, drivers and configuration
  tracked in `TG Settings
  <https://s3-docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_.
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
  <https://s3-docs.fd.io/csit/rls2106/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://s3-docs.fd.io/csit/rls2106/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2106>`_).

  - TRex version upgrade:
    `increase from 2.86 to 2.88 <https://gerrit.fd.io/r/c/csit/+/31652>`_.
  - Ubuntu upgrade:
    `upgrade from 18.04 LTS to 20.04.2 LTS <https://gerrit.fd.io/r/c/csit/+/31290>`_.
- Ver. 8 associated with CSIT rls2110 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2110>`_, `Linux
  <https://s3-docs.fd.io/csit/rls2110/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://s3-docs.fd.io/csit/rls2110/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2110>`_).

  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
- Ver. 9 associated with CSIT rls2202 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2202>`_, `Linux
  <https://s3-docs.fd.io/csit/rls2202/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://s3-docs.fd.io/csit/rls2202/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2202>`_).

  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
- Ver. 10 associated with CSIT rls2206 branch (`HW
  <https://git.fd.io/csit/tree/docs/lab?h=rls2206>`_, `Linux
  <https://s3-docs.fd.io/csit/rls2206/report/vpp_performance_tests/test_environment.html#sut-settings-linux>`_,
  `TRex
  <https://s3-docs.fd.io/csit/rls2206/report/vpp_performance_tests/test_environment.html#tg-settings-trex>`_,
  `CSIT <https://git.fd.io/csit/tree/?h=rls2206>`_).

  - Intel NIC 700/800 series firmware upgrade based on DPDK compatibility
    matrix.
  - Mellanox 556A series firmware upgrade based on DPDK compatibility
    matrix.
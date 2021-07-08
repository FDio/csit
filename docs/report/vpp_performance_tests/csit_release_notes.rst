.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - CSIT test environment is versioned, see
     :ref:`test_environment_versioning`.

   - **Upgrade to Ubuntu 20.04 LTS**: Reinstall base operating system to
       Ubuntu 20.04.2 LTS. Upgrade includes also baseline Docker
       containers used for spawning topology.

   - Initial test data for Intel Xeon Ice Lake platforms. Current
     CSIT-2106 report data for Intel Xeon Ice Lake comes from an
     external source (Intel labs running CSIT code on 8360Y D Stepping
     and 6338N processors). For detail about the physical setup
     see :ref:`tested_physical_topologies`. Tested VPP and CSIT
     versions are pre-release, VPP 21.06-rc0~779-gd640ae52f.

   - **AF_XDP**: Added af_xdp driver testing for all testcases.

   - **GTPU tunnel**: Added GTPU HW Offload IPv4 routing tests.

   - **Telemetry retouch**: Redesign telemetry retrieval from DUT.
       Include VPP perfmon plugin telemetry.

#. TEST FRAMEWORK

   - **CSIT PAPI support**: Due to issues with PAPI performance, VAT is
     still used in CSIT for all VPP scale tests. See known issues below.

   - **General Code Housekeeping**: Ongoing code optimizations,
     speed ups and bug fixes.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs improvements**: Updated Packet Latency graphs,
     see :ref:`latency_methodology`.

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

List of known issues in |csit-release| for VPP performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1782                              | Multicore AVF tests are failing when trying to create interface.                                          |
|    | <https://jira.fd.io/browse/CSIT-1782>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1763                              | Adapt ramp-up phase of nat44 tests for different frame sizes.                                             |
|    | <https://jira.fd.io/browse/CSIT-1763>`_ | Currently ramp-up phase rate and duration values are correctly set for tests with 64B frame size.         |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1671                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1671>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+ The usual PAPI library spends too much time parsing arguments, so even with async processing (hundreds of |
|    | `VPP-1763                               | commands in flight over socket), the VPP configuration for large scale tests (millions of messages) takes |
|    | <https://jira.fd.io/browse/VPP-1763>`_  | too long.                                                                                                 |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `VPP-1972                               | One VPP change has decreased performance of NAT44ed processing, both slow path and fast path.             |
|    | <https://jira.fd.io/browse/VPP-1972>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

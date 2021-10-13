.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Intel Xeon Ice Lake**: Added initial test data for these
     platforms. Current CSIT-2106 report data for Intel Xeon Ice Lake
     comes from an external source (Intel labs running CSIT code on
     "8360Y D Stepping" and "6338N" processors). For details about the
     physical setup see :ref:`tested_physical_topologies`. Tested
     VPP and CSIT versions are pre-release, VPP
     21.06-rc0~779-gd640ae52f.

   - **MLRsearch improvements**: Added support for multiple packet
     throughput rates in a single search, each rate is associated
     with a distinct Packet Loss Ratio (PLR) criterion. Previously
     only Non Drop Rate (NDR) (PLR=0) and single Partial Drop Rate
     (PDR) (PLR<0.5%) were supported. Implemented number of
     optimizations improving rate discovery efficiency.

   - **Reduction of tests**: Removed obsolete VPP use cases and
     superfluous test combinations from continuous and report test
     executions, including:

     - All vts tests, obsolete use cases.
     - dot1q tests apart from dot1q-l2bd, superfluous combinations.
     - -100flows, -100kflows in all acl tests.
     - nat44 tests

       - -pps tests, replaced by -tput tests.
       - h1-p1-s1 single session tests, unessential combination.
       - h4096-p63-s258048 tests, unessential scale combination.

     - ipsec tests

       - ethip4ipsectptlispgpe.
       - policy-aes128gcm.
       - policy-aes128cbc-hmac256sha.
       - policy-aes128cbc-hmac512sha.
       - int-aes128cbc-hmac256sha.
       - scale of

         - 400tnlsw.
         - 5000tnlsw.
         - 20000tnlsw.
         - 60000tnlsw.

#. TEST FRAMEWORK

   - **CSIT test environment** version has been updated to ver. 8, see
     :ref:`test_environment_versioning`.

   - **CSIT in AWS environment**: Added CSIT support for AWS c5n
     instances environment.

   - **CSIT PAPI support**: Due to issues with PAPI performance, VAT is
     still used in CSIT for all VPP scale tests. See known issues
     below.

   - **General Code Housekeeping**: Ongoing code optimizations and bug
     fixes.

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
|  4 | `CSIT-1789                              | AVF driver does not perform RSS in a deterministic way.                                                   |
|    | <https://jira.fd.io/browse/CSIT-1789>`_ | This increases standard deviation of tests with small number of flows (mainly ipsec).                     |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1790                              | Broken TRex latency measurements with TRex v2.88, DPDK 21.02 and FVL FW 6.01.                             |
|    | <https://jira.fd.io/browse/CSIT-1790>`_ | High latency O(5msec) for all VPP and testpmd/l3fwd test cases for FVL NICs with FW 6.01.                 |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1780                              | IPSEC SW async scheduler MRR tests failing with no traffic forwarded.                                     |
|    | <https://jira.fd.io/browse/CSIT-1780>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  7 | `CSIT-1786                              | IP4 and IP6 scale tests failing with no traffic forwarded.                                                |
|    | <https://jira.fd.io/browse/CSIT-1786>`_ | Issue reported to VPP devs.                                                                               |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  8 | `CSIT-1785                              | NAT44ED tests failing to establish all TCP sessions.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1785>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  9 | `CSIT-1791                              | Performance regression in RDMA tests, due to CSIT environment changes.                                    |
|    | <https://jira.fd.io/browse/CSIT-1791>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

Root Cause Analysis for Performance Changes
-------------------------------------------

List of RCAs in |csit-release| for VPP performance changes:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `VPP-1972                               | One VPP change has decreased performance of NAT44ed processing, mostly slow path.                         |
|    | <https://jira.fd.io/browse/VPP-1972>`_  |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

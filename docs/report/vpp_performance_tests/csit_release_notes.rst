.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

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

   - **Telemetry retouch**: Refactored telemetry retrieval from DUTs and
     SUTs. Included VPP perfmon plugin telemetry with all perfmon
     bundles available in VPP release.

   - **Upgrade to Ubuntu 20.04 LTS**: Re-installed base operating system
     to Ubuntu 20.04.2 LTS. Upgrade included also baseline Docker
     containers used for spawning topology.

   - **TRex upgrade v2.86 to v2.88**: Included move to DPDK 21.02 and
     changed the way egress low latency queues are used in FVL NICs.
     This broke latency measurements for majority of FVL NICs in
     CSIT. Latency values look better after upgrading FVL FW on TRex
     servers, but still somewhat higher than before the TRex upgrade.
     Tracked by `CSIT-1790 <https://jira.fd.io/browse/CSIT-1790>`_.

   - **CSIT test environment** version has been updated to ver. 7, see
     :ref:`test_environment_versioning`.

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
|  1 | `CSIT-1763                              | Adapt ramp-up phase of nat44 tests for different frame sizes.                                             |
|    | <https://jira.fd.io/browse/CSIT-1763>`_ | Currently ramp-up phase rate and duration values are correctly set for tests with 64B frame size.         |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1671                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1671>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+ The usual PAPI library spends too much time parsing arguments, so even with async processing (hundreds of |
|    | `VPP-1763                               | commands in flight over socket), the VPP configuration for large scale tests (millions of messages) takes |
|    | <https://jira.fd.io/browse/VPP-1763>`_  | too long.                                                                                                 |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1790                              | Broken TRex latency measurements with TRex v2.88, DPDK 21.02 and FVL FW 6.01.                             |
|    | <https://jira.fd.io/browse/CSIT-1790>`_ | High latency (5msec) for all VPP and testpmd/l3fwd test cases for FVL NICs with FW 6.01.                  |
|    |                                         | This issue does not affect the reported results since we upgraded firmware version on TG NICs.            |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1789                              | AVF driver does not perform RSS in a deterministic way.                                                   |
|    | <https://jira.fd.io/browse/CSIT-1789>`_ | This increases standard deviation of tests with small number of flows (mainly ipsec).                     |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1780                              | IPSEC SW async scheduler MRR tests failing with no traffic forwarded.                                     |
|    | <https://jira.fd.io/browse/CSIT-1780>`_ |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  6 | `CSIT-1785                              | NAT44ED tests failing to establish all TCP sessions.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1785>`_ |                                                                                                           |
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

.. _vpp_performance_tests_release_notes:

Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Intel Xeon Ice Lake**: Added test data for these platforms. Current
     CSIT-2110 report data for Intel Xeon Ice Lake comes from an external source
     (Intel labs running CSIT code on "8360Y D Stepping" and "6338N"
     processors). For details about the physical setup see
     :ref:`tested_physical_topologies`.

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
|    | <https://jira.fd.io/browse/CSIT-1782>`_ | Frequency is reduced by s CSIT workaround, but occasional failures do still happen.                       |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  2 | `CSIT-1671                              | All CSIT scale tests can not use PAPI due to much slower performance compared to VAT/CLI (it takes much   |
|    | <https://jira.fd.io/browse/CSIT-1671>`_ | longer to program VPP). This needs to be addressed on the PAPI side.                                      |
|    +-----------------------------------------+ Currently, the time critical code uses VAT running large files with exec statements and CLI commands.     |
|    | `VPP-1763                               | Still, we needed to reduce the number of scale tests run to keep overall duration reasonable.             |
|    | <https://jira.fd.io/browse/VPP-1763>`_  | More improvements needed to achieve sufficient configuration speed.                                       |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  3 | `CSIT-1780                              | IPSEC SW async scheduler MRR tests failing with no traffic forwarded.                                     |
|    | <https://jira.fd.io/browse/CSIT-1780>`_ | VPP code is not behaving correcty when crypo workers are the bottleneck.                                  |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  4 | `CSIT-1785                              | NAT44ED tests failing to establish all TCP sessions.                                                      |
|    | <https://jira.fd.io/browse/CSIT-1785>`_ | We removed the max scale NAT tests to avoid this issue.                                                   |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
|  5 | `CSIT-1791                              | Performance regression in RDMA tests, due to CSIT environment changes.                                    |
|    | <https://jira.fd.io/browse/CSIT-1791>`_ | Two symptoms: 1. 10-20% regression across most tests. 2. DUT performance cap just below 38 Mpps.          |
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

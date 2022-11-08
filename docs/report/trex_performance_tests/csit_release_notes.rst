Release Notes
=============

Changes in |csit-release|
-------------------------

#. TREX PERFORMANCE TESTS

   - **Intel Ice Lake**: Added tests for testing latency between 2 ports on
     Intel-E810Cq on the TRex. Used 2n-icx test bed. Added tests:

     - IP4Base
     - IP4scale2m
     - IP6Base
     - IP6scale2m
     - L2bscale1mmaclrn

   - **Amazon 1n-aws**: Added tests for testing latency between 2 ports on
     Amazon Nitro 50G on the TRex. Added tests:

     - IP4Base
     - IP4scale2m
     - IP6Base
     - IP6scale2m

#. TEST FRAMEWORK

   - **CSIT test environment** version has been updated to ver. 11, see
     :ref:`test_environment_versioning`.

.. _trex_known_issues:

Known Issues
------------

List of known issues in |csit-release| for TRex performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|  1 | `CSIT-1876                              | 1n-aws: TRex NDR PDR ALL IP4 scale and L2 scale tests failing with 50% packet loss.                       |
|    | <https://jira.fd.io/browse/CSIT-1876>`_ | CSIT removed ip4scale and l2scale except ip4scale2m where it's still failing.                             |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

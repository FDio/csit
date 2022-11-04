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


#. TRex RELEASE VERSION
   - **TRex version used: 3.00**

.. _trex_known_issues:

Known Issues
------------

List of known issues in |csit-release| for TRex performance tests:

+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                         |
+====+=========================================+===========================================================================================================+
|    |                                         |                                                                                                           |
+----+-----------------------------------------+-----------------------------------------------------------------------------------------------------------+

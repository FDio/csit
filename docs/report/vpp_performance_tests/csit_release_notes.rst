Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **Service density 2n-skx tests**: Added higher density tests with dtc=0.5
     (2 NF each with 1 DT per physical core) with VPP as a VNF payload.

   - **Experimental Soak Tests**: Added performamce soak tests framework
     code for extended time duration tests and throughput discovery
     at given PLR and at give total test time e.g. minutes, hours,
     days, weeks, months, years. See updated
     :ref:`test_methodology` section for more details.

#. TEST FRAMEWORK

   - **Qemu code refactor**: Complete code refactor of the key components
     QemuUtil.py and QemuManager.py (L1 and L2 KW counterparts). Added
     implementation of kernel-image-kvm based VM alongisde the previously used
     NestedVM images. Added ability to run VPP as a payload in VNF.

   - **CSIT PAPI Support**: Continue converting existing VAT L1 keywords to
     PAPI L1 KWs in CSIT using VPP Python bindings. Required for migrating away
     from VAT. Redesign of key components of PAPI Executor and PAPI history.

   - **General Code Housekeeping**: Ongoing RF keywords optimizations,
     removal of redundant RF keywords.

   - **Test suite generator**: Extend the test suite generator for ability to
     generate NIC permutation and search algorithm permutations from base
     suites.

   - **TOX verification**: Added verifications for test suite generator.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs Layout Improvements**: Improved performance graphs layout
     for better readibility and maintenance: test grouping, axis
     labels, descriptions, other informative decoration.

#. MISCELLANEOUS

   - **2n-dnv Tests (3rd Party)**: Published performance tests for 2n-
     dnv (2-Node Atom Denverton) from 3rd party testbeds running FD.io
     |csit-release| automated testing code.
     Only graphs for Packet Throughput and Speedup Multi-core and not
     for Packet Latency were published as there are no results for Packet
     Latency available.

.. raw:: latex

    \clearpage

.. _vpp_known_issues:

Known Issues
------------

List of known issues in |csit-release| for VPP performance tests:

+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| #  | JiraID                                  | Issue Description                                                                                                               |
+====+=========================================+=================================================================================================================================+
| 1  | `CSIT-570                               | Sporadic (1 in 200) NDR discovery test failures on x520. DPDK reporting rx-errors, indicating L1 issue.                         |
|    | <https://jira.fd.io/browse/CSIT-570>`_  | Suspected issue with HW combination of X710-X520 in LF testbeds. Not observed outside of LF testbeds.                           |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 2  | `CSIT-????                              | IPSecHW interface AES-GBC tests failing due to traffic not passing.                                                             |
|    | <https://jira.fd.io/browse/CSIT-????>`_ |                                                                                                                                 |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+

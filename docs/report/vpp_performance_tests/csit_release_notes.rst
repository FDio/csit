Release Notes
=============

Changes in |csit-release|
-------------------------

#. VPP PERFORMANCE TESTS

   - **BMRR Throughput**: MRR (Maximum Receive Rate) test code has been
     updated with a configurable burst MRR parameters: trial duration
     and number of trials in a single burst. Enables a new Burst MRR
     (BMRR for short) methodology for more precise performance
     trending. See updated :ref:`performance_test_methodology` section
     for more details.

   - **2n-skx tests**: Added performamce tests for 2n-skx (2-Node Xeon
     Skylake) testbeds: focus on baseline and scale tests, including
     VM vhost and Container memif tests.

   - **3n-skx tests**: Added performamce tests for 3n-skx (3-Node Xeon
     Skylake) testbeds: VM vhost and Container memif tests.

   - **VXLAN Scale Tests**: Added performamce tests for VXLAN scale with
     dot1q and VPP L2BD.

   - **AVF Driver Tests**: Added performamce tests for i40e AVF driver
     on VPP, no DPDK required.

   - **QAT**: Fixed reoccuring issues with QAT crypto accelerator cards.

   - **VM Vhost Virtio Params Combinations**: Added performance tests
     for VM vhost with different virtio parameters combinations:
     indirect buffers, mergeable buffers.

   - **K8s/Ligato in Trending**: Added K8s/Ligato Container memif tests
     to daily trending.

#. TEST FRAMEWORK

   - **Experimental Soak Tests**: Added performamce soak tests framework
     code for extended time duration tests and  throughput discovery
     at given PLR and at give total test time e.g. minutes, hours,
     days, weeks, months, years. See updated
     :ref:`performance_test_methodology` section for more details.

   - **Trending Tests BMRR**: Used new Burst MRR (BMRR) tests for daily
     trending.

   - **Per VPP Patch Performance Checks**: Per VPP gerrit patch vs.
     parent performance tests, anomaly detection and no verify voting
     (-1/0/+1) yet. Manual trigger only. Not "marketed" to FD.io
     community yet to avoid excessive LFN FD.io physical performance
     testbed blocking.

   - **Patch-on-Patch Infra**: Added capability to run performance tests
     using CSIT gerrit patch code testing VPP gerrit patch code, i.e.
     before any VPP and/or CSIT code is merged into git branch.

   - **CSIT PAPI Support**: Initial implementation of PAPI L1 KWs in
     CSIT using VPP Python bindings. Required for migraing away from
     VAT. Very few L1 KWs implemented ("show version", "show
     interfaces").

   - **General Code Housekeeping**: Ongoing RF keywords optimizations,
     removal of redundant RF keywords.

#. PRESENTATION AND ANALYTICS LAYER

   - **Graphs Layout Improvements**: Improved performance graphs layout
     for better readibility and maintenance: test grouping, axis
     labels, descriptions, other informative decoration. Master report
     generated. 744 graphs(!)


   - **Performance Trending**: Further improvements of continuous
     performance trending, anomaly detection and analysis.

#. MISCELLANEOUS

   - **3n-dnv Tests (3rd Party)**: Published performance tests for 3n-
     dnv (3-Node Atom Denverton) from 3rd party testbeds running FD.io
     |csit-release| automated testing code.

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
| 2  | `CSIT-1234                              | VPP IPSecHW scale interface mode 1core, low NDR and PDR 64B throughput in 3n-hsw testbeds, in CSIT-18.07 vs. CSIT-18.04.        |
|    | <https://jira.fd.io/browse/CSIT-1234>`_ | ip4ipsecscale1000tnl-ip4base-int 1core CSIT-18.07/18.04 relative change: NDR -31%, PDR -32%, MRR -38%.                          |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 3  | `CSIT-1242                              | VPP xl710 ip4base test 1core, low NDR and PDR 64B throughput in 3n-hsw testbeds, in CSIT-18.07 vs. CSIT-18.04.                  |
|    | <https://jira.fd.io/browse/CSIT-1242>`_ | xl710 ip4base 1core CSIT-18.07/18.04 relative change: NDR -29%, high stdev.                                                     |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 4  | `CSIT-1243                              | VPP nat44 base test 2core, low NDR and PDR 64B throughput in 3n-skx testbeds, compared to 3n-hsw testbeds.                      |
|    | <https://jira.fd.io/browse/CSIT-1243>`_ | ip4base-nat44 2core 3n-skx/3n-hsw relative change: NDR -19%, PDR -22%.                                                          |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| 5  | `CSIT-1246                              | Ligato K8S orchestrated tests are failing due to incompatibility of the latest released Ligato vpp-agent with VPP-18.07.        |
|    | <https://jira.fd.io/browse/CSIT-1246>`_ | Past vpp-agent releases are not compatible either.                                                                              |
+----+-----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+


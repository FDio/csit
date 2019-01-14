Report History
==============

FD.io CSIT-1810 Report history and per .[ww] revision changes are listed below.

+----------------+----------------------------------------------------------------+
| .[ww] Revision | Changes                                                        |
+================+================================================================+
| .03            | 1. Split the VPP throughput :ref:`_vpp_throughput_comparisons` |
|                |    tables per number of cores.                                 |
|                | 2. Add 20k and 200k scale tests to VPP                         |
|                |    :ref:`VPP_Packet_Throughput`.                               |
|                |                                                                |
+----------------+----------------------------------------------------------------+
| .49            | 1. Split pages with graphs.                                    |
|                |                                                                |
+----------------+----------------------------------------------------------------+
| .48            | 1. Added configurations for Denverton:                         |
|                |                                                                |
|                |    a. Packet throughput :ref:`vpp_perf_configurations_2n_dnv`  |
|                |    b. MRR :ref:`vpp_mrr_configurations_2n_dnv`                 |
|                |                                                                |
|                | 2. Added operational data for Denverton:                       |
|                |                                                                |
|                |    a. Packet throughput :ref:`vpp_perf_operational_2n_dnv`     |
|                |                                                                |
|                | 3. Added graphs for Denverton:                                 |
|                |                                                                |
|                |    a. Packet Throughput - L2 Switching -                       |
|                |       :ref:`packet_throughput_graphs_l2sw-2n-dnv-x553`         |
|                |    b. Packet Throughput - IPv4 Routing -                       |
|                |       :ref:`packet_throughput_graphs_ip4-2n-dnv-x553`          |
|                |    c. Packet Throughput - IPv6 Routing -                       |
|                |       :ref:`packet_throughput_graphs_ip6-2n-dnv-x553`          |
|                |    d. Speedup Multi-Core - L2 Switching -                      |
|                |       :ref:`speedup_graphs_l2sw-2n-dnv-x553`                   |
|                |    e. Speedup Multi-Core - IPv4 Routing -                      |
|                |       :ref:`speedup_graphs_ip4-2n-dnv-x553`                    |
|                |    f. Speedup Multi-Core - IPv6 Routing -                      |
|                |       :ref:`speedup_graphs_ip6-2n-dnv-x553`                    |
|                |                                                                |
|                | 4. Replaced Denverton data from revision .47 with the data     |
|                |    provided by Intel for revision .48.                         |
|                |                                                                |
|                | 5. Changed revision format of the document, see description at |
|                |    the bottom of this page.                                    |
|                |                                                                |
+----------------+----------------------------------------------------------------+
| .47            | 1. Added automated wrapping of long test names in graphs.      |
|                | 2. Changed data and time format in the header.                 |
|                | 3. Changed versioning.                                         |
|                | 4. Added more test runs:                                       |
|                |                                                                |
|                |    a. HoneyComb Functional.                                    |
|                |    b. VPP on 3n-hsw testbed.                                   |
|                |                                                                |
|                | 5. Added 3n-skx and 2n-skx comparisons to Report:              |
|                |                                                                |
|                |    a. VPP Performance Tests:                                   |
|                |       :ref:`vpp_compare_current_vs_previous_release`           |
|                |    b. DPDK Performance Tests:                                  |
|                |       :ref:`dpdk_compare_current_vs_previous_release`          |
|                |                                                                |
|                | 6. Changed title of this chapter to "Document History"         |
|                | 7. Added comparisons between topologies:                       |
|                |                                                                |
|                |    a. VPP: :ref:`vpp_compare_topologies_3n-Skx_vs_2n-Skx`      |
|                |    b. DPDK: :ref:`dpdk_compare_topologies_3n-Skx_vs_2n-Skx`    |
|                |                                                                |
|                | 8. Added results for Denverton:                                |
|                |                                                                |
|                |    a. Packet throughput :ref:`vpp_performance_results_2n_dnv`  |
|                |    b. MRR :ref:`vpp_mrr_results_2n_dnv`                        |
|                |                                                                |
|                | 9. Added the chapter "2-Node Atom Denverton (2n-dnv)" to       |
|                |    :ref:`tested_physical_topologies`                           |
|                |                                                                |
|                | 10. Added the chapter "Calibration Data - Denverton" to        |
|                |     :ref:`vpp_test_environment`                                |
|                |                                                                |
+----------------+----------------------------------------------------------------+
| .46            | 1. dot1q KVM VMs vhost-user tests added to                     |
|                |    :ref:`KVM_VMs_vhost`.                                       |
|                |                                                                |
|                | 2. Added number of test runs used to generate data for all     |
|                |    graphs                                                      |
|                |                                                                |
|                |    a. :ref:`VPP_Packet_Throughput`                             |
|                |    b. :ref:`throughput_speedup_multi_core`                     |
|                |    c. :ref:`VPP_Packet_Latency`                                |
|                |                                                                |
|                | 3. Added more test runs:                                       |
|                |                                                                |
|                |    a. K8s Container Memif,                                     |
|                |    b. VPP on 3n-hsw testbed.                                   |
|                |                                                                |
+----------------+----------------------------------------------------------------+
| .45            | Initial version                                                |
+----------------+----------------------------------------------------------------+

FD.io CSIT Reports follow CSIT-[yy][mm].[ww] numbering format, with version
denoted by concatenation of two digit year [yy] and two digit month [mm], and
maintenance revision identified by two digit calendar week number [ww].

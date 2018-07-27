Release Notes
=============

Changes in |csit-release|
-------------------------

No code changes apart from bug fixes.

Known Issues
------------

Here is the list of known issues in |csit-release| for Testpmd performance tests:

+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                             | Jira ID    | Description                                                     |
+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | Testpmd in 1t1c and 2t2c setups - large variation | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across        |            | throughput. Applies to XL710 and X710 NICs, no issues observed  |
|   | multiple test runs with xl710 and x710 NICs.      |            | on x520 NICs.                                                   |
+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | Lower than expected NDR throughput with xl710     | CSIT-571   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | and x710 NICs, compared to x520 NICs.             |            | throughput. Applies to XL710 and X710 NICs.                     |
+---+---------------------------------------------------+------------+-----------------------------------------------------------------+

CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added Testpmd tests

    - new NICs - 2p40GE Intel xl710, 2p10GE Intel x710

Known Issues
------------

Here is the list of known issues in CSIT |release| for Testpmd performance tests:

+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                             | Jira ID    | Description                                                     |
+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | Testpmd in 1t1c and 2t2c setups - large variation | CSIT-568   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across        |            | throughput. Applies to XL710 and X710 NICs, x520 NICs are fine. |
|   | multiple test runs with xl710 and x710 NICs.      |            |                                                                 |
+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | Lower than expected NDR throughput with xl710     | CSIT-?     | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | and x710 NICs, compared to x520 NICs.             |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+---------------------------------------------------+------------+-----------------------------------------------------------------+
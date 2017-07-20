CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added Honeycomb functional tests for the following features:

   - Policer

#. Improved test coverage for the following features:

   - Interface Management
   - Vlan
   - Port Mirroring

Known Issues
------------

Here is the list of known issues in CSIT |release| for Honeycomb functional
tests in VIRL:

+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| # | Issue                                      | Jira ID    | Description                                                                |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 1 | IP address subnet validation               | VPP-649    | When configuring two IP addresses from the same subnet on an interface,    |
|   |                                            |            | VPP refuses the configuration but returns code 200:OK. This can cause      |
|   |                                            |            | desync between Honeycomb's config and operational data.                    |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 2 | Removal of ACP-plugin interface assignment | HC2VPP-173 | Attempting to remove all ACLs from an interface responds with OK but does  |
|   |                                            |            | not remove the assignments.                                                |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 3 | VxLAN GPE configuration crashes VPP        | VPP-875    | Specific VxLAN GPE configurations cause VPP to crash and restart.          |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 4 | Policer traffic test failure               | CSIT-      | Traffic test has begun to fail, likely due to VPP changes. There is  more  |
|   |                                            |            | information available yet.                                                 |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 5 | SPAN traffic test failure                  | CSIT-      | Traffic test has begun to fail, likely due to VPP changes. There is  more  |
|   |                                            |            | information available yet.                                                 |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 6 | Unnumbered interface VIRL issue            | CSIT-      | CRUD for unnumbered interface appears to fail in VIRL, but not in local    |
|   |                                            |            | test runs. Investigation pending.                                          |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+

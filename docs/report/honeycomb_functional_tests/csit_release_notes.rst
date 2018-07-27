Release Notes
=============

Changes in |csit-release|
-------------------------

No changes.

Known Issues
------------

Here is the list of known issues in |csit-release| for Honeycomb functional
tests in VIRL:

+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+
| # | Issue                                      | Jira ID       | Description                                                             |
+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+
| 1 | IPv6 BGP route configuration               | HONEYCOMB-403 | Configuring Ipv6 route results in missing writer                        |
|   |                                            |               | for IPv6Route and IPv6NextHop exception.                                |
+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+
| 2 | IP address subnet validation               | VPP-649       | When configuring two IP addresses from the same subnet on an interface, |
|   |                                            |               | VPP refuses the configuration but returns code 200:OK. This can cause   |
|   |                                            |               | desync between Honeycomb's config and operational data.                 |
+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+
| 3 | VxLAN GPE configuration crashes VPP        | VPP-875       | Specific VxLAN GPE configurations cause VPP to crash and restart.       |
+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+
| 4 | Operational data for IPv6 special routes   | HC2VPP-254    | Special hop routes are misidentified as regular routes                  |
|   |                                            |               | in operational data.                                                    |
+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+
| 5 | LISP PITR feature configuration            | HC2VPP-263    | Locator set reference in operational data is incorrect.                 |
+---+--------------------------------------------+---------------+-------------------------------------------------------------------------+

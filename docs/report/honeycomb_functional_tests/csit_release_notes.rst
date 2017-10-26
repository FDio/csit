CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added Honeycomb functional tests for the following areas:

   - LISP GPE
   - Honeycomb northbound interfaces over IPv6
   - Honeycomb implementation of ODL BGP

#. Improved test coverage for the following features:

   - Vlan sub-interfaces

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
| 2 | VxLAN GPE configuration crashes VPP        | VPP-875    | Specific VxLAN GPE configurations cause VPP to crash and restart.          |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 3 | Operational data for IPv6 special routes   | HC2VPP-228 | Special hop routes are misidentified as regular routes in operational data.|
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+

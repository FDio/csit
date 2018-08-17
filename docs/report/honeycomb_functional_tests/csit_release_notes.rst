Release Notes
=============

Changes in |csit-release|
-------------------------

No changes.

Known Issues
------------

Here is the list of known issues in |csit-release| for Honeycomb functional
tests in VIRL:

+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| # | JiraID                                       | Issue Description                                                                                      |
+===+==============================================+========================================================================================================+
| 1 | `HONEYCOMB-403                               | IPv6 BGP route configuration.                                                                          |
|   | <https://jira.fd.io/browse/HONEYCOMB-403>`_  | Configuring IPv6 route results in missing writer for IPv6Route and IPv6NextHop exception.              |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 2 | `VPP-649                                     | When configuring two IP addresses from the same subnet on an interface, VPP refuses the configuration, |
|   | <https://jira.fd.io/browse/VPP-649>`_        | but returns code 200:OK. This can cause desync between Honeycomb's config and operational data.        |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 3 | `VPP-875                                     | VxLAN GPE configuration crashes VPP.                                                                   |
|   | <https://jira.fd.io/browse/VPP-875>`_        | Specific VxLAN GPE configurations cause VPP to crash and restart.                                      |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 4 | `HC2VPP-254                                  | Operational data for IPv6 special routes.                                                              |
|   | <https://jira.fd.io/browse/HC2VPP-254>`_     | Special hop routes are misidentified as regular routes  in operational data.                           |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 5 | `HC2VPP-263                                  | LISP PITR feature configuration.                                                                       |
|   | <https://jira.fd.io/browse/HC2VPP-263>`_     | Locator set reference in operational data is incorrect.                                                |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 6 | `CSIT-1210                                   | Unnumbered interface configuration.                                                                    |
|   | <https://jira.fd.io/browse/CSIT-1210>`_      | VPP does not send IP addresses for unnumbered interfaces anymore. HC CSIT tests were relying on that.  |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+

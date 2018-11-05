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
| 1 | `VPP-649                                     | When configuring two IP addresses from the same subnet on an interface, VPP refuses the configuration, |
|   | <https://jira.fd.io/browse/VPP-649>`_        | but returns code 200:OK. This can cause desync between Honeycomb's config and operational data.        |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 2 | `HC2VPP-263                                  | LISP PITR feature configuration.                                                                       |
|   | <https://jira.fd.io/browse/HC2VPP-263>`_     | Locator set reference in operational data is incorrect.                                                |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
| 3 | `CSIT-1210                                   | Unnumbered interface configuration.                                                                    |
|   | <https://jira.fd.io/browse/CSIT-1210>`_      | VPP does not send IP addresses for unnumbered interfaces anymore. HC CSIT tests were relying on that.  |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+
|   |                                              |                                                                                                        |
+---+----------------------------------------------+--------------------------------------------------------------------------------------------------------+

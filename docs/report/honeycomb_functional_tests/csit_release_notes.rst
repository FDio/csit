CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Naming change for all Honeycomb functional test suites in VIRL

    - Honeycomb functional test case names stayed unchanged

#. Added Honeycomb functional tests

    - NSH_SFC
    - LISP
    - NAT
    - SPAN

Known Issues
------------

Here is the list of known issues in CSIT |release| for Honeycomb functional
tests in VIRL:

+---+-------------------------------------------------+-----------------------------------------------------------------+
| # | Issue                                           | Description                                                     |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 1 | Operational data for Vhost-user interfaces      | Honeycomb Operational data reports Vhost-user interfaces        |
|   | "server" flag                                   | as client, even if they are server.                             |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 2 | Persistence of VxLAN tunnels                    | Configuration persistence often fails to restore                |
|   |                                                 | Honeycomb's internal naming context for VxLAN interfaces.       |
|   |                                                 | The interface is renamed to "vxlan_tunnel0" but is otherwise    |
|   |                                                 | configured correctly.                                           |
+---+-------------------------------------------------+-----------------------------------------------------------------+


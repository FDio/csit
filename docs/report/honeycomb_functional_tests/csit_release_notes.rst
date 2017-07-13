CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Added Honeycomb functional tests

   - ACL plugin
   - Routing
   - SLAAC
   - Proxy ARP
   - DHCP Relay
   - Neighbor Discovery Proxy

#. Changed execution environment from Ubuntu14.04 to Ubuntu16.04

Known Issues
------------

Here is the list of known issues in CSIT |release| for Honeycomb functional
tests in VIRL:

+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| # | Issue                                      | Jira ID    | Description                                                                |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 1 | IP address subnet validation               | VPP-649    | When configuring two IP addresses from the same subnet on an interface,    |
|   |                                            |            | VPP refuses the configuration but returns OK. This can cause desync        |
|   |                                            |            | between Honeycomb's config and operational data.                           |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 2 | Persistence of VxLAN tunnel naming context | HC2VPP-47  | When VPP restarts with Honeycomb running and a VxLan interface configured, |
|   |                                            |            | the interface is sometimes renamed to "vxlan_tunnel0".                     |
|   |                                            |            | It is otherwise configured correctly.                                      |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 3 | Classifier plugin for IPv6 cases           | VPP-687    | Classifier ignores IPv6 packets with less than 8 bytes after last header.  |
|   |                                            |            | Fixed in VPP 17.07.                                                        |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+
| 4 | Batch disable Lisp features                | HC2VPP-131 | When removing complex Lisp configurations in a single request,             |
|   |                                            |            | the operation fails due to a write ordering issue.                         |
+---+--------------------------------------------+------------+----------------------------------------------------------------------------+



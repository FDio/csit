Honeycomb Tests
===============

Overview
--------

Honeycomb tests run on virtual testbeds which are created in VIRL running on a
Cisco UCS C240 servers hosted in Linux Foundation labs. There is currently only
one testbed topology being used for Honeycomb testing - a three node topology
with two links between each pair of nodes as shown in this diagram::

    +--------+                      +--------+
    |        |                      |        |
    |  SUT1  <---------------------->  SUT2  |
    |        <---------------------->        |
    |        |                      |        |
    +---^^---+                      +---^^---+
        ||                              ||
        ||          +--------+          ||
        ||          |        |          ||
        |+---------->   TG   <----------+|
        +----------->        <-----------+
                    |        |
                    +--------+

Virtual testbeds are created dynamically whenever a patch is submitted to gerrit
and destroyed upon completion of all Honeycomb tests. During test execution,
all nodes are reachable through the MGMT network connected to every node via
dedicated NICs and links (not shown above for clarity). Each node is a Virtual
Machine and each connection that is drawn on the diagram is available for use in
any test case.

The following honeycomb test suites are included in the CSIT-17.01 Release and
this report - test areas added since CSIT-16.09 got marked with [&], extended
areas marked with [%]:

* **Basic interface management [%]** - CRUD for interface state,
  ipv4/ipv6 address, ipv4 neighbor, MTU value.
  Test case count: 7
* **L2BD [%]** - CRUD for L2 Bridge-Domain, interface assignment.
  Create up to two bridge domains with all implemented functions turned on.
  (flooding, unknown-unicast flooding, forwarding, learning, arp-termination)
  Assign up to two physical interfaces to a single bridge domain.
  Remove interface assignments, remove bridge domains.
  Test case count: 5
* **L2FIB [%]** - CRD for L2-FIB entries.
  Create 4 FIB entries
  (one of each for filter/forward, static/dynamic combinations).
  Remove FIB entries.
  Test case count: 7
* **VxLAN [%]** - CRD for VxLAN tunnels.
  Create VxLAN interface.
  Disable VxLAN interface.
  Re-create a disabled VxLAN interface.
  Test case count: 6
* **VxLAN-GPE [%]** - CRD for VxLAN GPE tunnels.
  Create VxLAN GPE interface.
  Disable VxLAN interface.
  Re-create a disabled VxLAN interface.
  Test case count: 7
* **Vhost-user [%]** - CRUD for Vhost-user interfaces.
  Create, modify and delete Vhost-user interface, as client and server.
  Test case count: 8
* **TAP** - CRUD for Tap interface management.
  Create, modify and delete TAP interface.
  Test case count: 3
* **VLAN** - CRUD for VLAN sub-interface management.
  Create VLAN sub-interface over a physical interface.
  Toggle interface state separately for super-interface and sub-interface.
  Configure IP address and bridge domain assignment on sub-interface.
  Configure VLAN tag rewrite on sub-interface.
  Test case count: 17
* **ACL [%]** - CRD for low-level classifiers: table and session management,
  interface assignment.
  Configure up to 2 classify tables.
  Configure up to 2 classify sessions on one table.
  Assign classify session to a physical interface.
  Remove tables, sessions, interface assignments.
  Test case count: 9
* **PBB** - CRD for provider backbone bridge sub-interface.
  Configure, modify and remove a PBB sub-interface over a physical interface.
  Test case count: 9
* **NSH_SFC [&]** - CRD for NSH maps and entries, using NSH_SFC plugin.
  Configure up to 2 NSH entries.
  Configure up to 2 NSH maps.
  Modify and delete NSH maps and entries.
  Test case count: 8
* **LISP [&]** - CRD for Lisp: mapping, locator set, adjacency, map resolver.
  Toggle Lisp feature status.
  Configure and delete Lisp mapping as local and remote.
  Configure and delete Lisp adjacency mapping
  Configure and delete Lisp map resolver, proxy ITR.
  Test case count: 11
* **NAT [&]** - CRD for NAT entries, interface assignment.
  Configure and delete up to two NAT entries.
  Assign NAT entries to a physical interface.
  Test case count: 6
* **Port mirroring [&]** - CRD for SPAN port mirroring, interface assignment.
  Configure SPAN port mirroring on a physical interface, mirroring
  up to 2 interfaces.
  Remove SPAN configuration from interfaces.
  Test case count: 3
* **Honeycomb Infractructure** - configuration persistence,
  Netconf notifications for interface events,
  Netconf negative tests aimed at specific issues
Total 111 Honeycomb tests in the CSIT-17.01 Release.

Operational data in Honeycomb should mirror configuration data at all times.
Because of this, test cases follow this general pattern:
1. read operational data of the feature using restconf
2. read status of the feature using VPP API dump
3. modify configuration of the feature using restconf
4. verify changes to operational data using restconf
5. verify changes using VPP API dump

Test cases involving network interfaces utilize the first two physical
interfaces on the first SUT node. The second SUT node is not used
when testing Honeycomb.

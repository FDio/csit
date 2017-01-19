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
    |        |                      |        |
    +---^----+                      +----^---+
        |                                |
        |                                |
        |           +-------+            |
        |           |       |            |
        +----------->   TG  <------------+
                    |       |
                    +-------+

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
* **L2BD [%]** - CRUD for L2 Bridge-Domain, interface assignment.
* **L2FIB [%]** - CRD for L2-FIB entries.
* **VxLAN [%]** - CRD for VxLAN tunnels.
* **VxLAN-GPE [%]** - CRD for VxLAN GPE tunnels.
* **Vhost-user [%]** - CRUD for Vhost-user interfaces.
* **TAP** - CRUD for Tap interface management.
* **VLAN** - CRUD for VLAN sub-interface management.
* **ACL [%]** - CRD for low-level classifiers: table and session management,
  interface assignment.
* **PBB** - CRD for provider backbone bridge sub-interface.
* **VRF [&]** - IP VPN routed-forwarding (IPv4, IPv6).
* **NSH_SFC [&]** - CRD for NSH maps and entries, using NSH_SFC plugin.
* **LISP [&]** - CRD for Lisp: mapping, locator set, adjacency, map resolver.
* **NAT [&]** - CRD for NAT entries, interface assignment.
* **Port mirroring [&]** - CRD for SPAN port mirroring, interface assignment.

Total 121 Honeycomb tests in the CSIT-17.01 Release.


Test Execution Environment
--------------------------

CSIT Honeycomb tests are currently executed in VIRL, as mentioned above. The
physical VIRL testbed infrastructure consists of three identical VIRL hosts,
each host being a Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @
2.30GHz, 18c, 512GB RAM) running Ubuntu 14.04.3 and the following VIRL software
versions:

  STD server version 0.10.24.7
  UWM server version 0.10.24.7

Whenever a patch is submitted to gerrit for review, one of the three VIRL hosts
is selected randomly, and a three-node (TG+SUT1+SUT2), "double-ring" topology is
created as a VIRL simulation on the selected host. The binary Debian Honeycomb
package built by Jenkins for the patch under review and binary Debian VPP
packages from the Nexus repository are then installed on the two SUTs.

Current Honeycomb 17.01 tests have been executed on a single VM operating system
and version only, as described in the following paragraph.

In order to enable future testing with different Operating Systems, or with
different versions of the same Operating System, and simultaneously allowing
others to reproduce tests in the exact same environment, CSIT has established a
process where a candidate Operating System (currently only Ubuntu 14.04.4 LTS)
plus all required packages are installed, and the versions of all installed
packages are recorded. A separate tool then creates, and will continue to create
at any point in the future, a disk image with these packages and their exact
versions. Identical sets of disk images are created in QEMU/QCOW2 format for use
within VIRL, and in VirtualBox format for use in the CSIT Vagrant environment.

A replica of this VM image can be built by running the "build.sh" script in CSIT
repository resources/tools/disk-image-builder/

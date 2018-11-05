Overview
========

Virtual Topologies
------------------

CSIT HoneyComb functional tests are executed in VM-based virtual topologies
created on demand using :abbr:`VIRL (Virtual Internet Routing Lab)`
simulation platform contributed by Cisco. VIRL runs on physical
baremetal servers hosted by LF FD.io project.

All tests are executed in two-node virtual test topology shown in the
figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_functional_tests/}}
                \includegraphics[width=0.90\textwidth]{virtual-2n-nic2nic}
                \label{fig:virtual-2n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_functional_tests/virtual-2n-nic2nic.svg
        :alt: virtual-2n-nic2nic
        :align: center

SUT (System Under Test) is a VM running Ubuntu Linux (or Centos,
depending on the test suite), TG (Traffic Generator) is another VM
running Ubuntu Linux. SUT VMs run HoneyComb management agent and VPP in
Linux user-mode as a combined DUT (Device Under Test). TG runs Scapy
application as a packet Traffic Generator. Virtual connectivity between
SUT and TG is provided using virtual NICs using VMs' virtio drivers.

Functional Tests Coverage
-------------------------

|csit-release| includes following HoneyComb functionality tested in
virtual VM environment:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| ACL                   | - CRD for low-level classifiers: table and   |
|                       |   session management, interface assignment.  |
|                       | - Configure up to 2 classify tables.         |
|                       | - Configure up to 2 classify sessions on one |
|                       |   table.                                     |
|                       | - Assign classify session to a physical      |
|                       |   interface.                                 |
|                       | - Remove tables, sessions, interface         |
|                       |   assignments.                               |
|                       | - Test case count: 9.                        |
+-----------------------+----------------------------------------------+
| ACL-PLUGIN            | - CRD for high-level classifier.             |
|                       | - MAC + IP address classification.           |
|                       | - IPv4, IPv6 address classification.         |
|                       | - TCP, UDP, ICMP, ICMPv6 protocol and        |
|                       |   next-header classification.                |
|                       | - port number classification.                |
|                       | - ICMP, ICMPv6 code and type classification. |
|                       | - Test case count: 15.                       |
+-----------------------+----------------------------------------------+
| Basic interface       | - CRUD for interface state.                  |
| management            | - ipv4/ipv6 address, ipv4 neighbor, MTU      |
|                       |   value.                                     |
|                       | - Test case count: 14.                       |
+-----------------------+----------------------------------------------+
| Border Gateway        | - CRUD and functional tests for BGP.         |
| Protocol              | - Configure peers and routes                 |
|                       | - Check interactions with another BGP peer.  |
|                       | - Test case count: 13.                       |
+-----------------------+----------------------------------------------+
| DHCP Relay            | - CRD for DHCP relay feature.                |
|                       | - Configure DHCP Relays.                     |
|                       | - IPv4 and IPv6 variants.                    |
|                       | - Test case count: 4.                        |
+-----------------------+----------------------------------------------+
| Honeycomb             | - Configuration persistence.                 |
| Infractructure        | - Netconf notifications for interface        |
|                       |   events.                                    |
|                       | - Netconf negative tests aimed at specific   |
|                       |   issues.                                    |
|                       | - Netconf/Restconf northbound over IPv6.     |
|                       | - Test case count: 14.                       |
+-----------------------+----------------------------------------------+
| L2BD                  | - CRUD for L2 Bridge-Domain, interface       |
|                       |   assignment.                                |
|                       | - Create up to two bridge domains with all   |
|                       |   implemented functions turned on:           |
|                       |   flooding, unknown-unicast flooding,        |
|                       |   forwarding, learning, arp-termination.     |
|                       | - Assign up to two physical interfaces to a  |
|                       |   single bridge domain.                      |
|                       | - Remove interface assignments, remove       |
|                       |   bridge domains.                            |
|                       | - Test case count: 5.                        |
+-----------------------+----------------------------------------------+
| L2FIB                 | - CRD for L2-FIB entries.                    |
|                       | - Create 4 FIB entries:                      |
|                       |   one of each for filter/forward,            |
|                       |   static/dynamic combinations.               |
|                       | - Remove FIB entries.                        |
|                       | - Test case count: 7.                        |
+-----------------------+----------------------------------------------+
| LISP                  | - CRD for Lisp: mapping, locator set,        |
|                       |   adjacency, mapresolver.                    |
|                       | - Toggle Lisp feature status.                |
|                       | - Configure and delete Lisp mapping as local |
|                       |   and remote.                                |
|                       | - Configure and delete Lisp adjacency        |
|                       |   mapping.                                   |
|                       | - Configure and delete Lisp map resolver,    |
|                       |   proxy ITR.                                 |
|                       | - Test case count: 18.                       |
+-----------------------+----------------------------------------------+
| LISP GPE              | - CRUD for LISP GPE mappings.                |
|                       | - Toggle Lisp GPE feature status.            |
|                       | - Configure Lisp GPE mappings.               |
|                       | - Traffic test verifying encapsulation.      |
|                       | - Test case count: 12.                       |
+-----------------------+----------------------------------------------+
| NAT                   | - CRD for NAT entries, interface assignment. |
|                       | - Configure and delete up to two NAT         |
|                       |   entries.                                   |
|                       | - Assign NAT entries to a physical           |
|                       |   interface.                                 |
|                       | - Test case count: 6.                        |
+-----------------------+----------------------------------------------+
| NSH_SFC (excluded)    | - CRD for NSH maps and entries, using        |
|                       |   NSH_SFC plugin.                            |
|                       | - Configure up to 2 NSH entries.             |
|                       | - Configure up to 2 NSH maps.                |
|                       | - Modify and delete NSH maps and entries.    |
|                       | - Test case count: 8.                        |
+-----------------------+----------------------------------------------+
| PBB                   | - CRD for provider backbone bridge           |
|                       |   sub-interface.                             |
|                       | - Configure, modify and remove a PBB         |
|                       |   sub-interface over a physical interface.   |
|                       | - Test case count: 8.                        |
+-----------------------+----------------------------------------------+
| Policer               | - CRD for traffic policing feature.          |
|                       | - Configure Policing rules.                  |
|                       | - Assign to interface.                       |
|                       | - Test case count: 6.                        |
+-----------------------+----------------------------------------------+
| Port mirroring        | - CRD for SPAN port mirroring, interface     |
|                       |   assignment.                                |
|                       | - Configure SPAN port mirroring on a         |
|                       |   physical interface, mirroring.             |
|                       | - up to 2 interfaces.                        |
|                       | - Remove SPAN configuration from interfaces. |
|                       | - Test case count: 14.                       |
+-----------------------+----------------------------------------------+
| ProxyARP              | - CRD for proxyARP feature.                  |
|                       | - Configure proxyARP.                        |
|                       | - Assign to interface.                       |
|                       | - Test case count: 3.                        |
+-----------------------+----------------------------------------------+
| ProxyND6              | - CRD for Neighbor Discovery Proxy.          |
|                       | - Configure ProxyND6 feature on interface.   |
|                       | - Test case count: 4.                        |
+-----------------------+----------------------------------------------+
| Routing               | - CRD for routing.                           |
|                       | - Configure single-hop route.                |
|                       | - Configure multi-hop routes.                |
|                       | - Configure blackhole route.                 |
|                       | - IPv4 and IPv6 variants.                    |
|                       | - Test case count: 6.                        |
+-----------------------+----------------------------------------------+
| SLAAC                 | - CRD for Stateless Address                  |
|                       |   AutoConfiguration.                         |
|                       | - Configure SLAAC feature on interfaces.     |
|                       | - Test case count: 7.                        |
+-----------------------+----------------------------------------------+
| Vhost-user            | - CRUD for Vhost-user interfaces.            |
|                       | - Create, modify and delete Vhost-user       |
|                       |   interface, as client and server.           |
|                       | - Test case count: 8.                        |
+-----------------------+----------------------------------------------+
| VLAN                  | - CRUD for VLAN sub-interface management.    |
|                       | - Create VLAN sub-interface over a physical  |
|                       |   interface.                                 |
|                       | - Toggle interface state separately for      |
|                       |   super-interface and sub-interface.         |
|                       | - Configure IP address and bridge domain     |
|                       |   assignment on sub-interface.               |
|                       | - Configure VLAN tag rewrite on              |
|                       |   sub-interface.                             |
|                       | - Test case count: 24.                       |
+-----------------------+----------------------------------------------+
| VxLAN                 | - CRD for VxLAN tunnels.                     |
|                       | - Create VxLAN interface.                    |
|                       | - Disable VxLAN interface.                   |
|                       | - Re-create a disabled VxLAN interface.      |
|                       | - Test case count: 6.                        |
+-----------------------+----------------------------------------------+
| VxLAN-GPE             | - CRD for VxLAN GPE tunnels.                 |
|                       | - Create VxLAN GPE interface.                |
|                       | - Disable VxLAN interface.                   |
|                       | - Re-create a disabled VxLAN interface.      |
|                       | - Test case count: 7.                        |
+-----------------------+----------------------------------------------+
| TAP                   | - CRUD for Tap interface management.         |
|                       | - Create, modify and delete TAP interface.   |
|                       | - Test case count: 3.                        |
+-----------------------+----------------------------------------------+

Total 213 Honeycomb functional tests in the |csit-release|.

Operational data in Honeycomb should mirror configuration data at all
times. Because of this, test cases follow this general pattern:

#. read operational data of the feature using restconf.
#. read status of the feature using VPP API dump.
#. modify configuration of the feature using restconf.
#. verify changes to operational data using restconf.
#. verify changes using VPP API dump, OR
#. send a packet to VPP node and observe behaviour to verify configuration.

Test cases involving network interfaces utilize the first two interfaces
on the DUT node.

Functional Tests Naming
-----------------------

|csit-release| follows a common structured naming convention for all
performance and system functional tests, introduced in CSIT-17.01.

The naming should be intuitive for majority of the tests. Complete
description of CSIT test naming convention is provided on
:ref:`csit_test_naming`.

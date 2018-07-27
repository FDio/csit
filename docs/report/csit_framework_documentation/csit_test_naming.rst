.. _csit_test_naming:

Test Naming
===========

Background
----------

CSIT-|release| follows a common structured naming convention for all
performance and system functional tests, introduced in CSIT-1701.

The naming should be intuitive for majority of the tests. Complete
description of CSIT test naming convention is provided on
`CSIT test naming wiki page <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.
Below few illustrative examples of the naming usage for test suites across CSIT
performance, functional and Honeycomb management test areas.

Naming Convention
-----------------

The CSIT approach is to use tree naming convention and to encode following
testing information into test suite and test case names:

#. packet network port configuration

   * port type, physical or virtual;
   * number of ports;
   * NIC model, if applicable;
   * port-NIC locality, if applicable;

#. packet encapsulations;

#. VPP packet processing

   * packet forwarding mode;
   * packet processing function(s);

#. packet forwarding path

   * if present, network functions (processes, containers, VMs) and their
     topology within the computer;

#. main measured variable, type of test.

Proposed convention is to encode ports and NICs on the left (underlay),
followed by outer-most frame header, then other stacked headers up to the
header processed by vSwitch-VPP, then VPP forwarding function, then encap on
vhost interface, number of vhost interfaces, number of VMs. If chained VMs
present, they get added on the right. Test topology is expected to be
symmetric, in other words packets enter and leave SUT through ports specified
on the left of the test name. Here some examples to illustrate the convention
followed by the complete legend, and tables mapping the new test filenames to
old ones.

Naming Examples
---------------

CSIT test suite naming examples (filename.robot) for common tested VPP
topologies:

1. **Physical port to physical port - a.k.a. NIC-to-NIC, Phy-to-Phy, P2P**

   * *PortNICConfig-WireEncapsulation-PacketForwardingFunction-
     PacketProcessingFunction1-...-PacketProcessingFunctionN-TestType*
   * *10ge2p1x520-dot1q-l2bdbasemaclrn-ndrdisc.robot* => 2 ports of 10GE on Intel
     x520 NIC, dot1q tagged Ethernet, L2 bridge-domain baseline switching with
     MAC learning, NDR throughput discovery.
   * *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrchk.robot* => 2 ports of 10GE on
     Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain baseline switching
     with MAC learning, NDR throughput discovery.
   * *10ge2p1x520-ethip4-ip4base-ndrdisc.robot* => 2 ports of 10GE on Intel x520
     NIC, IPv4 baseline routed forwarding, NDR throughput discovery.
   * *10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot* => 2 ports of 10GE on Intel
     x520 NIC, IPv6 scaled up routed forwarding, NDR throughput discovery.
   * *10ge2p1x520-ethip4-ip4base-iacldstbase-ndrdisc.robot* => 2 ports of 10GE on
     Intel x520 NIC, IPv4 baseline routed forwarding, ingress Access Control
     Lists baseline matching on destination, NDR throughput discovery.
   * *40ge2p1vic1385-ethip4-ip4base-ndrdisc.robot* => 2 ports of 40GE on Cisco
     vic1385 NIC, IPv4 baseline routed forwarding, NDR throughput discovery.
   * *eth2p-ethip4-ip4base-func.robot* => 2 ports of Ethernet, IPv4 baseline
     routed forwarding, functional tests.

2. **Physical port to VM (or VM chain) to physical port - a.k.a. NIC2VM2NIC,
   P2V2P, NIC2VMchain2NIC, P2V2V2P**

   * *PortNICConfig-WireEncapsulation-PacketForwardingFunction-
     PacketProcessingFunction1-...-PacketProcessingFunctionN-VirtEncapsulation-
     VirtPortConfig-VMconfig-TestType*
   * *10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot* => 2 ports
     of 10GE on Intel x520 NIC, dot1q tagged Ethernet, L2 bridge-domain switching
     to/from two vhost interfaces and one VM, NDR throughput discovery.
   * *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot* => 2
     ports of 10GE on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain
     switching to/from two vhost interfaces and one VM, NDR throughput discovery.
   * *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc.robot* => 2
     ports of 10GE on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain
     switching to/from four vhost interfaces and two VMs, NDR throughput
     discovery.
   * *eth2p-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-func.robot* => 2 ports of
     Ethernet, IPv4 VXLAN Ethernet, L2 bridge-domain switching to/from two vhost
     interfaces and one VM, functional tests.

3. **API CRUD tests - Create (Write), Read (Retrieve), Update (Modify), Delete
   (Destroy) operations for configuration and operational data**

   * *ManagementTestKeyword-ManagementOperation-ManagedFunction1-...-
     ManagedFunctionN-ManagementAPI1-ManagementAPIN-TestType*
   * *mgmt-cfg-lisp-apivat-func* => configuration of LISP with VAT API calls,
     functional tests.
   * *mgmt-cfg-l2bd-apihc-apivat-func* => configuration of L2 Bridge-Domain with
     Honeycomb API and VAT API calls, functional tests.
   * *mgmt-oper-int-apihcnc-func* => reading status and operational data of
     interface with Honeycomb NetConf API calls, functional tests.
   * *mgmt-cfg-int-tap-apihcnc-func* => configuration of tap interfaces with
     Honeycomb NetConf API calls, functional tests.
   * *mgmt-notif-int-subint-apihcnc-func* => notifications of interface and
     sub-interface events with Honeycomb NetConf Notifications, functional tests.

For complete description of CSIT test naming convention please refer to `CSIT
test naming wiki page <https://wiki.fd.io/view/CSIT/csit-test-naming>`_.

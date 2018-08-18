Overview
========

Virtual Topologies
------------------

CSIT VPP functional tests are executed in VM-based virtual topologies
created on demand using :abbr:`VIRL (Virtual Internet Routing Lab)`
simulation platform contributed by Cisco. VIRL runs on physical
baremetal servers hosted by LF FD.io project. Based on the packet path
thru SUT VMs, two distinct logical topology types are used for VPP DUT
data plane testing:

#. vNIC-to-vNIC switching topologies.
#. Nested-VM service switching topologies.

vNIC-to-vNIC Switching
~~~~~~~~~~~~~~~~~~~~~~

The simplest virtual topology for software data plane application like
VPP is vNIC-to-vNIC switching. Tested virtual topologies for 2-Node and
3-Node testbeds are shown in figures below.

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


.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_functional_tests/}}
                \includegraphics[width=0.90\textwidth]{virtual-3n-nic2nic}
                \label{fig:virtual-3n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_functional_tests/virtual-3n-nic2nic.svg
        :alt: virtual-3n-nic2nic
        :align: center

SUT1 and SUT2 are two VMs (running Ubuntu or Centos, depending on the test
suite), TG is a Traffic Generator (running Ubuntu VM). SUTs run VPP
SW application in Linux user-mode as a Device Under Test (DUT) within
the VM. TG runs Scapy SW application as a packet Traffic Generator.
Network connectivity between SUTs and to TG is provided using virtual
NICs and VMs' virtio drivers.

Virtual testbeds are created on-demand whenever a verification job is
started (e.g. triggered by the gerrit patch submission) and destroyed
upon completion of all functional tests. Each node is a Virtual Machine
and each connection that is drawn on the diagram is available for use in
any test case. During the test execution, all nodes are reachable thru
the Management network connected to every node via dedicated virtual
NICs and virtual links (not shown above for clarity).

Nested-VM Service Switching
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nested-VM (Virtual Machine) service switching topology test cases
require VPP DUT to communicate with nested-VM(s) over vhost-user virtual
interfaces. Nested-VM(s) is(are) created on SUT1 and/or SUT2 for the
duration of these particular test cases only. Virtual test topology with
nested-VM(s) is shown in the figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_functional_tests/}}
                \includegraphics[width=0.90\textwidth]{virtual-3n-vm-vhost}
                \label{fig:virtual-3n-vm-vhost}
        \end{figure}

.. only:: html

    .. figure:: ../vpp_functional_tests/virtual-3n-vm-vhost.svg
        :alt: virtual-3n-vm-vhost
        :align: center

Functional Tests Coverage
-------------------------

|csit-release| includes following VPP functionality tested in virtual VM
environment:

+-----------------------+----------------------------------------------+
| Functionality         |  Description                                 |
+=======================+==============================================+
| ACL                   | Ingress Access Control List security for L2  |
|                       | Bridge-Domain MAC switching, IPv4 routing,   |
|                       | IPv6 routing.                                |
+-----------------------+----------------------------------------------+
| COP                   | COP address white-list and black-list        |
|                       | filtering for IPv4 and IPv6 routing.         |
+-----------------------+----------------------------------------------+
| DHCP                  | Dynamic Host Control Protocol Client and     |
|                       | Proxy for IPv4 and IPv6 routing.             |
+-----------------------+----------------------------------------------+
| GRE                   | Generic Routing Encapsulation Overlay        |
|                       | Tunnels for IPv4.                            |
+-----------------------+----------------------------------------------+
| IPSec                 | IPSec tunnel and transport modes.            |
+-----------------------+----------------------------------------------+
| IPv4                  | IPv4 routing, RPF, ARP, Proxy ARP, ICMPv4.   |
+-----------------------+----------------------------------------------+
| IPv6                  | IPv6 routing, NS/ND, RA, ICMPv6.             |
+-----------------------+----------------------------------------------+
| L2BD                  | L2 Bridge-Domain switching for untagged      |
|                       | Ethernet, dot1q and dot1ad tagged.           |
+-----------------------+----------------------------------------------+
| L2XC                  | L2 Cross-Connect switching for untagged      |
|                       | Ethernet, dot1q and dot1ad tagged.           |
+-----------------------+----------------------------------------------+
| LISP                  | Locator/ID Separation Protocol overlay       |
|                       | tunnels and locator/id mapping control.      |
+-----------------------+----------------------------------------------+
| QoS Policer Metering  | Ingress packet rate metering and marking for |
|                       | IPv4, IPv6.                                  |
+-----------------------+----------------------------------------------+
| Softwire Tunnels      | IPv4-in-IPv6 softwire tunnels.               |
+-----------------------+----------------------------------------------+
| Tap Interface         | Baseline Linux tap interface tests.          |
+-----------------------+----------------------------------------------+
| IPFIX and SPAN        | Telemetry IPFIX netflow statistics and SPAN  |
|                       | port mirroring.                              |
+-----------------------+----------------------------------------------+
| uRPF Source Security  | Unicast Reverse Path Forwarding security for |
|                       | IPv4 and IPv6 routing.                       |
+-----------------------+----------------------------------------------+
| VLAN Tag Translation  | L2 VLAN tag translation 2to2, 2to1, 1to2,    |
|                       | 1to1.                                        |
+-----------------------+----------------------------------------------+
| VRF Routing           | Multi-context VRF IPVPN routing for IPv4 and |
|                       | IPv6.                                        |
+-----------------------+----------------------------------------------+
| VXLAN                 | VXLAN overlay tunneling for L2-over-IPv4 and |
|                       | -over-IPv6.                                  |
+-----------------------+----------------------------------------------+

Functional Tests Naming
-----------------------

|csit-release| follows a common structured naming convention for all
performance and system functional tests, introduced in CSIT-17.01.

The naming should be intuitive for majority of the tests. Complete
description of CSIT test naming convention is provided on
:ref:`csit_test_naming`.
